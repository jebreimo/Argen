#include <iostream>
#include "ParseArguments.h"

void print_string(int outer_size, const std::string& outer_str,
                  int inner_size, const std::string& inner_str)
{
    for (int i = 0; i < outer_size; ++i)
        std::cout << outer_str;
    for (int i = 0; i < inner_size; ++i)
        std::cout << inner_str;
    for (int i = 0; i < outer_size; ++i)
        std::cout << outer_str;
    std::cout << '\n';
}

bool print_string_callback(const Arguments& arguments, const std::string&)
{
    print_string(std::get<0>(arguments.NUM_NUM.back()), arguments.outer,
                 std::get<1>(arguments.NUM_NUM.back()), arguments.inner);
    return true;
}
