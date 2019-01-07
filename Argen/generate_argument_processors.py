# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2019 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2019-01-04.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import deducedtype as dt


class Operations:
    NO_OPERATION = 0
    ASSIGN_VALUE = 2
    ASSIGN_TUPLE = 3
    ASSIGN_VECTOR = 4
    APPEND_VALUE = 12
    APPEND_TUPLE = 13
    APPEND_VECTOR = 14
    EXTEND_VECTOR = 24


def get_operation_type(option):
    if option.operation == "assign":
        op_value = 0
    elif option.operation == "append":
        op_value = 10
    elif option.operation == "extend":
        op_value = 20
    else:
        return Operations.NO_OPERATION
    if option.value:
        type_value = 1
    elif not option.value_type.subtypes:
        type_value = 2
    elif dt.is_tuple(option.value_type):
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


def append_check_value(lines, option, operation_type, name):
    valid_values = option.valid_values
    if not valid_values:
        return
    if operation_type == Operations.ASSIGN_VALUE:
        lines.append(make_check_value("check_value",
                                      "result." + option.member_name,
                                      valid_values[0],
                                      name))
    elif operation_type == Operations.ASSIGN_VECTOR:
        lines.append(make_check_value("check_values",
                                      "result." + option.member_name,
                                      valid_values[0],
                                      name))
    elif operation_type == Operations.APPEND_VALUE:
        lines.append(make_check_value("check_value",
                                      "result.%s.back()" % option.member_name,
                                      option.valid_values[0],
                                      name))
    elif operation_type in (Operations.APPEND_VECTOR, Operations.EXTEND_VECTOR):
        lines.append(make_check_value("check_values", "temp",
                                      option.valid_values[0],
                                      name))
    elif operation_type in (Operations.APPEND_TUPLE, Operations.ASSIGN_TUPLE):
        if operation_type == Operations.ASSIGN_TUPLE:
            variable = "result." + option.member_name
        else:
            variable = "temp"
        for i in range(len(valid_values)):
            lines.append(make_check_value("check_value",
                                          "std::get<%d>(%s)" % (i, variable),
                                          valid_values[i],
                                          name))


def make_split_value(option, source, name):
    if option.separator_count[1]:
        max_count = str(option.separator_count[1])
    else:
        max_count = "SIZE_MAX"
    return "split_value(parts, %s, '%s', %d, %s, %s)" \
           % (source, option.separator, option.separator_count[0], max_count, name)


def generate_parameter_assignment(option, source, name):
    operation_type = get_operation_type(option)
    destination = "result." + option.member_name
    lines = []
    if operation_type == Operations.ASSIGN_VALUE:
        lines.append("parse_and_assign(%s, %s, %s)" % (destination, source, name))
        append_check_value(lines, option, operation_type, name)
    elif operation_type == Operations.ASSIGN_TUPLE:
        lines.append(make_split_value(option, source, name))
        for i in range(len(option.value_type.subtypes)):
            name = "std::get<%d>(%s)" % (i, destination)
            lines.append("parse_and_assign(%s, parts[%d], %s)" % (name, i, name))
        append_check_value(lines, option, operation_type, name)
    elif operation_type == Operations.ASSIGN_VECTOR:
        if option.separator is None:
            lines.append("parse_and_assign(%s, std::vector<std::string_view>{%s}, %s)"
                         % (destination, source, name))
        else:
            lines.append(make_split_value(option, source, name))
            lines.append("parse_and_assign(%s, parts, %s)" % (destination, name))
        append_check_value(lines, option, operation_type, name)
    elif operation_type == Operations.APPEND_VALUE:
        lines.append("parse_and_append(%s, %s, %s)" % (destination, source, name))
        append_check_value(lines, option, operation_type, name)
    elif operation_type == Operations.APPEND_TUPLE:
        lines.append(make_split_value(option, source, name))
        for i in range(len(option.value_type.subtypes)):
            name = "std::get<%d>(temp)" % i
            lines.append("parse_and_assign(%s, parts[%d], %s)" % (name, i, name))
        append_check_value(lines, option, operation_type, name)
        lines.append("append(%s, std::move(temp))" % destination)
    elif operation_type == Operations.APPEND_VECTOR:
        lines.append(make_split_value(option, source, name))
        for i in range(len(option.value_type.subtypes)):
            lines.append("parse_and_assign(temp, parts, %s)" % name)
        lines.append("append(%s, std::move(temp))" % destination)
        append_check_value(lines, option, operation_type, name)
    elif operation_type == Operations.EXTEND_VECTOR:
        lines.append(make_split_value(option, source, name))
        if option.valid_values:
            lines.append("parse_and_assign(temp, parts, %s)" % name)
            lines.append("extend(%s, std::move(temp))" % destination)
        else:
            lines.append("parse_and_extend(%s, parts, %s)" % (destination, name))
    return lines


