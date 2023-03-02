import asyncio
import logging
import os
from queue import Queue

from proto.config_pb2 import ChatGTProvider

from EdgeGPT import Chatbot as microsoft_chatgpt
from revChatGPT.V1 import Chatbot as ponyai_chatgpt

from concurrent.futures import ThreadPoolExecutor

chatgpt_thread_pool = ThreadPoolExecutor(max_workers=2)


class ChatGPT:

    def __init__(self):
        self._answer = ''
        self.prompts_queue = Queue()
        self.replies_queue = {}

    def run(self):
        while True:
            if self.prompts_queue.empty():
                continue
            nickname, prompt = self.prompts_queue.get()
            self.reply(prompt, nickname)
            logging.info(f'{nickname}: {prompt}, {self._answer}')
            if nickname not in self.replies_queue.keys():
                self.replies_queue[nickname] = Queue()
            self.replies_queue[nickname].put(self._answer)

    def reply(self, prompt, nickname):
        pass


class OpenAiChatGPT(ChatGPT):

    def __init__(self, config):
        super().__init__()
        self._config = {
            "email": config.account_info.user_name,
            "password": config.account_info.password,
            "proxy": config.proxy,
        }
        self._conversation_id = {}
        self._openai_chatgpt = ponyai_chatgpt(config=self._config)

    def reply(self, prompt, nickname):
        conversation_id = None
        prev_message = None
        self._answer = ''
        logging.info(prompt)
        if nickname in self._conversation_id.keys():
            conversation_id = self._conversation_id[nickname]
        if not conversation_id and len(self._conversation_id.keys()) > 1:
            self._openai_chatgpt.reset_chat()
        for data in self._openai_chatgpt.ask(prompt=prompt, conversation_id=conversation_id):
            self._answer += data['message'][len(prev_message):]
            prev_message = data['message']
        if not conversation_id:
            self._conversation_id[nickname] = self._openai_chatgpt.conversation_id


class MicroSoftChatGPT(ChatGPT):

    def __init__(self, config):
        super().__init__()
        os.environ['COOKIE_FILE'] = config.cookie_path

    async def _reply(self, prompt, _):
        self._microsoft_chatgpt = microsoft_chatgpt()
        self._answer = (await self._microsoft_chatgpt.ask(
            prompt=prompt))["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"]
        await self._microsoft_chatgpt.close()

    def reply(self, prompt, _):
        logging.info(prompt)
        asyncio.run(self._reply(prompt, _))


_PROVIDER_TO_CHATGPT = {
    ChatGTProvider.OPENAI: OpenAiChatGPT,
    ChatGTProvider.MICROSOFT: MicroSoftChatGPT,
}


def chatgpt_factory(config):
    return _PROVIDER_TO_CHATGPT[config.provider](config)


class ChatgptFactory:

    def __init__(self, config):
        self._config = config
        self._chatgpt_instances = self._create_chatgpt()
        self._create_reply_thread()

    @property
    def chatgpt_instances(self):
        return self._chatgpt_instances

    def _create_chatgpt(self):
        keyword_to_chatgpt_instance = {}
        for bot_config in self._config.bot_config:
            cahtgpt_config = bot_config.chatgpt_config
            keyword_to_chatgpt_instance[bot_config.trigger_keyword] = chatgpt_factory(
                cahtgpt_config)
        return keyword_to_chatgpt_instance

    def _create_reply_thread(self):
        for chatgpt_instance in self._chatgpt_instances.values():
            chatgpt_thread_pool.submit(chatgpt_instance.run)

    def select_chatgpt(self, content):
        for keyword, chatgpt_instance in self._chatgpt_instances.items():
            if content.startswith(keyword):
                return keyword, chatgpt_instance
        return
