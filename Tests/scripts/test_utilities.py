# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2019 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2019-02-19.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import os
import subprocess
import sys


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


def run_tests(exe_name, tests):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    exe_path = os.path.join(script_dir, "../bin", exe_name)
    for test in tests:
        cmd = [exe_path]
        if test.get("arguments"):
            cmd.extend(test["arguments"])
        result = subprocess.run(cmd, capture_output=True)
        if not check_value(cmd, test, "returncode", 0, result.returncode) \
                or not check_value(cmd, test, "stdout", b"", result.stdout) \
                or not check_value(cmd, test, "stderr", b"", result.stderr):
            return 1
    print(exe_name + ": all tests passed.")
    return 0


def foo():
    print("foo")