def determine_argument_ranges(counts):
    min_count = 0
    for lo, hi in counts:
        if lo:
            min_count += lo
    result = []
    acc_pos, acc_neg = 0, -min_count
    start = (acc_pos, acc_neg)
    i = 0
    for i in range(len(counts)):
        lo, hi = counts[i]
        if hi is not None:
            acc_pos += hi
        else:
            acc_pos = -1
        acc_neg += lo
        end = acc_pos, acc_neg
        result.append((start, end))
        start = end
        if hi is None:
            break
    i += 1
    for i in range(i, len(counts)):
        lo, hi = counts[i]
        acc_neg += lo
        end = acc_pos, acc_neg
        result.append((start, end))
        start = end

    return result


def make_read_argument(option, source, name):
    conditions = generate_parameter_assignment(option, source, name)

    if option.callback:
        conditions.append("%s(result, %s)" % (option.callback, name))

    lines = []
    if conditions:
        lines.append("if (!" + conditions[0])
        for i in range(1, len(conditions)):
            lines.append("    || !" + conditions[i])
        lines[-1] += ")"
        lines.extend(("{",
                      "    return false;",
                      "}"))
    return lines


def make_scope(lines):
    result = []
    result.append("{")
    for line in lines:
        result.append("    " + line)
    result.append("}")
    return result


def determine_argument_expressions(arguments):
    ranges = determine_argument_ranges([a.count for a in arguments])
    result = []
    for i, r in enumerate(ranges):
        lo, hi = r
        arg = arguments[i]
        name = '"%s"' % arg.metavar
        if hi[0] == -1 and lo[1] == hi[1] - 1:
            result.extend(make_read_argument(arg, "arguments[i++]", name))
        elif hi[0] == -1:
            if hi[1] == 0:
                result.append("for (; i < n; ++i)")
            else:
                result.append("for (; i < n - %d; ++i)" % (-hi[1]))
            lines = make_read_argument(arg, "arguments[i]", name)
            result.extend(make_scope(lines))
        elif lo[0] == hi[0] - 1:
            if lo[1] != hi[1]:
                result.extend(make_read_argument(arg, "arguments[i++]", name))
            else:
                if hi[1] == 0:
                    result.append("if (i < n)")
                else:
                    result.append("if (i < n - %d)" % -hi[1])
                lines = make_read_argument(arg, "arguments[i++]", name)
                result.extend(make_scope(lines))
        else:
            result.append("for (; i < std::min<size_t>(%d, n - %d); ++i)"
                          % (hi[0], -hi[1]))
            lines = make_read_argument(arg, "arguments[i]", name)
            result.extend(make_scope(lines))
    return result


def generate_argument_processors(session):
    return determine_argument_expressions(session.code_properties.arguments)


ARGUMENT_PROCESSOR_TEMPLATE = """\
[[[IF has_temp_variable]]]
    {
        [[[temp_variable_type]]] temp;
    }
[[[ELSE]]]
[[[ENDIF]]]\
"""
