# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-12-23.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import parse_help_text
import helpfilesyntax


def test_parse_argument():
    syntax = helpfilesyntax.HelpFileSyntax()
    arg = parse_help_text.parse_argument("-t --test | Value: 3 | Count: 2...",
                                         syntax)
    assert arg.text == "-t --test "
    assert arg.given_properties["value"] == "3"
    assert arg.given_properties["count"] == "2..."
