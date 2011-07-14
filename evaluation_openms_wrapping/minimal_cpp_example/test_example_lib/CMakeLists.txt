project (minimal_example_dllapproach)
cmake_minimum_required(VERSION 2.6)

SET(CMAKE_BUILD_TYPE release) # ExampleLib is in release mode

FIND_LIBRARY(FOUND_LIB ExampleLib PATHS .. ../build )
MESSAGE("Found Lib: ${FOUND_LIB}")

add_executable(main main.cpp)
target_link_libraries(main ${FOUND_LIB})


INSTALL(TARGETS main
        RUNTIME DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}
        LIBRARY DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}
        ARCHIVE DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}                
       )

INSTALL(FILES ${CMAKE_CURRENT_SOURCE_DIR}/../ExampleLib.dll DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})






