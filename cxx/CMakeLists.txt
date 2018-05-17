project(cxx_decls_extractor)
cmake_minimum_required(VERSION 3.1.3)

set(CMAKE_CXX_FLAGS "-std=c++1y -fPIC -fno-rtti")
# -fno-exceptions

# CMAKE_EXE_LINKER_FLAGS
# CMAKE_MODULE_LINKER_FLAGS
# set(CMAKE_SHARED_LINKER_FLAGS "-fPIC -fvisibility-inlines-hidden -Wall -W -Wno-unused-parameter -Wwrite-strings -Wcast-qual -Wmissing-field-initializers -pedantic -Wno-long-long  -Wnon-virtual-dtor -Wdelete-non-virtual-dtor -Werror=date-time -fno-common -Woverloaded-virtual -Wno-nested-anon-types -Wl,-headerpad_max_install_names -Wl,-flat_namespace -Wl,-undefined -Wl,suppress -Wl,-rpath,/usr/lib" )
# CMAKE_STATIC_LINKER_FLAGS

include_directories(src ext)

file(GLOB SRC "src/*.cpp")

add_library(CXXDeclsExtractor SHARED ${SRC})
SET_TARGET_PROPERTIES(CXXDeclsExtractor PROPERTIES PREFIX "")
# add_subdirectory(src)
INSTALL(TARGETS CXXDeclsExtractor LIBRARY DESTINATION lib)
# INSTALL(FILES cxx_decls_extractor-config.cmake DESTINATION share/cxx_decls_extractor/cmake)
# INSTALL(FILES cxx_decls_extractor-config.sh DESTINATION bin)
