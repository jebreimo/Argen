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