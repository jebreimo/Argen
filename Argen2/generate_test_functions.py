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

    if value_type.subtypes:
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

TEST_TUPLE_VALUES = """\
bool check_value(const [[[type]]]& value,
                 const Argument& argument)
{
    return [[[check_each_value]]];
}
"""
