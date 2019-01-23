# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-04-15.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


def has_help_flags(flags):
    if not flags:
        return False
    for flag in flags:
        if flag.lower() not in ["-h", "--help", "/?"]:
            return False
    return True


def find_best_help_options(arguments):
    candidates = {"callback": [], "flag": [], "type": []}
    for arg in arguments:
        if not arg.flags:
            continue
        elif arg.callback == "show_help":
            candidates["callback"].append(arg)
        elif arg.callback:
            continue
        elif arg.argument_type == "help":
            candidates["type"].append(arg)
        elif arg.argument_type != "normal":
            continue
        elif arg.callback is None and has_help_flags(arg.flags):
            candidates["flag"].append(arg)
    if candidates["type"]:
        return candidates["type"]
    if candidates["callback"]:
        return candidates["callback"]
    best_candidates = []
    for arg in candidates["flag"]:
        if (("--help" in arg.flags) or ("/?" in arg.flags)) \
                and (arg.post_operation in (None, "abort")):
            best_candidates.append(arg)
    return best_candidates or candidates["flag"]


def deduce_help_option(session):
    for arg in find_best_help_options(session.arguments):
        if arg.callback != "show_help":
            arg.callback = "show_help"
            session.logger.debug("Deduced callback: %s." % arg.callback,
                                 argument=arg)
        if arg.post_operation is None:
            arg.post_operation = "abort"
            session.logger.debug("Deduced post-operation: %s."
                                 % arg.post_operation, argument=arg)
        if arg.argument_type == "normal":
            arg.argument_type = "help"
            session.logger.debug("Deduced argument-type: %s."
                                 % arg.argument_type, argument=arg)


def looks_like_final_option(arg):
    if arg.argument_type == "final":
        return True
    if arg.argument_type != "normal":
        return False
    if not arg.flags or arg.flags[0] != "--" or len(arg.flags) != 1:
        return False
    return arg.operation in (None, "none")


def deduce_final_option(session):
    for arg in session.arguments:
        if looks_like_final_option(arg):
            if arg.argument_type == "normal":
                session.logger.debug("Deduced argument-type: final.",
                                     argument=arg)
            arg.argument_type = "final"
            if arg.member_name is None:
                arg.member_name = ""
            if arg.post_operation != "final":
                arg.post_operation = "final"
                session.logger.debug("Deduced post-operation: final.",
                                     argument=arg)


def deduce_special_options(session):
    deduce_help_option(session)
    deduce_final_option(session)
