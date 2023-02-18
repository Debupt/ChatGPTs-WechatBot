package(default_visibility = ["//visibility:public"])

filegroup(
    name = "selenium_datas",
    srcs = glob(["selenium/**/*.js"]),
)

py_library(
    name = "selenium_libs",
    srcs = glob(["selenium/**/*.py"]),
    data = [":selenium_datas"],
)

py_library(
    name = "selenium",
    deps = select({
        "@//bazel:selenium_400": ["@selenium_py_400//:selenium_libs"],
        "//conditions:default": ["@selenium_py//:selenium_libs"],
    }),
)
