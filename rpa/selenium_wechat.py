from collections import deque, namedtuple

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

WECHAT_WEB_URL = 'http://wx.qq.com/'
XpathArgs = namedtuple('XpathArgs', ['by', 'value'])

TRACKED_CHAT_CONTACT_NUM = 8
CHATROOM_MESSAGE_DEQUE_LENGTH = 10


class SeleniumWechatBot:

    def __init__(self, chrome_exe_path, chatgpts):
        self._chrome_exe_path = chrome_exe_path
        self._chatgpts = chatgpts
        self._prompts = {}
        self._contents = {}
        self._browser = webdriver.Chrome(executable_path=chrome_exe_path)

    def login(self):
        self._browser.set_page_load_timeout(10)
        try:
            self._browser.get(WECHAT_WEB_URL)
        except exceptions.TimeoutException:
            pass

        qrcode_element = self._browser.find_element(by=By.XPATH, value='//img[@class="img"]')
        qrcode_url = qrcode_element.get_attribute('src')
        print(f'You could open this link to login as well, {qrcode_url}')

        # wait for successfully login
        WebDriverWait(self._browser, 120).until(
            EC.element_to_be_clickable((By.XPATH, '//span[@ng-bind-html="account.NickName"]')))

        # assume login and switch to chat page
        self._browser.switch_to.window(self._browser.window_handles[-1])

    def get_contacts(self):
        # some how, it can't catch some of chat items
        xpath_args = XpathArgs(
            by=By.XPATH,
            value='(//div[contains(@class,"chat_item slide-left")])',
        )
        WebDriverWait(self._browser,
                      10.0).until(EC.element_to_be_clickable((xpath_args.by, xpath_args.value)))
        return self._browser.find_elements(*xpath_args)

    def get_nickname(self, contact):
        return contact.find_element(by=By.CLASS_NAME, value='nickname').text

    def switch_chatroom(self, contact):
        contact.click()

    def get_chatroom_contents(self):
        return self._browser.find_elements(by=By.XPATH, value='//div[@class="plain"]')

    def get_notice_count(self, contact):
        try:
            contact.find_element(by=By.XPATH,
                                 value='//i[contains(@class,"icon web_wechat_reddot")]')
            return True
        except:
            return False

    def send_message(self, message):
        '''fillin message and click send button'''
        edit_element = self._browser.find_element(by=By.ID, value='editArea')
        button_element = self._browser.find_element(by=By.XPATH, value="//A[@class='btn btn_send']")

        for _ in range(10):
            edit_element.send_keys(message)
            edit_element = self._browser.find_element(by=By.ID, value='editArea')
            if edit_element.text:
                button_element.click()
                return

    def get_trigger_keywords(self):
        return self._chatgpts.keys()

    def select_chatgpt(self, content):
        for key, chatgpt in self._chatgpts.items():
            if key in content:
                return key, chatgpt
        return None, None

    def check_keywords(self, content):
        for key in self._chatgpts.keys():
            if content.startswith(key):
                return True
        return False

    def one_interation(self):
        # 1. get chat items
        # 2. iterate each chatroom check lastest 10 pieces message, whether contains keywords
        # 3. select chatgpt according to keyword
        # 4. submit question and wait for answer
        # 5. send answer out
        contacts = self.get_contacts()
        for index in range(TRACKED_CHAT_CONTACT_NUM):
            contact = contacts[index]
            prompt_list = []
            nickname = self.get_nickname(contact)

            if nickname not in self._contents.keys():
                self._contents[nickname] = deque('', CHATROOM_MESSAGE_DEQUE_LENGTH)
            # once user in specific chatroom, it won't have notice red dot
            # notice_count = self.get_notice_count(contact)
            # if not notice_count:
            #     continue
            self.switch_chatroom(contact)
            chat_contents = self.get_chatroom_contents()
            # only check the lastest 10 message and abandon others
            # collect prompt first and them trigger chatgpt
            for chat_content in chat_contents[-CHATROOM_MESSAGE_DEQUE_LENGTH:]:
                content = chat_content.text
                if content in self._contents[nickname]:
                    continue
                self._contents[nickname].append(content)
                print(f'{nickname}: {content}')
                if not self.check_keywords(content):
                    continue
                keyword, chatgpt = self.select_chatgpt(content)
                if not keyword:
                    continue
                prompt = content.replace(keyword, '')
                key = f'{keyword}{prompt}'
                prompt_list.append((prompt, key))

            for prompt_info, key_info in prompt_list:
                if key_info in self._prompts.keys():
                    continue
                answer = chatgpt.capture_answer(prompt_info)
                print(f'{key_info}, {answer}')
                self._prompts[key_info] = True
                if not answer:
                    continue
                self.send_message(answer)

    def refresh(self):
        self._browser.refresh()
