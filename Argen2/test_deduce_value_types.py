# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-06-05.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import deduce_value_types as dvt
import deducedtype as dt
import logger


def test_deduce_type_from_values_part():
    log = logger.Logger()
    typ = dvt.deduce_type_from_values_part([("-10", "20")], log)
    assert typ.category == dt.Category.NUMBER

    typ = dvt.deduce_type_from_values_part([("-10", "20.5")], log)
    assert typ.category == dt.Category.REAL

    typ = dvt.deduce_type_from_values_part(
        [("Foo(2)", "Foo(2)"), ("Foo(3)", "Foo(3)"), ("Foo(5)", "Foo(5)")], log)
    assert typ.explicit == "Foo"

    typ = dvt.deduce_type_from_values_part([
        ("{1, 2, \"g\"}", "{1, 2, \"g\"}"),
        ("{3, 4.0f, \"h\"}", "{3, 4.0f, \"h\"}")], log)
    assert typ.category == dt.Category.COMPOSITE
    assert len(typ.subtypes) == 3
    assert typ.subtypes[0].category == dt.Category.NUMBER
    assert typ.subtypes[1].specific == "float"
    assert typ.subtypes[2].category == dt.Category.STRING


def test_deduce_type_from_values():
    log = logger.Logger()
    typ = dvt.deduce_type_from_valid_values([[("0", "10"), ("99", "99")],
                                             [("'a'", "'a'"), ("'b'", "'b'")],
                                             [("1UL", "1UL"), ("5", "5")]], log)
    assert typ.category == dt.Category.COMPOSITE
    assert len(typ.subtypes) == 3
    assert typ.subtypes[0].category == dt.Category.NUMBER
    assert typ.subtypes[1].specific == "char"
    assert typ.subtypes[2].specific == "unsigned long"
