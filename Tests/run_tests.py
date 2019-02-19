#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2019 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2019-01-23.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import glob
import os
import pathlib
import subprocess
import sys

HELP_TEXT_FILE_NAMES = {"helptext.txt"}


def touch_helptext_files(root_dir):
    for file_path in glob.glob(os.path.join(root_dir, "*/*.txt")):
        if os.path.basename(file_path) in HELP_TEXT_FILE_NAMES:
            print(f"Touching {file_path}")
            pathlib.Path(file_path).touch()


def build(root_dir):
    build_dir = os.path.join(root_dir, "build")
    if not os.path.isdir(build_dir):
        os.mkdir(build_dir)
    os.chdir(build_dir)
    os.system("cmake ..")
    os.system("make")


def run_tests(root_dir):
    env = os.environ.copy()
    python_path = env.get("PYTHONPATH")
    script_dir = os.path.join(root_dir, "scripts")
    if not python_path:
        python_path = script_dir
    else:
        python_path += os.pathsep + script_dir
    env["PYTHONPATH"] = python_path
    for file_path in glob.glob(os.path.join(root_dir, "*/test.py")):
        test_name = os.path.basename(os.path.dirname(file_path))
        print(f"Testing {test_name}.")
        subprocess.run([file_path], stdout=sys.stdout, stderr=sys.stderr,
                       env=env)


def main(args):
    root_dir = os.path.dirname(os.path.realpath(__file__))
    if len(args) == 1 and args[0] in ("-r", "--rebuild"):
        touch_helptext_files(root_dir)
    elif args:
        print("Usage: %s [-r or --rebuild]" % sys.argv[0])
        return 1
    build(root_dir)
    run_tests(root_dir)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
