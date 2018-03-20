# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-03-07.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import type_deduction as td


def test_get_int_type():
    assert(td.get_int_type("0") == "int")
    assert(td.get_int_type("10L") == "long")
    assert(td.get_int_type("10Lu") == "unsigned long")
    assert(td.get_int_type("10Ull") == "unsigned long long")
    assert(td.get_int_type("0x56") == "int")
    assert(td.get_int_type("-0x56") == "int")
    assert(td.get_int_type("-0x56ll") == "long long")
    assert(td.get_int_type("0078") == "int")
    assert(td.get_int_type("0B10101") == "int")
    assert(td.get_int_type("B10101") is None)
    assert(td.get_int_type("-B10101") is None)
    assert(td.get_int_type("-10'000'000") == "int")
    assert(td.get_int_type("10'000'000u") == "unsigned")


def test_get_float_type():
    assert(td.get_float_type("123") is None)
    assert(td.get_float_type("123.1") == "double")
    assert(td.get_float_type("123.") == "double")
    assert(td.get_float_type("123.e+3") == "double")
    assert(td.get_float_type("123E-3") == "double")
    assert(td.get_float_type("123'456.1") == "double")
    assert(td.get_float_type("123.1e10") == "double")
    assert(td.get_float_type("123.1f") == "float")
    assert(td.get_float_type("123.1e3L") == "long double")
    assert(td.get_float_type("123.1e+") is None)
    assert(td.get_float_type(".1") is None)


def test_get_class_name_parenthesis():
    assert(td.get_class_name_parenthesis("foo(23, 56") == "foo")
    assert(td.get_class_name_parenthesis("{foo(23, 56}") is None)
    assert(td.get_class_name_parenthesis("(Object*)nullptr") == "Object*")


def test_get_class_name_braces():
    assert(td.get_class_name_braces("std::vector<int>{1, 2, 3}") == "std::vector<int>")


def test_get_value_type():
    assert(td.get_value_type('"foo"') == "std::string")
    assert(td.get_value_type("'\x0A'") == "char")
    assert(td.get_value_type("12'345'678") == "int")
    assert(td.get_value_type("12'345.678") == "double")
    assert(td.get_value_type("INT32_MIN") == "int32_t")
    assert(td.get_value_type("std::vector<int>()") == "std::vector<int>")
    assert(td.get_value_type('{"ABC", UINT64_MAX}') == "std::tuple<std::string, uint64_t>")


def test_find_char():
    assert(td.find_char('"Abra \\"kadabra\\"", ', ",", 0) == 18)
    assert(td.find_char("'A'", ",", 0) == -1)
    assert(td.find_char("'\\u3FA1', 2", ",", 0) == 8)
    assert(td.find_char('\n\t 123, ', ",", 0) == 6)
    assert(td.find_char('Class(1, 2)("1,3"), 123', ",", 0) == 18)
    assert(td.find_char("1, 2, 34, 5", ",", 5) == 8)
