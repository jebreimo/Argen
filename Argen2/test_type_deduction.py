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
    assert(td.get_int_type("0").type_category == "number")
    assert(td.get_int_type("10L").specific_type == "long")
    assert(td.get_int_type("10Lu").specific_type == "unsigned long")
    assert(td.get_int_type("10Ull").specific_type == "unsigned long long")
    assert(td.get_int_type("0x56").type_category == "integer")
    assert(td.get_int_type("-0x56").type_category == "integer")
    assert(td.get_int_type("-0x56ll").specific_type == "long long")
    assert(td.get_int_type("0078").type_category == "integer")
    assert(td.get_int_type("0B10101").type_category == "integer")
    assert(td.get_int_type("B10101") is None)
    assert(td.get_int_type("-B10101") is None)
    assert(td.get_int_type("-10'000'000").type_category == "number")
    assert(td.get_int_type("10'000'000u").specific_type == "unsigned")


def test_get_float_type():
    assert(td.get_float_type("123") is None)
    assert(td.get_float_type("123.1").type_category == "real")
    assert(td.get_float_type("123.").type_category == "real")
    assert(td.get_float_type("123.e+3").type_category == "real")
    assert(td.get_float_type("123E-3").type_category == "real")
    assert(td.get_float_type("123'456.1").type_category == "real")
    assert(td.get_float_type("123.1e10").type_category == "real")
    assert(td.get_float_type("123.1f").specific_type == "float")
    assert(td.get_float_type("123.1e3L").specific_type == "long double")
    assert(td.get_float_type("123.1e+") is None)
    assert(td.get_float_type(".1") is None)


def test_get_class_name_parenthesis():
    assert(td.get_class_name_parenthesis("foo(23, 56").specific_type == "foo")
    assert(td.get_class_name_parenthesis("{foo(23, 56}") is None)
    assert(td.get_class_name_parenthesis("(Object*)nullptr").specific_type == "Object*")


def test_get_class_name_braces():
    assert(td.get_class_name_braces("std::vector<int>{1, 2, 3}").specific_type == "std::vector<int>")


def test_get_value_type():
    assert(td.get_value_type('"foo"').type_category == "string")
    assert(td.get_value_type("'\x0A'").specific_type == "char")
    assert(td.get_value_type("12'345'678").type_category == "number")
    assert(td.get_value_type("12'345.678").type_category == "real")
    assert(td.get_value_type("INT32_MIN").specific_type == "int32_t")
    assert(td.get_value_type("std::vector<int>()").specific_type == "std::vector<int>")
    typ = td.get_value_type('{"ABC", UINT64_MAX}')
    assert(len(typ.subtypes) == 2)
    assert(typ.subtypes[0].type_category == "string")
    assert(typ.subtypes[1].specific_type == "uint64_t")


def test_find_char():
    assert(td.find_char('"Abra \\"kadabra\\"", ', ",", 0) == 18)
    assert(td.find_char("'A'", ",", 0) == -1)
    assert(td.find_char("'\\u3FA1', 2", ",", 0) == 8)
    assert(td.find_char('\n\t 123, ', ",", 0) == 6)
    assert(td.find_char('Class(1, 2)("1,3"), 123', ",", 0) == 18)
    assert(td.find_char("1, 2, 34, 5", ",", 5) == 8)
