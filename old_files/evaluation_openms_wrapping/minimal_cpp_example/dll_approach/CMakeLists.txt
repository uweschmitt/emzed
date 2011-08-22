project (minimal_example_dllapproach)
cmake_minimum_required(VERSION 2.6)

SET(CMAKE_BUILD_TYPE release) # ExampleLib is in release mode

FIND_LIBRARY(FOUND_LIB ExampleLib PATHS .. ../build )
MESSAGE("Found Lib: ${FOUND_LIB}")

add_library(cdll SHARED cdll.cpp)
target_link_libraries(cdll ${FOUND_LIB})




