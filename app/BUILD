package(default_visibility = ["//visibility:public"])
load("@subpar//:subpar.bzl", "par_binary")

par_binary(
    name = "chatgpt_bot",
    srcs = [
        "chatgpt_bot.py",
    ],
    deps = [
        "//chatgpt:chatgpt",
        "//rpa:selenium_wechat",
        "//rpa:playwright_wechat",
        "//proto:config_proto",
        "//utils:file_utils",
        "@click_py//:click",
    ],
    data = [
        "//config:config_files",
        "@firefox_driver",
    ],
)
