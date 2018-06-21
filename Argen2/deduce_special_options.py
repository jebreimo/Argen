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


def deduce_help_option(session):
    candidates = []
    for arg in session.arguments:
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
            session.logger.debug("Deduced callback: %s and post-operation: %s."
                                 % (arg.callback, arg.post_operation),
                                 argument=arg)
        else:
            session.logger.debug("Deduced callback: %s." % arg.callback,
                                 argument=arg)


def looks_like_final_option(arg):
    if not arg.flags or arg.flags[0] != "--" or len(arg.flags) != 1:
        return False
    if not arg.properties:
        return True
    if len(arg.properties) != 1 or "operation" not in arg.properties:
        return False
    return arg.properties["operation"] == "none"


def deduce_final_option(session):
    for arg in session.arguments:
        if looks_like_final_option(arg):
            arg.post_operation = "final"
            arg.member_name = ""
            session.logger.debug("Deduced final option.", argument=arg)


def deduce_special_options(session):
    deduce_help_option(session)
    deduce_final_option(session)

