import datetime
import logging

from chatgpt.chatgpt import chatgpt_factory, ChatgptFactory
from proto.config_pb2 import WechatConfig
from rpa.selenium_wechat import SeleniumWechatBot
from rpa.playwright_wechat import PlayWrightWeChat
from utils.file_utils import read_proto

import click
import time

CONFIG_FILE = 'config/config'
CHROME_DRIVER = 'bazel-ChatGPTs-WechatBot/external/firefox_driver/geckodriver'

FEED_DOG_USER = 'File Transfer'
FEED_DOG_INTERVAL_IN_SEC = 2 * 60 * 60


@click.group()
def main():
    pass


def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger_format = logging.Formatter(
        '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]: %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logger_format)
    logger.addHandler(stream_handler)


def _parse_config(config_file):
    config_content = read_proto(config_file, WechatConfig)
    keyword_to_bot = {}
    for bot_config in config_content.bot_config:
        keyword_to_bot[bot_config.trigger_keyword] = bot_config.chatgpt_config

    return keyword_to_bot


def _chatgpt_get_answer(bot_config, prompt):
    chatgpt_inst = chatgpt_factory(bot_config)
    return chatgpt_inst.capture_answer(prompt)


@main.command()
@click.option('--prompt', default='hello world')
def chatgpt_test(prompt):
    config = _parse_config(CONFIG_FILE)
    for keyword, bot_config in config.items():
        answer = _chatgpt_get_answer(bot_config, prompt)
        print(f'[{keyword}]: {answer}')


@main.command()
def run():
    config = read_proto(CONFIG_FILE, WechatConfig)

    chatgpts = ChatgptFactory(config)
    selenium_wechat_bot = SeleniumWechatBot(CHROME_DRIVER, chatgpts)
    selenium_wechat_bot.login()
    while True:
        try:
            selenium_wechat_bot.one_iteration()
        except Exception as e:
            logging.warning(e)
            pass
        selenium_wechat_bot.browser.implicitly_wait(2)


@main.command()
def run_v2():
    config = read_proto(CONFIG_FILE, WechatConfig)

    chatgpts = ChatgptFactory(config)
    playwright_wechat_bot = PlayWrightWeChat(chatgpts)
    playwright_wechat_bot.playwright_setup()
    playwright_wechat_bot.login()

    start_time = datetime.datetime.now()
    while True:
        try:
            playwright_wechat_bot.one_iteration()
            if datetime.datetime.now() - start_time > datetime.timedelta(
                    seconds=FEED_DOG_INTERVAL_IN_SEC):
                start_time = datetime.datetime.now()
                playwright_wechat_bot.reload_page()
                playwright_wechat_bot.feed_dog(FEED_DOG_USER)
            time.sleep(1)
        except Exception as err:
            logging.error(err)


if __name__ == "__main__":
    setup_logger()
    main()
