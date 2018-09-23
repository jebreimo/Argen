# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-08-14.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import templateprocessor


class ParseArgumentsGenerator(templateprocessor.Expander):
    def __init__(self, session):
        super().__init__()
        self._session = session
        self._options = [a for a in self._session.arguments if a.flags]
        self.class_name = session.settings.class_name
        self.function_name = session.settings.function_name
        self.has_final_option = any(o for o in self._options
                                    if o.post_operation == "final")
        self.has_program_name = session.code_properties.has_program_name

    def option_cases(self, params, context):
        result = []
        post_op_gen = PostOperationGenerator(self._session)
        for opt in self._options:
            result.append("case Option_%s:" % opt.option_name)
            if opt.value:
                if opt.operation == "assign":
                    result.append("    result.%s = %s;"
                                  % (opt.member_name, opt.value))
                elif opt.operation == "append":
                    result.append("    result.%s.push_back(%s);"
                                  % (opt.member_name, opt.value))
                elif opt.operation == "extend":
                    result.append("    result.%s.insert(result.%s.end(), %s);"
                                  % (opt.member_name, opt.member_name,
                                     opt.value))
            if opt.post_operation == "none":
                result.append("    break;")
            else:
                post_op_gen.option = opt
                result.extend(templateprocessor.make_lines(
                    POST_OPERATION_TEMPLATE,
                    post_op_gen))
        return result


def generate_parse_arguments(session):
    return templateprocessor.make_lines(PARSE_ARGUMENTS_TEMPLATE,
                                        ParseArgumentsGenerator(session))


class PostOperationGenerator(templateprocessor.Expander):
    def __init__(self, session):
        super().__init__()
        self.class_name = session.settings.class_name
        self.function_name = session.settings.function_name
        self.option = None

    def option_name(self, *args):
        return self.option.option_name

    def abort_option(self, *args):
        return self.option.post_operation == "abort"

    def return_option(self, *args):
        return self.option.post_operation == "return"

    def final_option(self, *args):
        return self.option.post_operation == "final"


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
        return [[[class_name]]]();

[[[IF has_program_name]]]
    programName = getBaseName(argv[0]);

[[[ENDIF]]]
    [[[class_name]]] result;
    ArgumentIterator argIt(argc - 1, argv + 1);
[[[IF has_final_option]]]
    bool finalOption = false;
[[[ENDIF]]]
    while (auto arg = argIt.nextArgument())
    {
        auto optionCode = findOptionCode(arg);
        switch (optionCode)
        {
        [[[option_cases]]]
        default:
            break;
        }

        if (autoExit && result.parseArguments_result == [[[class_name]]]::RESULT_ERROR)
            exit(EINVAL);
        [[[IF has_final_option]]]
        if (finalOption)
            break;
        [[[ENDIF]]]
    }
    return result;
}
"""

POST_OPERATION_TEMPLATE = """\
[[[IF abort_option]]]
    if (autoExit)
    {
        exit([[[class_name]]]::OPTION_[[[option_name]]]);
    }
    else
    {
        result.[[[function_name]]]_result = [[[class_name]]]::OPTION_[[[option_name]]];
        return result;
    }
[[[ELIF return_option]]]
    result.[[[function_name]]]_result = [[[class_name]]]::OPTION_[[[option_name]]];
    return result;
[[[ELIF final_option]]]
    finalOption = true;
    break;
[[[ELSE]]]
    break;
[[[ENDIF]]]\
"""