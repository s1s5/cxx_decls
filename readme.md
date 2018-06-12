# cxx decls extractor

## USAGE

``` shell
$ docker pull --disable-content-trust s1s5/cxx_decls
```

### cxx header files -> json
``` shell
$ docker run -i --rm -v <project_root>:/work s1s5/cxx_decls json <compile flags> <header file> > <output.json>

### e.g)
$ docker run -i --rm -v `pwd`:/work s1s5/cxx_decls json -std=c++1z examples/global_functions.hpp > a.json
```


### json files -> java interfaces

``` shell
$ docker run -i --rm -v <project_root>:/work s1s5/cxx_decls java <package name> <library name> <json files> > <output.tar>

### e.g)
$ docker run -i --rm -v `pwd`:/work s1s5/cxx_decls java com.example test a.json > /tmp/test.tar
```

### json files -> objc interfaces

``` shell
$ docker run -i --rm -v <project_root>:/work s1s5/cxx_decls objc <objc filename> <json files> > <output.tar>

### e.g)
$ docker run -i --rm -v `pwd`:/work s1s5/cxx_decls objc cxx2objc a.json > /tmp/test.tar
```


## DEBUG
docker run -i --rm -e PYTHONPATH=/work/py -v `pwd`:/work s1s5/cxx_decls objc cxx2objc a.json


docker run -i --rm -v `pwd`/examples/function_ptr.hpp:/work/sandbox.hpp s1s5/cxx_decls json -std=c++1z sandbox.hpp > a.json
docker run -i --rm -e PYTHONPATH=/work/py -v `pwd`:/work s1s5/cxx_decls objc sandbox a.json | tar -xC /tmp/objc-if/
