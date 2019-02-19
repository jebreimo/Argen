#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2019 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2019-02-19.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import sys
from test_utilities import run_tests

COMMAND = "immediate_callback_tuple"

TESTS = [
    {
        "returncode": 0,
        "stdout": b"""\
parse_arguments_result: 0
outer: *
inner: -
"""
    },
    {
        "arguments": ["-h"],
        "returncode": 0,
        "stdout": b"""\
USAGE
  immediate_callback_tuple [-h] [-o CHAR] [-i CHAR] <NUM,NUM> ...

ARGUMENTS
  <NUM,NUM> ...         One or more tuples of integers.

OPTIONS
  -h, --help            Show help.
  -o CHAR, --outer=CHAR The outer characters.
  -i CHAR, --inner=CHAR The inner characters.

"""
    },
    {
        "arguments": ["3,5", "-o", "#", "5,8", "-o$",
                      "-iM", "8,13", "--outer", "%", "13,21"],
        "returncode": 0,
        "stdout": b"""\
***-----***
#####--------#####
$$$$$$$$MMMMMMMMMMMMM$$$$$$$$
%%%%%%%%%%%%%MMMMMMMMMMMMMMMMMMMMM%%%%%%%%%%%%%
parse_arguments_result: 0
NUM_NUM[0]: (3, 5)
NUM_NUM[1]: (5, 8)
NUM_NUM[2]: (8, 13)
NUM_NUM[3]: (13, 21)
outer: %
inner: M
"""
    }]

sys.exit(run_tests(COMMAND, TESTS))
