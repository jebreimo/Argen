# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-10-10.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import templateprocessor


class OptionFunctionsGenerator(templateprocessor.Expander):
    def __init__(self, session):
        self._session = session


def generate_option_functions(session):
    generator = OptionFunctionsGenerator(session)
    return templateprocessor.make_lines(OPTION_FUNCTIONS_TEMPLATE, generator)


OPTION_FUNCTIONS_TEMPLATE = """\
void show_help(Arguments& arguments, const std::string& argument)
{
    write_help_text(std::cout);
}

template <typename T>
bool from_string(const std::string_view& str, T& value)
{
    std::istringstream stream(std::string(str.data(), str.size()));
    stream >> value;
    return !stream.fail() && stream.eof();
}

template <typename T>
bool read_value(ArgumentIterator& iterator, T& value,
                const Argument& argument)
{
    if (!iterator.hasNext())
    {
        write_error_text(to_string(argument) + ": no value given.");
        return false;
    }
    auto inputValue = iterator.nextValue();
    if (!from_string(inputValue, value))
    {
        write_error_text(to_string(argument) + ": invalid value \\""
                         + to_string(inputValue) + "\\".");
        return false;
    }
    return true;
}

Arguments& abort(Arguments& arguments,
                 Arguments::Result result,
                 bool autoExit)
{
    if (autoExit)
        exit(result);
    arguments.parseArguments_result = result;
    return arguments;
}
"""