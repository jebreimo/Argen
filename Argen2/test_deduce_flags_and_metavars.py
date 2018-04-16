# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-04-15.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import deduce_flags_and_metavars as dfam


def test_find_end_of_flag():
    assert dfam.find_end_of_flag("-a,/a", 0) == 2
    assert dfam.find_end_of_flag("-a, /a", 0) == 2
    assert dfam.find_end_of_flag("--abra-ham -a", 0) == 10
    assert dfam.find_end_of_flag("-a=N", 0) == 2
    assert dfam.find_end_of_flag("--a=N", 0) == 3
    assert dfam.find_end_of_flag("-=, --=", 0) == 2
    assert dfam.find_end_of_flag("--=, -=", 0) == 3


def test_get_flags_and_arguments():
    assert dfam.get_flags_and_arguments("-a N") == (["-a"], "N")
    assert dfam.get_flags_and_arguments("/a N") == (["/a"], "N")
    assert dfam.get_flags_and_arguments("-a,--a") == (["-a", "--a"], None)
    assert dfam.get_flags_and_arguments("-a, --a") == (["-a", "--a"], None)
    assert dfam.get_flags_and_arguments("-a --a") == (["-a", "--a"], None)
    assert dfam.get_flags_and_arguments("--a N") == (["--a"], "N")
    assert dfam.get_flags_and_arguments("--a=N") == (["--a"], "N")
    assert dfam.get_flags_and_arguments("--a=<M N O>") == (["--a"], "<M N O>")
    assert dfam.get_flags_and_arguments("-a M,N --a M,N") == (["-a", "--a"], "M,N")
    assert dfam.get_flags_and_arguments("-a M N, --a M N, --b Q R") == (["-a", "--a", "--b"], "M N")
    assert dfam.get_flags_and_arguments("-a, --a M N") == (["-a", "--a"], "M N")
    assert dfam.get_flags_and_arguments("[FILE ...]") == ([], "[FILE ...]")
