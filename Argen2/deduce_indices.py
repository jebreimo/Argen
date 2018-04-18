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


def find_conflicting_indices(arguments):
    conflicts = []
    taken_indices = {}
    for arg in arguments:
        if arg.index is not None:
            if taken_indices.get(arg.index):
                conflicts.append(dict(
                    message="Two arguments have the same index, %i." % arg.index,
                    arguments=[arg, taken_indices[arg.index]]))
            else:
                taken_indices[arg.index] = arg
    return conflicts


def deduce_indices(arguments):
    conflicts = find_conflicting_indices(arguments)
    if conflicts:
        return [], conflicts

    actual_arguments = [a for a in arguments if not a.flags]
    available_indices = set(range(len(actual_arguments)))
    for arg in actual_arguments:
        if arg.index is not None and arg.index in available_indices:
            available_indices.remove(arg.index)

    affected = []
    actual_arguments.sort(key=lambda a: a.auto_index)
    for arg in actual_arguments:
        if arg.index is None:
            arg.index = available_indices.pop()
            affected.append(arg)
    return affected, None
