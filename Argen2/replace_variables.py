# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-11-25.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
from helpfileerror import HelpFileError


def find_variable(text, startPos, syntax):
    start = text.find(syntax.variable_start, startPos)
    if start < 0:
        return None
    end = text.find(syntax.variable_end, start + len(syntax.variable_start))
    if end < 0:
        raise HelpFileError("Invalid variable.")
    return start, end + len(syntax.variable_end)


def replace_variables(text, session):
    syntax = session.syntax
    output = []
    pos = 0
    while True:
        var = find_variable(text, pos, syntax)
        if not var:
            break
        nameStart = var[0] + len(syntax.variable_start)
        nameEnd = var[1] - len(syntax.variable_end)
        name = text[nameStart:nameEnd]
        if name in session.syntax.internal_variables:
            pass
        elif name in session.variables:
            output.append(text[pos:var[0]])
            output.append(session.variables[name])
        else:
            raise HelpFileError("Undefined variable: %s" % name)
        pos = var[1]
    if not output:
        return text
    output.append(text[pos:])
    return "".join(output)
