# cxx decls extractor

docker run -t -i --rm -v ~/work/cxx_decls_extractor/test:/tmp/test s1s5/cxx_decls clang -Xclang -load -Xclang /usr/local/lib/CXXDeclsExtractor.so -Xclang -plugin -Xclang print-decls -std=c++1z /tmp/test/example_000.hpp > a.json


docker run -t -i --rm -v /tmp/conv_java/output:/output -v `pwd`:/tmp/source/ s1s5/cxx_decls python -m blueboss.conv_java --libname test --dst-dir /output --default-package com.example --jni-filename /output/jniex.cpp /tmp/source/a.json

docker run -t -i --rm -v /tmp/conv_objc/output:/output -v `pwd`:/tmp/source/ s1s5/cxx_decls python -m blueboss.conv_objc --dst-header /output/objc.h --dst-source /output/objc.mm /tmp/source/a.json

