# cxx decls extractor

## USAGE

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
