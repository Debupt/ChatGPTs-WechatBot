workspace(name = "wechat_bot")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

# find corresponding chrome version: https://chromedriver.chromium.org/home
http_archive(
    name = "chrome_driver",
    build_file = "//third_party:chrome_driver.BUILD",
    sha256 = "40d0ee4e2d821d7fe8be3b0601579e7665f58bd9296372c1dea68e6f9325acad",
    url = "https://chromedriver.storage.googleapis.com/110.0.5481.77/chromedriver_linux64.zip",
)

http_archive(
    name = "chrome_driver_111",
    build_file = "//third_party:chrome_driver.BUILD",
    sha256 = "",
    url = "https://chromedriver.storage.googleapis.com/111.0.5563.19/chromedriver_linux64.zip"
)

http_archive(
    name = "chrome_driver_109",
    build_file = "//third_party:chrome_driver.BUILD",
    sha256 = "",
    url = "https://chromedriver.storage.googleapis.com/109.0.5414.74/chromedriver_linux64.zip"
)

http_archive(
    name = "selenium_py_400",
    build_file = "//third_party:selenium_py.BUILD",
    sha256 = "a9779ddc69cf03b75d94062c5e948f763919cf3341c77272f94cd05e6b4c7b32",
    type = "zip",
    url = "https://files.pythonhosted.org/packages/2b/b6/53b86357953961faaccdf5413c83d72a2efaf279b73bc80d3cb2e8d1c64c/selenium-4.0.0a6.post2-py2.py3-none-any.whl#sha256=a9779ddc69cf03b75d94062c5e948f763919cf3341c77272f94cd05e6b4c7b32",
)

http_archive(
    name = "selenium_py",
    build_file = "//third_party:selenium_py.BUILD",
    sha256 = "bd04eb41395605d9b2b65fe587f3fed21431da75512985c52772529e5e210c60",
    type = "zip",
    url = "https://files.pythonhosted.org/packages/ad/13/481aa476a9bcfec0bf74140a4c395dede0569cf56dc773abec181f95e30f/selenium-4.8.2-py3-none-any.whl#sha256=bd04eb41395605d9b2b65fe587f3fed21431da75512985c52772529e5e210c60",
)

http_archive(
    name = "com_google_protobuf",
    sha256 = "b07772d38ab07e55eca4d50f4b53da2d998bb221575c60a4f81100242d4b4889",
    strip_prefix = "protobuf-3.20.0",
    urls = [
        "https://mirror.bazel.build/github.com/protocolbuffers/protobuf/archive/v3.20.0.tar.gz",
        "https://github.com/protocolbuffers/protobuf/archive/v3.20.0.tar.gz",
    ],
)

load("@com_google_protobuf//:protobuf_deps.bzl", "protobuf_deps")
protobuf_deps()

http_archive(
    name = "click_py",
    build_file = "//third_party:click_py.BUILD",
    sha256 = "f15516df478d5a56180fbf80e68f206010e6d160fc39fa508b65e035fd75130b",
    strip_prefix = "click-6.7",
    url = "https://files.pythonhosted.org/packages/95/d9/c3336b6b5711c3ab9d1d3a80f1a3e2afeb9d8c02a7166462f6cc96570897/click-6.7.tar.gz",
)
