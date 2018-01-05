#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2017 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2017-10-22.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
from helpfileerror import HelpFileError

# Section types: Text, Define, Header, Source, Options, ErrorText
class Section:
    def __init__(self, sectionType, parameter, file_name, line_number):
        self.type = sectionType
        self.parameter = parameter
        self.file_name = file_name
        self.line_number = line_number
        self.lines = []

    def __str__(self):
        if self.parameter:
            return "%(type)s %(parameter)s (%(file_name)s:%(line_number)d)" % self.__dict__
        else:
            return "%(type)s (%(file_name)s:%(line_number)d)" % self.__dict__


def parse_section_header(line):
    words = line.split(None, 1)
    if len(words) == 0:
        raise HelpFileError("Empty section header")
    sectionType = words[0].lower()
    if sectionType == "set":
        return sectionType, words[1]
    elif sectionType in ("text", "source", "header", "settings", "errortext"):
        if len(words) == 1:
            return sectionType, None
        else:
            raise HelpFileError("Incorrect section header: %s" % line)
    else:
        raise HelpFileError("Unknown section header: %s" % sectionType)


def read_sections(file_name, syntax):
    sections = []
    for i, line in enumerate(open(file_name)):
        if i == 0 and line.startswith("#!"):
            continue
        if line.startswith(syntax.section_prefix):
            text = line[len(syntax.section_prefix):].strip()
            try:
                sectionType, parameter = parse_section_header(text)
                if sectionType in ("source", "header"):
                    parameter = sectionType.upper()
                    sectionType = "set"
                sections.append(Section(sectionType, parameter,
                                        file_name, i + 1))
            except HelpFileError as ex:
                ex.file_name = file_name
                ex.line_number = i + 1
                raise
        else:
            if not sections:
                sections.append(Section("text", None, file_name, i + 1))
            sections[-1].lines.append(line)
    return sections


def read_all_sections(fileNames, syntax):
    sections = []
    for file_name in fileNames:
        print(file_name)
        sections.extend(read_sections(file_name, syntax))
    return sections


if __name__ == "__main__":
    import sys
    from helpfilesyntax import HelpFileSyntax

    def main(args):
        syntax = HelpFileSyntax()
        sections = []
        for file_name in fileNames:
            print(file_name)
            sections.extend(read_sections(file_name, syntax))
        for section in sections:
            print(section)
        return 0

    sys.exit(main(sys.argv[1:]))
