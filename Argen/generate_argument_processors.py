# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2019 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2019-01-04.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import generator_tools as gt


def generate_parameter_assignment(option, source_name, help_name):
    lines = []
    gt.append_assignment_conditions(lines, option, source_name, help_name)
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


def has_temp_variable(arg):
    operation_type = gt.get_operation_type(arg)
    if operation_type in (gt.Operations.APPEND_TUPLE,
                          gt.Operations.APPEND_VECTOR):
        return True
    elif operation_type == gt.Operations.EXTEND_VECTOR:
        return arg.valid_values
    else:
        return False


def make_read_argument(option, source, name):
    conditions = generate_parameter_assignment(option, source, name)
    if option.callback:
        conditions.append("%s(result, %s)" % (option.callback, name))
    lines = []
    if conditions:
        if has_temp_variable(option):
            lines.append("%s temp;" % option.value_type)
        lines.append("if (!" + conditions[0])
        for i in range(1, len(conditions)):
            lines.append("    || !" + conditions[i])
        lines[-1] += ")"
        lines.extend(("{",
                      "    return false;",
                      "}"))
    return lines


def make_scope(lines):
    result = ["{"]
    result.extend("    " + line for line in lines)
    result.append("}")
    return result


def determine_argument_expressions(arguments):
    ranges = determine_argument_ranges([a.count for a in arguments])
    result = []
    for i, r in enumerate(ranges):
        lo, hi = r
        arg = arguments[i]
        name = '"%s"' % arg.metavar
        if lo[0] == -1 and lo[1] == hi[1] - 1:
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


def generate_immediate_argument_processor(session):
    arg = session.code_properties.arguments[0]
    name = '"%s"' % arg.metavar
    return make_read_argument(arg, "arg.string", name)
