import asyncio
import os

from proto.config_pb2 import ChatGTProvider

from EdgeGPT import Chatbot as microsoft_chatgpt
from revChatGPT.V1 import Chatbot as ponyai_chatgpt


class OpenAiChatGPT:

    def __init__(self, config):
        self._config = {
            "email": config.account_info.user_name,
            "password": config.account_info.password,
            "proxy": config.proxy,
        }
        self._openai_chatgpt = ponyai_chatgpt(config=self._config)

    def capture_answer(self, prompt):
        prev_message = ''
        answer_contents = ''
        for data in self._openai_chatgpt.ask(prompt):
            answer_contents += data['message'][len(prev_message):]
            prev_message = data['message']
        return answer_contents


class MicroSoftChatGPT:

    def __init__(self, config):
        os.environ['COOKIE_FILE'] = config.cookie_path
        self._contents = ''

    def capture_answer(self, prompt):
        asyncio.run(self._ask_answer(prompt))
        return self._contents

    async def _ask_answer(self, prompt):
        self._microsoft_chatgpt = microsoft_chatgpt()
        self._contents = (await self._microsoft_chatgpt.ask(
            prompt=prompt))["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"]
        await self._microsoft_chatgpt.close()


_PROVIDER_TO_CHATGPT = {
    ChatGTProvider.OPENAI: OpenAiChatGPT,
    ChatGTProvider.MICROSOFT: MicroSoftChatGPT,
}


def chatgpt_factory(config):
    return _PROVIDER_TO_CHATGPT[config.provider](config)
