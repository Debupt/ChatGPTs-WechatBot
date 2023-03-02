from collections import deque
from concurrent.futures import ThreadPoolExecutor
import logging
from PIL import Image
import tempfile
from typing import NamedTuple

from utils.utils import print_qr_code

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

WECHAT_WEB_URL = 'http://wx.qq.com/'
TRACK_CHATROOM_NUMS = 8
CHECK_MESSAGE_LINES = 15

chatroom_thread_pool = ThreadPoolExecutor(max_workers=TRACK_CHATROOM_NUMS)


class XpathArgs(NamedTuple):
    by: By
    value: str


class ChatRoomInfo(NamedTuple):
    nickname: str
    messages: deque
    prompts: list


class SeleniumWechatBot:

    def __init__(self, firefox_exe_path, chatgpt_factory):
        self._chatgpt_factory = chatgpt_factory
        self._chatroom_info = {}

        firefox_options = FirefoxOptions()
        firefox_options.add_argument('--headless')
        firefox_options.add_argument('--disable-gpu')
        self._browser = webdriver.Firefox(executable_path=firefox_exe_path, options=firefox_options)

    @property
    def browser(self):
        return self._browser

    def login(self):
        self._browser.set_page_load_timeout(15)
        try:
            self._browser.get(WECHAT_WEB_URL)
        except exceptions.TimeoutException:
            pass

        qrcode_element = self._browser.find_element(by=By.XPATH, value='//img[@class="img"]')

        # wait util qrcode load successfully
        self.browser.implicitly_wait(20)

        with tempfile.NamedTemporaryFile(suffix='.png') as temp_file:
            qrcode_element.screenshot(temp_file.name)
            with Image.open(temp_file.name) as image:
                print_qr_code(image)

        xpath_args = XpathArgs(by=By.XPATH, value='//span[@ng-bind-html="account.NickName"]')
        # wait for successfully login
        WebDriverWait(self._browser,
                      120).until(EC.element_to_be_clickable((xpath_args.by, xpath_args.value)))

        nickname = self._browser.find_element(*xpath_args)
        logging.info(f'{nickname.text} login WeChat successfully')

        # assume login and switch to chat page
        self._browser.switch_to.window(self._browser.window_handles[-1])

    def _handle_message(self, messages, chatroom_info: ChatRoomInfo):
        for message in messages:
            keyword, chatgpt_instance = self._chatgpt_factory.select_chatgpt(message)
            if not keyword:
                continue
            if message in chatroom_info.prompts:
                continue
            chatroom_info.prompts.append(message)
            prompt = message.replace(keyword, '')
            chatgpt_instance.prompts_queue.put((chatroom_info.nickname, prompt))

    def one_iteration(self):
        chat_sessions = self._get_chatroom_sessions()
        track_chatroom_nums = TRACK_CHATROOM_NUMS if len(
            chat_sessions) > TRACK_CHATROOM_NUMS else len(chat_sessions)

        for index in range(track_chatroom_nums):
            chat_session = chat_sessions[index]
            nickname = self._get_nickname(chat_session)
            if nickname not in self._chatroom_info.keys():
                self._chatroom_info[nickname] = ChatRoomInfo(
                    nickname=nickname,
                    messages=deque('', 5 * CHECK_MESSAGE_LINES),
                    prompts=list(),
                )
            self._switch_chatroom(chat_session)
            chatroom_info = self._chatroom_info[nickname]

            for chatgpt_instance in self._chatgpt_factory.chatgpt_instances.values():
                if nickname not in chatgpt_instance.replies_queue.keys():
                    continue
                while not chatgpt_instance.replies_queue[nickname].empty():
                    answer = chatgpt_instance.replies_queue[nickname].get()
                    chatgpt_instance.replies_queue[nickname].task_done()
                    self._chatroom_info[nickname].messages.append(answer)
                    self._send_message(answer)

            chatroom_contents = self._get_chatroom_contents()
            need_handle_messages = []
            for chatroom_content in chatroom_contents[-CHECK_MESSAGE_LINES:]:
                logging.info(f'{nickname}: {chatroom_content.text}')
                if chatroom_content.text in chatroom_info.messages:
                    continue
                need_handle_messages.append(chatroom_content.text)
            if not need_handle_messages:
                continue
            self._chatroom_info[nickname].messages.extend(need_handle_messages)
            chatroom_thread_pool.submit(self._handle_message, need_handle_messages, chatroom_info)

    def _get_chatroom_sessions(self):
        xpath_args = XpathArgs(
            by=By.XPATH,
            value='(//div[contains(@class,"chat_item slide-left")])',
        )
        WebDriverWait(self._browser,
                      10.0).until(EC.element_to_be_clickable((xpath_args.by, xpath_args.value)))
        return self._browser.find_elements(*xpath_args)

    def _get_nickname(self, chatroom_session):
        xpath_args = XpathArgs(
            by=By.CLASS_NAME,
            value='nickname',
        )
        return chatroom_session.find_element(*xpath_args).text

    def _switch_chatroom(self, chatroom_session):
        chatroom_session.click()

    def _get_chatroom_contents(self):
        xpath_args = XpathArgs(
            by=By.XPATH,
            value='//div[@class="plain"]',
        )
        return self._browser.find_elements(*xpath_args)

    def _send_message(self, messages):
        if not messages:
            return

        edit_xpath_args = XpathArgs(
            by=By.ID,
            value='editArea',
        )
        edit_element = self._browser.find_element(*edit_xpath_args)

        buttom_xpath_args = XpathArgs(
            by=By.XPATH,
            value='//A[@class="btn btn_send"]',
        )
        buttom_element = self._browser.find_element(*buttom_xpath_args)

        edit_element.send_keys(messages)
        edit_element = self._browser.find_element(*edit_xpath_args)
        if edit_element.text:
            buttom_element.click()
