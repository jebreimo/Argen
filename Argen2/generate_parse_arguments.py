# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-08-14.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import templateprocessor
import deducedtype as dt


class ParseArgumentsGenerator(templateprocessor.Expander):
    def __init__(self, session):
        super().__init__()
        self._session = session
        self.class_name = session.settings.class_name
        self.function_name = session.settings.function_name

    def option_cases(self, params, context):
        result = []
        for opt in (a for a in self._session.arguments if a.flags):
            result.append("case Option_%s:" % opt.option_name)
            if opt.value:
                if opt.operation == "assign":
                    result.append("    result.%s = %s;"
                                  % (opt.member_name, opt.value))
                elif opt.operation == "append":
                    result.append("    result.%s.push_back(%s);"
                                  % (opt.member_name, opt.value))
            result.append("    break;")
        return result

    def has_program_name(self, params, context):
        return self._session.code_properties.has_program_name

def generate_parse_arguments(session):
    return templateprocessor.make_lines(PARSE_ARGUMENTS_TEMPLATE,
                                        ParseArgumentsGenerator(session))


PARSE_ARGUMENTS_TEMPLATE = """\
[[[IF has_program_name]]]
std::string getBaseName(const std::string& path)
{
    size_t pos = path.find_last_of("/\\\\");
    if (pos == std::string::npos)
        return path;
    else
        return path.substr(pos + 1);
}
[[[ENDIF]]]

[[[class_name]]] [[[function_name]]](int argc, char* argv[], bool autoExit)
{
    if (argc == 0)
        return Arguments();

[[[IF has_program_name]]]
    programName = getBaseName(argv[0]);

[[[ENDIF]]]
    Arguments result;
    ArgumentIterator argIt(argc - 1, argv + 1);

    while (auto arg = argIt.nextArgument())
    {
        auto optionCode = findOptionCode(arg);
        switch (optionCode)
        {
        [[[option_cases]]]
        default:
            break;
        }

        if (autoExit && result.parseArguments_result == Arguments::RESULT_ERROR)
            exit(EINVAL);

    }
    return result;
}
"""
