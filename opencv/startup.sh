#!/bin/bash
# -*- mode: shell-script -*-

set -eu  # <= 0以外が返るものがあったら止まる, 未定義の変数を使おうとしたときに打ち止め

if [ ! -e opencv ]; then
    git clone https://github.com/opencv/opencv.git
fi

cd opencv
git fetch
git checkout 3.4.0
cd ..


if [ ! -e opencv_contrib ]; then
    git clone https://github.com/opencv/opencv_contrib.git
fi

cd opencv_contrib
git fetch
git checkout 3.4.0
cd ..
