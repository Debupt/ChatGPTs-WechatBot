from chatgpt.chatgpt import chatgpt_factory
from proto.config_pb2 import WechatConfig
from rpa.selenium_wechat import SeleniumWechatBot
from utils.file_utils import read_proto

import click
import time

CONFIG_FILE = 'config/config'
CHROME_DRIVER = 'bazel-ChatGPTs-WechatBot/external/chrome_driver/chromedriver'


@click.group()
def main():
    pass


def _parse_config(config_file):
    config_content = read_proto(config_file, WechatConfig)
    keyword_to_bot = {}
    for bot_config in config_content.bot_config:
        keyword_to_bot[bot_config.trigger_keyword] = bot_config.chatgpt_config

    return keyword_to_bot


def _chatgpt_get_answer(bot_config, prompt):
    chatgpt_inst = chatgpt_factory(bot_config)
    return chatgpt_inst.capture_answer(prompt)


def _get_chatgpts(config):
    keyword_to_chatgpt = {}
    for keyword, bot_config in config.items():
        keyword_to_chatgpt[keyword] = chatgpt_factory(bot_config)
    return keyword_to_chatgpt


@main.command()
@click.option('--prompt', default='hello world')
def chatgpt_test(prompt):
    config = _parse_config(CONFIG_FILE)
    for keyword, bot_config in config.items():
        answer = _chatgpt_get_answer(bot_config, prompt)
        print(f'[{keyword}]: {answer}')


@main.command()
def run():
    config = _parse_config(CONFIG_FILE)

    chatgpts = _get_chatgpts(config)
    selenium_bot = SeleniumWechatBot(CHROME_DRIVER, chatgpts)
    selenium_bot.login()
    while True:
        try:
            selenium_bot.one_interation()
        except Exception as e:
            pass
        time.sleep(1)


if __name__ == "__main__":
    main()
