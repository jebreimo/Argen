# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-06-23.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import os.path
import re
from replace_variables import replace_variables


class CodeProperties:
    def __init__(self):
        self.header_includes = None
        self.source_includes = None
        self.source_file_name = ""
        self.source_file_path = ""
        self.header_file_name = ""
        self.header_file_path = ""
        self.class_name = None
        self.parse_function_name = None
        self.expose_helptext_functions = None
        self.has_short_options = None
        self.shortest_option_length = 0
        self.case_sensitive_flags = False
        self.abbreviated_options = True
        self.non_short_options = True
        self.special_options = True
        self.header_template = None
        self.source_template = None
        self.tracked_members = None
        self.namespace_start = None
        self.namespace_end = None


def get_internal_variables(session):
    internals = {
        "HEADER_CONTENTS": "${HEADER_INCLUDES}\n\n${HEADER_CODE}",
        "SOURCE_CONTENTS": "${SOURCE_INCLUDES}\n\n${SOURCE_CODE}",
        "HEADER_INCLUDES": "[[[header_includes]]]",
        "SOURCE_INCLUDES": "[[[source_includes]]]",
        "HEADER_CODE": "[[[header_code]]]",
        "SOURCE_CODE": "[[[source_code]]]",
        "HEADER": "#pragma once\n${HEADER_CONTENTS}",
        "SOURCE": "${SOURCE_CONTENTS}",
        "PROGRAM": "[[[program_name]]]",
        "HEADER_NAME": "[[[header_file_name]]]",
        "SOURCE_NAME": "[[[source_file_name]]]",
        "OPTIONS": "[[[options]]]",
        "ARGUMENTS": "[[[arguments]]]",
        "ERROR": ""
    }
    for key in internals:
        if key in session.variables:
            internals[key] = session.variables[key]
    return internals


def has_strings(session):
    pass


def _replace_variables(text, session, internal_variables):
    prev_text = None
    while text != prev_text:
        prev_text = text
        text = replace_variables(text, session, internal_variables)
    return text


def get_header_file_name(settings):
    return settings.file_name + settings.header_extension


def get_header_file_path(session):
    name = session.get_header_file_name()
    if session.settings.header_dir_name:
        name = os.path.join(session.settings.header_dir_name, name)
    return name


def get_source_file_name(session):
    name = session.settings.file_name + session.settings.source_extension
    if session.settings.source_dir_name:
        name = os.path.join(session.settings.source_dir_name,
                            session.settings.file_name)
    return name


INCLUDE_FILES_REXPS = {
    r"\btuple\b": "<tuple>",
    r"\bu?int(?:8|16|32|64)_t\b": "<cstdint>",
    r"\bvector\b": "<vector>",
    r"\bw?string\b": "<string>"
}


def get_header_includes(session):
    includes = {"<iosfwd>"}
    rexps = {k: re.compile(k) for k in INCLUDE_FILES_REXPS}
    for mem in session.members:
        t = str(mem.member_type)
        for rexp_key in rexps:
            if rexps[rexp_key].search(t):
                includes.add(INCLUDE_FILES_REXPS[rexp_key])
    return sorted(includes)


def get_counted_members(session):
    has_count = lambda a, b: a or b
    return [m for m in session.members
            if m.count and has_count(*m.count) and m.is_option()]


def make_code_properties(session):
    settings = session.settings

    result = CodeProperties()

    name = settings.file_name + settings.header_extension
    result.header_file_name = name
    if session.settings.header_dir_name:
        name = os.path.join(settings.header_dir_name, name)
    result.header_file_path = name

    name = settings.file_name + settings.header_extension
    result.header_file_name = name
    if session.settings.header_dir_name:
        name = os.path.join(settings.header_dir_name, name)
    result.header_file_path = name

    internal_variables = get_internal_variables(session)
    result.header_template = _replace_variables(
        internal_variables["HEADER"], session, internal_variables)
    result.source_template = _replace_variables(
        internal_variables["SOURCE"], session, internal_variables)

    result.header_includes = get_header_includes(session)
    result.counted_members = get_counted_members(session)

    if session.settings.namespace:
        ns = " { namespace ".join(session.settings.namespace)
        result.namespace_start = ["namespace " + ns, "{"]
        result.namespace_end = "}" * len(session.settings.namespace)
    return result
