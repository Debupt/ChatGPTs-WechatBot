from collections import deque
from concurrent.futures import ThreadPoolExecutor
import logging
from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Playwright, Browser, Page, Locator, BrowserContext
import tempfile
from PIL import Image
import time
from utils.utils import print_qr_code
from datetime import datetime

WECHAT_WEB_URL = 'http://wx.qq.com/'
TRACK_CHATROOM_NUMS = 8
CHECK_MESSAGE_LINES = 15

chatroom_tread_pool = ThreadPoolExecutor(max_workers=TRACK_CHATROOM_NUMS)


class PlayWrightWeChat:

    def __init__(self, chatgpt_factory):
        self.playwright: Playwright
        self.browser: Browser
        self.page: Page
        self.context: BrowserContext
        self._chatroom_info = {}
        self._chatgpt_factory = chatgpt_factory
        self._storage_state = tempfile.NamedTemporaryFile(suffix='.json')

    def playwright_setup(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def reload_page(self, website=WECHAT_WEB_URL):
        new_page = self.browser.new_page(storage_state=self._storage_state.name)
        new_page.goto(website, wait_until='commit')
        self.context.close()
        self.page.close()
        self.page = new_page

    def login(self, website=WECHAT_WEB_URL):
        self.page.goto(website, wait_until='commit')

        # wait for while until qr code load successful
        time.sleep(5)

        qrcode_element = self.page.locator('//div[@class="qrcode"]/img[contains(@class, "img")]')
        with tempfile.NamedTemporaryFile(suffix='.png') as temp_file:
            qrcode_element.click()
            qrcode_element.screenshot(path=temp_file.name)
            with Image.open(temp_file.name) as qrcode_image:
                print_qr_code(qrcode_image)

        self.page.wait_for_selector('//span[@ng-bind-html="account.NickName"]', timeout=120 * 1000)

        nickname = self.page.locator('//span[@ng-bind-html="account.NickName"]').inner_html()
        logging.info(f'{nickname} login successfully.')

        self.page.context.storage_state(path=self._storage_state.name)

    def one_iteration(self):
        chatroom_sessions = self.get_chatroom_sessions()
        sessions_count = chatroom_sessions.count()
        track_chatroom_nums = TRACK_CHATROOM_NUMS if sessions_count > TRACK_CHATROOM_NUMS else sessions_count
        for index in range(track_chatroom_nums):
            chatroom_session = chatroom_sessions.nth(index)
            self.handle_chatroom_session(chatroom_session)

    def send_chatgpt_reply(self, nickname):
        for chatgpt_instance in self._chatgpt_factory.chatgpt_instances.values():
            if nickname not in chatgpt_instance.replies_queue.keys():
                continue
            while not chatgpt_instance.replies_queue[nickname].empty():
                answer = chatgpt_instance.replies_queue[nickname].get()
                chatgpt_instance.replies_queue[nickname].task_done()
                self._chatroom_info[nickname].append(answer)
                self.send_message(answer)

    def handle_chatroom_messages(self, messages, nickname):
        for message in messages:
            keyword, chatgpt_instance = self._chatgpt_factory.select_chatgpt(message)
            if not keyword:
                continue
            prompt = message.replace(keyword, '')
            chatgpt_instance.prompts_queue.put((nickname, prompt))

    def handle_chatroom_session(self, chatroom_session):
        nickname = self.get_nickname(chatroom_session)
        if nickname not in self._chatroom_info.keys():
            self._chatroom_info[nickname] = deque('', 5 * TRACK_CHATROOM_NUMS)
        self.swich_chatroom(chatroom_session)
        self.send_chatgpt_reply(nickname)

        need_handle_messages = []
        chatroom_messages = self.get_chatroom_messages()
        if not chatroom_messages:
            return
        for message in chatroom_messages:
            if message in self._chatroom_info[nickname]:
                continue
            need_handle_messages.append(message)
        if not need_handle_messages:
            return
        logging.info(f'{need_handle_messages}')
        self._chatroom_info[nickname].extend(need_handle_messages)
        chatroom_tread_pool.submit(self.handle_chatroom_messages, need_handle_messages, nickname)

    def get_chatroom_sessions(self):
        self.page.wait_for_selector(
            '//div[@ng-repeat="chatContact in chatList track by chatContact.UserName"]',
            timeout=120 * 1000)
        return self.page.locator(
            '//div[@ng-repeat="chatContact in chatList track by chatContact.UserName"]')

    def get_nickname(self, chatroom_session: Locator):
        return chatroom_session.locator('.nickname').inner_text()

    def swich_chatroom(self, chatroom_session: Locator):
        chatroom_session.click()

    def get_chatroom_messages(self):
        return self.page.locator('//div[@class="content"]').all_inner_texts()

    def send_message(self, message):
        self.page.locator('//pre[@id="editArea"]').fill(message)
        self.page.locator('//A[@class="btn btn_send"]').click()

    def feed_dog(self, username):
        chatroom_sessions = self.get_chatroom_sessions()
        for index in range(chatroom_sessions.count()):
            chatroom_session = chatroom_sessions.nth(index)
            nickname = self.get_nickname(chatroom_session)
            if nickname == username:
                self.swich_chatroom(chatroom_session)
                self.send_message(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
