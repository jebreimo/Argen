#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2019 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2019-01-27.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import sys
from test_utilities import run_tests


COMMAND = "list_of_tuple_argument"

TESTS = [
    {
        "returncode": 1,
        "stderr": b"""\
usage: list_of_tuple_argument  <x,y,z> ... <x,y,z>

Incorrect number of arguments. Requires 2 or more, received 0.
"""
    },
    {
        "arguments": ["foo"],
        "returncode": 1,
        "stderr": b"""\
usage: list_of_tuple_argument  <x,y,z> ... <x,y,z>

Incorrect number of arguments. Requires 2 or more, received 1.
"""
    },
    {
        "arguments": ["foo", "bar"],
        "returncode": 1,
        "stderr": b"""\
usage: list_of_tuple_argument  <x,y,z> ... <x,y,z>

<x,y,z> ... <x,y,z>: incorrect number of parts in value "foo".
It must have exactly 3 parts separated by ,'s.
"""
    },
    {
        "arguments": ["2,3,5", "4,5.5,6"],
        "returncode": 0,
        "stdout": b"""\
parse_arguments_result: 0
points[0]: (2, 3, 5)
points[1]: (4, 5.5, 6)
"""
    },
    {
        "arguments": ["2,3,5", "4,5.5,6", "5,7,12"],
        "returncode": 0,
        "stdout": b"""\
parse_arguments_result: 0
points[0]: (2, 3, 5)
points[1]: (4, 5.5, 6)
points[2]: (5, 7, 12)
"""
    }
]

sys.exit(run_tests(COMMAND, TESTS))
