# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-03-07.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import type_deduction as td
import helpfilesyntax as hfs


def test_get_int_type():
    assert td.get_int_type("0").type_name == "number"
    assert td.get_int_type("10L").type_name == "long"
    assert td.get_int_type("10Lu").type_name == "unsigned long"
    assert td.get_int_type("10Ull").type_name == "unsigned long long"
    assert td.get_int_type("0x56").type_name == "integer"
    assert td.get_int_type("-0x56").type_name == "integer"
    assert td.get_int_type("-0x56ll").type_name == "long long"
    assert td.get_int_type("0078").type_name == "integer"
    assert td.get_int_type("0B10101").type_name == "integer"
    assert td.get_int_type("B10101") is None
    assert td.get_int_type("-B10101") is None
    assert td.get_int_type("-10'000'000").type_name == "number"
    assert td.get_int_type("10'000'000u").type_name == "unsigned"


def test_get_float_type():
    assert td.get_float_type("123") is None
    assert td.get_float_type("123.1").type_name == "real"
    assert td.get_float_type("123.").type_name == "real"
    assert td.get_float_type("123.e+3").type_name == "real"
    assert td.get_float_type("123E-3").type_name == "real"
    assert td.get_float_type("123'456.1").type_name == "real"
    assert td.get_float_type("123.1e10").type_name == "real"
    assert td.get_float_type("123.1f").type_name == "float"
    assert td.get_float_type("123.1e3L").type_name == "long double"
    assert td.get_float_type("123.1e+") is None
    assert td.get_float_type(".1") is None


def test_get_class_name_parenthesis():
    assert td.get_class_name_parenthesis("foo(23, 56)").type_name == "foo"
    assert td.get_class_name_parenthesis("{foo(23, 56}") is None
    assert td.get_class_name_parenthesis("(const Foo::Object*)nullptr").type_name == "const Foo::Object*"
    assert td.get_class_name_parenthesis("(12 + 13)") is None
    assert td.get_class_name_parenthesis("(12 + 13) * 14") is None


def test_get_class_name_braces():
    assert td.get_class_name_braces("std::vector<int>{1, 2, 3}").type_name == "std::vector<int>"


def test_get_value_type():
    assert td.get_value_type('"foo"').type_name == "string"
    assert td.get_value_type("'\x0A'").type_name == "char"
    assert td.get_value_type("12'345'678").type_name == "number"
    assert td.get_value_type("12'345.678").type_name == "real"
    assert td.get_value_type("INT32_MIN").type_name == "int32_t"
    assert td.get_value_type("std::vector<int>()").type_name == "std::vector<int>"
    typ = td.get_value_type('{"ABC", UINT64_MAX}')
    assert len(typ.subtypes) == 2
    assert typ.subtypes[0].type_name == "string"
    assert typ.subtypes[1].type_name == "uint64_t"


def test_deduce_type_from_values_part():
    syntax = hfs.HelpFileSyntax()
    assert td.deduce_type_from_values_part("-10..20", syntax).type_name == "number"
    assert td.deduce_type_from_values_part("-10..20.5", syntax).type_name == "real"
    assert td.deduce_type_from_values_part("Foo(2), Foo(3), Foo(5)", syntax).type_name == "Foo"
    typ = td.deduce_type_from_values_part("{1, 2, \"g\"}, {3, 4.0f, \"h\"}", syntax)
    assert typ.confidence == td.DeducedType.COMPOSITE
    assert len(typ.subtypes) == 3
    assert typ.subtypes[0].type_name == "number"
    assert typ.subtypes[1].type_name == "float"
    assert typ.subtypes[2].type_name == "string"


def test_deduce_type_from_values():
    syntax = hfs.HelpFileSyntax()
    typ = td.deduce_type_from_values("0..10, 99 $ 'a', 'b' $ 1UL, 5", syntax)
    assert typ.confidence == td.DeducedType.COMPOSITE
    assert len(typ.subtypes) == 3
    assert typ.type_name == "tuple"
    assert typ.subtypes[0].type_name == "number"
    assert typ.subtypes[1].type_name == "char"
    assert typ.subtypes[2].type_name == "unsigned long"
