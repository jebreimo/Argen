# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-06-13.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


def deduce_values(session):
    for arg in session.arguments:
        if arg.value or arg.metavar or not arg.member:
            continue
        if (not arg.value_type
                or arg.value_type.explicit == "bool") \
            and (not arg.member.member_type
                 or arg.member.member_type.explicit == "bool"):
            arg.value = "true"
            session.logger.debug("Deduced value: %s." % arg.value,
                                 argument=arg)
        else:
            session.logger.error("Unable to deduce the option's value.",
                                 argument=arg)
