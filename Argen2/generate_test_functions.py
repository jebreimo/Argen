# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-10-31.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import templateprocessor


def generate_test(valid_values):
    tests = []
    for entry in valid_values:
        lo, hi = entry
        if not lo and not hi:
            continue
        elif lo == hi:
            tests.append(f"value == {lo}")
        elif lo and hi:
            tests.append(f"{lo} <= value && value <= {hi}")
        elif lo:
            tests.append(f"{lo} <= value")
        else:
            tests.append(f"value <= {hi}")
    return "[](auto&& v){return %s;}" % " || ".join(tests)


def generate_text(valid_values):
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


def generate_test_function(valid_values, value_type, argument, session):
    if not valid_values:
        return None

    if not value_type.subtypes:
        if len(valid_values) > 1:
            session.logger.error("Property 'valid_values' is invalid.",
                                 argument=argument)
            return None
        valid_values = valid_values[0]
        if len(valid_values) == 1:
            lo, hi = valid_values[0]
            if not lo and not hi:
                return None
            elif not lo:
                return [TEST_MAX_RANGE_TEMPLATE]
            elif not hi:
                return [TEST_MIN_RANGE_TEMPLATE]
            elif lo != hi:
                return [TEST_MINMAX_RANGE_TEMPLATE]
            else:
                session.logger.warn("Argument has only one legal value: "
                                    + lo)
                # TODO Single value check.
                return None
        else:
            return [generate_complex_value_check(valid_values, value_type, argument, session)]
    else:
        functions = []
        subtypes = value_type.subtypes
        if len(valid_values) > len(subtypes):
            session.logger.error("Too many entries in property 'valid_values'.",
                                 argument=argument)
            return None
        elif len(valid_values) < len(subtypes):
            for i in range(len(subtypes) - len(valid_values)):
                valid_values.append(valid_values[-1])
        for subtype, valid_values in zip(subtypes, valid_values):
            text = generate_test_function([valid_values], subtype,
                                          argument, session)
            if text:
                functions.extend(text)
        return functions


def generate_test_functions(session):
    functions = {}
    for arg in session.arguments:
        funcs = generate_test_function(arg.valid_values, arg.value_type,
                                       arg, session)
        if funcs:
            for func in funcs:
                args = functions.get(func)
                if not args:
                    functions[func] = [arg]
                else:
                    args.append(arg)
    lines = []
    for func in functions:
        if func.startswith("bool"):
            lines.extend(func.split("\n"))
        else:
            lines.extend(func.split("\n"))
    return lines


class CheckValueGenerator(templateprocessor.Expander):
    def __init__(self, valid_values, value_type, argument, session):
        super().__init__()
        self._session = session
        self._argument = argument
        self._valid_values = valid_values
        self._value_type = value_type

    def type(self, *args):
        return str(self._value_type)

    def test(self, *args):
        return generate_test(self._valid_values)

    def legal_values(self, *args):
        return generate_text(self._valid_values)


def generate_complex_value_check(valid_values, value_type, argument, session):
    gen = CheckValueGenerator(valid_values, value_type, argument, session)
    text = templateprocessor.make_text(TEST_COMPLEX_LEGAL_VALUES, gen)
    print(text)
    return text


TEST_LEGAL_VALUES = """\
template <typename T, typename CheckFunc>
bool check_value(T value, CheckFunc check_func,
                 const char* legal_values_text,
                 const Argument& argument)
{
    if (!check_func(value))
    {
        std::stringstream ss;
        ss << argument << ": illegal value: " << value << ". (Legal values: "
           << legal_values_text 
           << ")";
        write_error_text(ss.str());
        return false;
    }
    return true;
}
"""


TEST_COMPLEX_LEGAL_VALUES = """\
bool check_%s([[[type]]] value, const Argument& argument)
{
    if ([[[test]]])
    {
        std::stringstream ss;
        ss << argument << ": illegal value: " << value << ". (Legal values: "
           << [[[legal_values]]] 
           << ")";
        write_error_text(ss.str());
        return false;
    }
    return true;
}
"""


TEST_MINMAX_RANGE_TEMPLATE = """\
template <typename T>
bool check_value_is_in_range(T value, T minValue, T maxValue,
                             const Argument& argument)
{
    if (value < minValue || maxValue < value)
    {
        std::stringstream ss;
        ss << argument << ": illegal value: " << value
           << ". (Legal range: " << minValue <<  "..."
           << maxValue << ")";
        write_error_text(ss.str());
        return false;
    }
    return true;
}
"""


TEST_MIN_RANGE_TEMPLATE = """\
template <typename T>
bool check_value_is_at_least(T value, T minValue, const Argument& argument)
{
    if (value < minValue)
    {
        std::stringstream ss;
        ss << argument << ": illegal value: " << value
           << ". (Minimum value: " << minValue << ")";
        write_error_text(ss.str());
        return false;
    }
    return true;
}
"""


TEST_MAX_RANGE_TEMPLATE = """\
template <typename T>
bool check_value_is_at_most(T value, T maxValue, const Argument& argument)
{
    if (maxValue < value)
    {
        std::stringstream ss;
        ss << argument << ": illegal value: " << value
           << ". (Maximum value: " << maxValue << ")";
        write_error_text(ss.str());
        return false;
    }
    return true;
}
"""
