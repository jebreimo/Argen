# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2019 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2019-01-20.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import deducedtype as dt


class Operations:
    NO_OPERATION = 0
    ASSIGN_CONSTANT = 1
    ASSIGN_VALUE = 2
    ASSIGN_TUPLE = 3
    ASSIGN_VECTOR = 4
    APPEND_CONSTANT = 11
    APPEND_VALUE = 12
    APPEND_TUPLE = 13
    APPEND_VECTOR = 14
    EXTEND_CONSTANT = 21
    EXTEND_VECTOR = 24


def get_operation_type(argument):
    if argument.operation == "assign":
        op_value = 0
    elif argument.operation == "append":
        op_value = 10
    elif argument.operation == "extend":
        op_value = 20
    else:
        return Operations.NO_OPERATION
    if argument.value:
        type_value = 1
    elif not argument.value_type.subtypes:
        type_value = 2
    elif dt.is_tuple(argument.value_type):
        type_value = 3
    else:
        type_value = 4
    return op_value + type_value


def generate_check_value_lambda(valid_values):
    tests = []
    for entry in valid_values:
        lo, hi = entry
        if not lo and not hi:
            continue
        elif lo == hi:
            tests.append(f"v == {lo}")
        elif lo and hi:
            if len(valid_values) == 1:
                tests.append(f"{lo} <= v && v <= {hi}")
            else:
                tests.append(f"({lo} <= v && v <= {hi})")
        elif lo:
            tests.append(f"{lo} <= v")
        else:
            tests.append(f"v <= {hi}")
    return "[](auto&& v){return %s;}" % " || ".join(tests)


def generate_check_value_text(valid_values):
    tokens = []
    for entry in valid_values:
        lo, hi = entry
        if not lo and not hi:
            continue
        elif lo == hi:
            tokens.append(lo)
        elif lo and hi:
            tokens.append(f"{lo}...{hi}")
        elif lo:
            tokens.append(f"{lo}...")
        else:
            tokens.append(f"...{hi}")
    return '"%s"' % ", ".join(t.replace('"', '\\"') for t in tokens)


def make_check_value(function_name, value_name, valid_values, name):
    return "%s(%s, %s, %s, %s)" \
           % (function_name, value_name,
              generate_check_value_lambda(valid_values),
              generate_check_value_text(valid_values),
              name)


def append_check_value(lines, argument, operation_type, name):
    valid_values = argument.valid_values
    if not valid_values:
        return
    if operation_type == Operations.ASSIGN_VALUE:
        lines.append(make_check_value("check_value",
                                      "result." + argument.member_name,
                                      valid_values[0],
                                      name))
    elif operation_type == Operations.ASSIGN_VECTOR:
        lines.append(make_check_value("check_values",
                                      "result." + argument.member_name,
                                      valid_values[0],
                                      name))
    elif operation_type == Operations.APPEND_VALUE:
        lines.append(make_check_value("check_value",
                                      "result.%s.back()" % argument.member_name,
                                      argument.valid_values[0],
                                      name))
    elif operation_type in (Operations.APPEND_VECTOR, Operations.EXTEND_VECTOR):
        lines.append(make_check_value("check_values", "temp",
                                      argument.valid_values[0],
                                      name))
    elif operation_type in (Operations.APPEND_TUPLE, Operations.ASSIGN_TUPLE):
        if operation_type == Operations.ASSIGN_TUPLE:
            variable = "result." + argument.member_name
        else:
            variable = "temp"
        for i in range(len(valid_values)):
            lines.append(make_check_value("check_value",
                                          "std::get<%d>(%s)" % (i, variable),
                                          valid_values[i],
                                          name))


def make_split_value(option, source_name, dest_name):
    if option.separator_count[1]:
        max_count = str(option.separator_count[1])
    else:
        max_count = "SIZE_MAX"
    return "split_value(parts, %s, '%s', %d, %s, %s)" \
           % (source_name, option.separator, option.separator_count[0],
              max_count, dest_name)


