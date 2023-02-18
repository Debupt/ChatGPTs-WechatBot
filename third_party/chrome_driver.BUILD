package(default_visibility = ["//visibility:public"])

filegroup(
    name = "chrome_driver_binary",
    srcs = [
        "chromedriver",
    ],
)

filegroup(
    name = "chrome_driver",
    srcs = select({
        "@//bazel:chrome_driver_109": ["@chrome_driver_109//:chrome_driver_binary"],
        "@//bazel:chrome_driver_111": ["@chrome_driver_111//:chrome_driver_binary"],
        "//conditions:default": ["@chrome_driver//:chrome_driver_binary"],
    }),
)
