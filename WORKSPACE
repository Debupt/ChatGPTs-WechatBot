workspace(name = "wechat_bot")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "firefox_driver",
    build_file = "//third_party:firefox_driver.BUILD",
    sha256 = "1eab226bf009599f5aa1d77d9ed4c374e10a03fd848b500be1b32cefd2cbec64",
    url = "https://github.com/mozilla/geckodriver/releases/download/v0.32.2/geckodriver-v0.32.2-linux64.tar.gz",
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

http_archive(
    name = "subpar",
    sha256 = "b80297a1b8d38027a86836dbadc22f55dc3ecad56728175381aa6330705ac10f",
    strip_prefix = "subpar-2.0.0",
    url = "https://github.com/google/subpar/archive/refs/tags/2.0.0.tar.gz"
)