project (minimal_example_dllapproach)
cmake_minimum_required(VERSION 2.6)

FIND_LIBRARY(FOUND_LIB ExampleLib PATHS .. ../build )
MESSAGE("Found Lib: ${FOUND_LIB}")

add_library(cdll SHARED cdll.cpp)
target_link_libraries(cdll ${FOUND_LIB})




