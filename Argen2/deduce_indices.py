# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-04-17.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================


# def compare_indices(arg1, arg2):
#     index1 = arg1.index if arg1.index is not None else arg1.auto_index
#     index2 = arg2.index if arg2.index is not None else arg2.auto_index
#     if index1 != index2:
#         return index1 - index2
#     if arg1.index == arg2.index:
#         return 0
#     return -1 if arg1.index is not None else 1


def find_conflicting_indices(session):
    result = False
    taken_indices = {}
    for arg in session.arguments:
        if arg.index is not None:
            if taken_indices.get(arg.index):
                session.logger.error("Another argument has the same index, %i."
                                     % arg.index, argument=arg)
                session.logger.info("...the other argument is defined here.",
                                    argument=taken_indices[arg.index])
                result = True
            else:
                taken_indices[arg.index] = arg
    return result


def deduce_indices(session):
    if find_conflicting_indices(session):
        return

    actual_arguments = [a for a in session.arguments if not a.flags]
    available_indices = set(range(len(actual_arguments)))
    for arg in actual_arguments:
        if arg.index is not None and arg.index in available_indices:
            available_indices.remove(arg.index)

    actual_arguments.sort(key=lambda a: a.auto_index)
    for arg in actual_arguments:
        if arg.index is None:
            arg.index = available_indices.pop()
            session.logger.debug("Deduced index: %d." % arg.index,
                                 argument=arg)
