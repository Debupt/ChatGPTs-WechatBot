package(default_visibility = ["//visibility:public"])

py_binary(
    name = "selenium_wechat",
    srcs = [
        "selenium_wechat.py",
    ],
    deps = [
        "//utils:utils",
        "//chatgpt:chatgpt",
        "@selenium_py//:selenium",
    ],
)

py_library(
    name = "playwright_wechat",
    srcs = ["playwright_wechat.py"],
    deps = [
        "//utils:utils",
    ],
)

py_library(
    name = "rpa_bot",
    deps = [
        ":selenium_wechat",
        ":playwright_wechat",
    ],
)
