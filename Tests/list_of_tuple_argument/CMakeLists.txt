cmake_minimum_required(VERSION 3.12)

set(CMAKE_CXX_STANDARD 14)

add_custom_command(
    OUTPUT  ParseArguments.h ParseArguments.cpp
    COMMAND python3 ${PROJECT_SOURCE_DIR}/../Argen/argen.py ${CMAKE_CURRENT_SOURCE_DIR}/helptext.txt
    MAIN_DEPENDENCY ${CMAKE_CURRENT_SOURCE_DIR}/helptext.txt
)

add_executable(list_of_tuple_argument
    ParseArguments.cpp
    ParseArguments.h)
