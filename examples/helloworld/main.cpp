#include <iostream>
#include "ParseArguments.hpp"

void put(std::ostream& os, char c, size_t n)
{
    for (size_t i = 0; i != n; ++i)
        os.put(c);
}

void centerText(std::ostream& os, const std::string& text, int width,
                char fillChar = ' ')
{
    int remainder = width - text.size();
    if (remainder < 0)
        remainder = 0;
    put(os, fillChar, (remainder + 1) / 2);
    os << text;
    put(os, fillChar, remainder / 2);
}

int main(int argv, char* argv[])
{
    return 0;
}
