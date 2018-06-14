# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-06-13.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


def deduce_values(arguments):
    conflicts = []
    affected = []
    for arg in arguments:
        if arg.value or arg.metavar or not arg.member:
            continue
        if (not arg.member.value_type
                or arg.member.value_type.explicit == "bool") \
            and (not arg.member.member_type
                 or arg.member.member_type.explicit == "bool"):
            arg.value = "true"
            affected.append(arg)
        else:
            conflicts.append("Error")
    return affected