def append_assignment_conditions(lines, argument, src_name, help_name):
    operation_type = get_operation_type(argument)
    dst_name = "result." + argument.member_name
    if operation_type == Operations.ASSIGN_VALUE:
        lines.append("parse_and_assign(%s, %s, %s)"
                     % (dst_name, src_name, help_name))
        append_check_value(lines, argument, operation_type, help_name)
    elif operation_type == Operations.ASSIGN_TUPLE:
        lines.append(make_split_value(argument, src_name, help_name))
        for i in range(len(argument.value_type.subtypes)):
            tmp_name = "std::get<%d>(%s)" % (i, dst_name)
            lines.append("parse_and_assign(%s, parts[%d], %s)"
                         % (tmp_name, i, help_name))
        append_check_value(lines, argument, operation_type, help_name)
    elif operation_type == Operations.ASSIGN_VECTOR:
        if argument.separator is None:
            lines.append("parse_and_assign(%s, std::vector<std::string_view>{%s}, %s)"
                         % (dst_name, src_name, help_name))
        else:
            lines.append(make_split_value(argument, src_name, help_name))
            lines.append("parse_and_assign(%s, parts, %s)"
                         % (dst_name, help_name))
        append_check_value(lines, argument, operation_type, help_name)
    elif operation_type == Operations.APPEND_VALUE:
        lines.append("parse_and_append(%s, %s, %s)"
                     % (dst_name, src_name, help_name))
        append_check_value(lines, argument, operation_type, help_name)
    elif operation_type == Operations.APPEND_TUPLE:
        lines.append(make_split_value(argument, src_name, help_name))
        for i in range(len(argument.value_type.subtypes)):
            tmp_name = "std::get<%d>(temp)" % i
            lines.append("parse_and_assign(%s, parts[%d], %s)"
                         % (tmp_name, i, help_name))
        append_check_value(lines, argument, operation_type, help_name)
        lines.append("append(%s, std::move(temp))" % dst_name)
    elif operation_type == Operations.APPEND_VECTOR:
        lines.append(make_split_value(argument, src_name, help_name))
        for i in range(len(argument.value_type.subtypes)):
            lines.append("parse_and_assign(temp, parts, %s)" % help_name)
        lines.append("append(%s, std::move(temp))" % dst_name)
        append_check_value(lines, argument, operation_type, help_name)
    elif operation_type == Operations.EXTEND_VECTOR:
        lines.append(make_split_value(argument, src_name, help_name))
        if argument.valid_values:
            lines.append("parse_and_assign(temp, parts, %s)" % help_name)
            lines.append("extend(%s, std::move(temp))" % dst_name)
        else:
            lines.append("parse_and_extend(%s, parts, %s)"
                         % (dst_name, help_name))


def get_argument_assignment_methods(argument):
    operation_type = get_operation_type(argument)
    if operation_type == Operations.ASSIGN_VALUE:
        return ["parse_and_assign"]
    elif operation_type == Operations.ASSIGN_TUPLE:
        return ["parse_and_assign"]
    elif operation_type == Operations.ASSIGN_VECTOR:
        return ["parse_and_assign_vector"]
    elif operation_type == Operations.APPEND_VALUE:
        return ["parse_and_append"]
    elif operation_type == Operations.APPEND_TUPLE:
        return ["parse_and_assign", "append"]
    elif operation_type == Operations.APPEND_VECTOR:
        return ["parse_and_assign_vector", "append"]
    elif operation_type == Operations.EXTEND_VECTOR:
        if argument.valid_values:
            return ["parse_and_assign_vector", "extend"]
        else:
            return ["parse_and_extend"]


def get_assignment_methods(arguments):
    methods = set()
    for argument in arguments:
        methods.update(get_argument_assignment_methods(argument))
    return methods
