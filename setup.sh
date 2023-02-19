#!/bin/bash

# install Bazel
sudo apt install g++ unzip zip zlib1g-dev -y
sudo dpkg -i packages/bazel_4.2.2-linux-x86_64.deb

# install python dependencies
pip3 install -r requirements.txt
