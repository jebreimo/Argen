# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-08-13.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import templateprocessor


class TestCodeGenerator(templateprocessor.Expander):
    def __init__(self, session):
        super().__init__()
        self._session = session

    def namespace(self, params, context):
        return self._session.code_properties.namespace


def generate_test_code(session):
    return templateprocessor.make_lines(TEST_TEMPLATE,
                                        TestCodeGenerator(session))


TEST_TEMPLATE = """\
#ifdef ARGEN_MAIN
#include <iostream>

template <typename T>
void write_value(std::ostream& stream, const char* label, const T& value)
{
    stream << label << value << "\\n";
}

#define WRITE_VALUE(name) write_value(std::cout, #name ": ", args.name)

int main(int argc, char* argv[])
{
    auto args = parse_arguments(argc, argv);
    WRITE_VALUE(parse_arguments_result);
    return 0;
}
#endif
"""
