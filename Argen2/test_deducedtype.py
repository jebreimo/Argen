# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-03-07.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import deducedtype as dt


def test_get_int_type():
    assert dt.get_int_type("0").category == dt.Category.NUMBER
    assert dt.get_int_type("10L").specific == "long"
    assert dt.get_int_type("10Lu").specific == "unsigned long"
    assert dt.get_int_type("10Ull").specific == "unsigned long long"
    assert dt.get_int_type("0x56").category == dt.Category.INTEGER
    assert dt.get_int_type("-0x56").category == dt.Category.INTEGER
    assert dt.get_int_type("-0x56ll").specific == "long long"
    assert dt.get_int_type("0078").category == dt.Category.INTEGER
    assert dt.get_int_type("0B10101").category == dt.Category.INTEGER
    assert dt.get_int_type("B10101") is None
    assert dt.get_int_type("-B10101") is None
    assert dt.get_int_type("-10'000'000").category == dt.Category.NUMBER
    assert dt.get_int_type("10'000'000u").specific == "unsigned"


def test_get_float_type():
    assert dt.get_float_type("123") is None
    assert dt.get_float_type("123.1").category == dt.Category.REAL
    assert dt.get_float_type("123.").category == dt.Category.REAL
    assert dt.get_float_type("123.e+3").category == dt.Category.REAL
    assert dt.get_float_type("123E-3").category == dt.Category.REAL
    assert dt.get_float_type("123'456.1").category == dt.Category.REAL
    assert dt.get_float_type("123.1e10").category == dt.Category.REAL
    assert dt.get_float_type("123.1f").specific == "float"
    assert dt.get_float_type("123.1e3L").specific == "long double"
    assert dt.get_float_type("123.1e+") is None
    assert dt.get_float_type(".1") is None


def test_get_class_name_parenthesis():
    assert dt.get_class_name_parenthesis("foo(23, 56)").explicit == "foo"
    assert dt.get_class_name_parenthesis("{foo(23, 56}") is None
    assert dt.get_class_name_parenthesis("(const Foo::Object*)nullptr").explicit == "const Foo::Object*"
    assert dt.get_class_name_parenthesis("(12 + 13)") is None
    assert dt.get_class_name_parenthesis("(12 + 13) * 14") is None


def test_get_class_name_braces():
    assert dt.get_class_name_braces("std::vector<int>{1, 2, 3}").explicit == "std::vector<int>"


def test_get_value_type():
    assert dt.get_value_type('"foo"').category == dt.Category.STRING
    assert dt.get_value_type("'\x0A'").specific == "char"
    assert dt.get_value_type("12'345'678").category == dt.Category.NUMBER
    assert dt.get_value_type("12'345.678").category == dt.Category.REAL
    assert dt.get_value_type("INT32_MIN").specific == "int32_t"
    assert dt.get_value_type("std::vector<int>()").explicit == "std::vector<int>"
    typ = dt.get_value_type('{"ABC", UINT64_MAX}')
    assert typ.category == dt.Category.COMPOSITE
    assert len(typ.subtypes) == 2
    assert typ.subtypes[0].category == dt.Category.STRING
    assert typ.subtypes[1].specific == "uint64_t"
