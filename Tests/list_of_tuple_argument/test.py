#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2019 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2019-01-27.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import os
import subprocess
import sys

COMMAND = "list_of_tuple_argument"


def check_value(cmd, test, value_key, default_value, actual_value):
    expected_value = test.get(value_key, default_value)
    if actual_value != expected_value:
        texts = (f"Test failed! Incorrect {value_key}\n",
                 f"""  Command: {"".join(cmd)}\n""",
                 f"  Expected value: {str(expected_value)}\n",
                 f"  Actual value: {str(actual_value)}\n")
        for text in texts:
            sys.stderr.write(text)
        return False
    return True


def main():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    exe_path = os.path.join(script_dir, "../bin", COMMAND)
    for test in TESTS:
        cmd = [exe_path]
        if test.get("arguments"):
            cmd.extend(test["arguments"])
        result = subprocess.run(cmd, capture_output=True)
        if not check_value(cmd, test, "returncode", 0, result.returncode) \
                or not check_value(cmd, test, "stdout", b"", result.stdout) \
                or not check_value(cmd, test, "stderr", b"", result.stderr):
            return 1
    print(COMMAND + ": all tests passed.")
    return 0


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

sys.exit(main())
