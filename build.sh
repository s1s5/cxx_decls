#!/bin/bash
# -*- mode: shell-script -*-

set -eu  # <= 0以外が返るものがあったら止まる, 未定義の変数を使おうとしたときに打ち止め

script_dir=$(cd $(dirname ${BASH_SOURCE:-$0}); pwd)

pushd `pwd`
cd ${script_dir}

docker tag s1s5/llvm:50 cxx_decls-base
docker build -f docker/Dockerfile -t s1s5/cxx_decls .

docker tag s1s5/llvm:50_with_opencv cxx_decls-base
docker build -f docker/Dockerfile -t s1s5/cxx_decls:with_opencv .

