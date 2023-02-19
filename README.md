# ChatGPT-Wechat-Bot

Wechat bot to auto reply with different ChatGPTs

## Installation

run `setup.sh` to install Bazel and Python dependencies

```bash
sudo ./setup.sh
```

## Configuration

update OpenAI/Microsoft ChatGPT config files in `config/config`, each field defination please refer `proto/config.proto`

1. update OPENAI ChatGPT account and network proxy information

```bash
# config/config
bot_config {
    name: "openai"
    chatgpt_config {
        provider: OPENAI
        account_info {
            user_name: "your input"
            password: "your input"
        }
        proxy: "your input"
    }
    trigger_keyword: "your input"
}
```

2. update Microsoft Bing ChatGPT account cookies, could use `Cookie-Editor`(https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm?hl=en) to save, and override `config/cookies.json` file

```bash
# config/config
bot_config {
    name: "microsoft"
    chatgpt_config {
        provider: MICROSOFT
        # fillin contents with your own cookies in config/cookies.json file
        cookie_path: "config/cookies.json"
    }
    trigger_keyword: "your input"
}
```

## Usage

Noted:

- `selenium` need webdriver which matches your own one, for now we provide `109`, `110` and `110` for you choose, you could use `--config chrome_109`, `--config chrome_111`, default is `110`
- `selenium` different version supports different Python verions, for now we provide `400` and `480`, `400` for Python3.6 and lower, while `480` for Python3.7 and newer, you could use `--config selenium_400` to choose suitable verison and default is `480`

1. after setup, you could check whether ChatGPTs work well

```bash
bazel run //app:wechat_bot -- chatgpt_test
# eg: use selenium 400 and chrom 111 to build:
# bazel run //app:wechat_bot --config chrome_111 --config selenium_400 -- chatgpt_test
```

2. once it can response, you can run WechatBot, then you can reply in chatroom with setted `trigger_keyword`

```bash
bazel run //app:wechat_bot -- run
```

## TODO

- [ ] add headless mode
- [ ] find a better way check chatroom contents instead of polling
- [ ] use async to reply to different chatroom
- [ ] different chatroom with fixed ChatGPT thread that could collect user favorites

## Thanks

> revChatGPT: https://github.com/acheong08/ChatGPT  
> EdgeGPT: https://github.com/acheong08/EdgeGPT  
> WechatAutoReplyWithSelenium: https://github.com/Baoming520/WechatAutoReplyWithSeleniumgit
