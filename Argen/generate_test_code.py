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


TEST_TEMPLATE = """
#include <iostream>

int main(int argc, char* argv[])
{
    [[[namespace]]]::write_help_text(std::cout, 0); 
    return 0;
}
"""