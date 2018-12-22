# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-12-07.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import argument


def deduce_member_count(session):
    def is_count(c): return c and (c[0] or c[1])
    for arg in session.arguments:
        if arg.member \
                and len(arg.member.arguments) == 1 \
                and arg.member.size is None \
                and is_count(arg.count) \
                and arg.operation in ("append", "extend"):
            arg.member.size = arg.count
            session.logger.debug("Deduced size: %s" % str(arg.member.size),
                                 argument=arg)
