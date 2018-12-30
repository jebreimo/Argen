# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-12-29.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


def deduce_count(session):
    for arg in session.arguments:
        if not arg.count and not arg.flags:
            if arg.operation == "assign":
                arg.count = 1, 1
            elif arg.operation in ("append", "extend"):
                arg.count = 1, None
            if arg.count:
                session.logger.debug("Deduced count for %s: %s"
                                     % (arg, str(arg.count)), argument=arg)
