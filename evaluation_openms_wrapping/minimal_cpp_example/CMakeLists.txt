project (minimal_example)
cmake_minimum_required(VERSION 2.6)

SET(CMAKE_BUILD_TYPE release)
MESSAGE("build type is ${CMAKE_BUILD_TYPE}")
add_library(ExampleLib SHARED example.cpp)





