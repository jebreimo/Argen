# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-04-15.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


def has_help_flags(flags):
    for flag in flags:
        if flag.lower() not in ["-h", "--help", "/?"]:
            return False
    return True


def deduce_help_option(arguments):
    candidates = []
    for arg in arguments:
        if arg.callback == "show_help":
            return arg, None
        elif arg.callback is None and has_help_flags(arg.flags):
            candidates.append(arg)
    best_candidates = []
    if len(candidates) > 1:
        for arg in candidates:
            if (("--help" in arg.flags) or ("/?" in arg.flags)) \
                    and (arg.post_operation in (None, "abort")):
                best_candidates.append(arg)
        if best_candidates:
            candidates = best_candidates
    for arg in candidates:
        arg.callback = "show_help"
        if arg.post_operation is None:
            arg.post_operation = "abort"
    return candidates, None
