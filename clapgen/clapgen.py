#!/usr/bin/env python
"""
    clapgen - Command Line Argument Parser GENerator
"""
import argparse
import os
import sys
import textwrap

from error import Error
import helptextparser
import argparser_hpp
import argparser_cpp

def find_first(s, func):
    for i, c in enumerate(s):
        if func(c):
            return i
    return -1

def formatText(text, definitionLineNos, width, definitionIndent):
    result = []
    wrapper = textwrap.TextWrapper(width=width)
    for i, line in enumerate(text.split("\n")):
        line = line.rstrip()
        if len(line) <= width:
            result.append(line)
        else:
            if i in definitionLineNos:
                indent = definitionIndent
            else:
                indent = find_first(line, lambda c: not c.isspace())
                if indent == -1:
                    indent = 0
            wrapper.subsequent_indent = " " * indent
            result.extend(wrapper.wrap(line))
    return "\n".join(result)

def makeArgParser():
    ap = argparse.ArgumentParser(description='Process some integers.')
    ap.add_argument("helpfile", metavar="text file",
                    help="a text file containing the help text")
    ap.add_argument("-i", "--indent", metavar="N", type=int,
                    dest="indent", default=-1,
                    help="indentation width when option help text is word-wrapped")
    ap.add_argument("-c", "--class", metavar="NAME",
                    dest="className", default="Arguments",
                    help="the name of the generated class")
    ap.add_argument("-f", "--file", metavar="NAME",
                    dest="fileName", default="ParseArguments",
                    help="the file name (without extension) of the generated files")
    ap.add_argument("--cpp", metavar="CPP",
                    dest="cpp", default="cpp",
                    help="the extension of the generated implementation file (default is cpp)")
    ap.add_argument("--hpp", metavar="HPP",
                    dest="hpp", default="h",
                    help="the extension of the generated header file (default is h)")
    ap.add_argument("--function", metavar="NAME",
                    dest="functionName", default="parse_arguments",
                    help="the name of the generated function (default is parse_arguments)")
    ap.add_argument("--namespace", metavar="NAME",
                    dest="namespace", default="",
                    help="the namespace of the generated functions and classes")
    ap.add_argument("--parenthesis", metavar="PARENS",
                    dest="parenthesis", default="",
                    help="Set the parenthesis used to enclose the "
                         "definitions and separate properties from each "
                         "other in the help file. (Defalut is \"${ | }$\"")
    ap.add_argument("--test",
                    dest="includeTest", action="store_const",
                    const=True, default=False,
                    help="Include a main-function the source file")
    ap.add_argument("--width", metavar="N", type=int,
                    dest="width", default=79,
                    help='line width for help text word wrapping (default is 79)')
    ap.add_argument("--debug",
                    dest="listProperties", action="store_const",
                    const=True, default=False,
                    help="list the parser result without generating files")
    return ap


def inferIndentation(line):
    gaps = []
    start = -1
    for i, c in enumerate(line):
        if c.isspace():
            if start == -1:
                start = i
        elif start != -1:
            if i - start > 1:
                gaps.append((i - start, start))
            start = -1
    if start != -1:
        gaps.append((len(line) - start, start))
    if not gaps:
        return 0
    gaps.sort()
    return gaps[-1][0] + gaps[-1][1]

def inferOptionIndentation(text, lineNos):
    lines = text.split("\n")
    widths = {}
    for lineNo in lineNos:
        width = inferIndentation(lines[lineNo])
        if width in widths:
            widths[width] += 1
        else:
            widths[width] = 1
    n, width = 0, 0
    for key in widths:
        if widths[key] > n or widths[key] == n and key > width:
            n, width = widths[key], key
    return width

def main(args):
    try:
        args = makeArgParser().parse_args()
    except argparse.ArgumentError:
        return 1
    try:
        if args.parenthesis:
            parens = args.parenthesis.split()
            if len(parens) == 3 and parens[0] and parens[1] and parens[2]:
                helptextparser.StartDefinition = parens[0]
                helptextparser.DefinitionSeparator = parens[1]
                helptextparser.EndDefinition = parens[2]
            else:
                print("Invalid parenthesis: " + args.parenthesis)
                print("The parenthesis string must consist of the opening "
                      " parenthesis (defaults is \"${\"), the property "
                      " separator (default is \"|\") and the closing "
                      " parenthesis (default is \"}$\")separated by a space "
                      " character. The space character must either be "
                      " escaped or the entire option must be enclosed in "
                      " quotes. For instance to produce the default "
                      " perenthesis: \"--parenthesis=${ }$\".")
                return 1
        parserResult = helptextparser.parseFile(args.helpfile)
    except IOError as ex:
        print(ex)
        return 2
    except Error as ex:
        print(ex)
        return 3
    if args.indent != -1:
        indentation = args.indent
    else:
        indentation = inferOptionIndentation(parserResult.text,
                                             parserResult.definitionLineNos)
    text = formatText(parserResult.text,
                      parserResult.definitionLineNos,
                      args.width,
                      indentation)
    if args.listProperties:
        print("")
        print("Options")
        print("=======")
        for o in parserResult.options:
            print(o.props)
        print("")
        print("Arguments")
        print("=========")
        for a in parserResult.arguments:
            print(a.props)
        print("")
        print("Members")
        print("=======")
        for m in parserResult.members:
            print(m.props)
        print("")
        print("Help text")
        print("=========")
        print(text)
        return 0
    try:
        hppFile = args.fileName + "." + args.hpp
        argparser_hpp.createFile(hppFile,
                                 parserResult.members,
                                 className=args.className,
                                 functionName=args.functionName,
                                 namespace=args.namespace)
        cppFile = args.fileName + "." + args.cpp
        argparser_cpp.createFile(cppFile,
                                 text,
                                 parserResult.options,
                                 parserResult.arguments,
                                 parserResult.members,
                                 className=args.className,
                                 functionName=args.functionName,
                                 namespace=args.namespace,
                                 headerFileName=os.path.basename(hppFile),
                                 includeTest=args.includeTest)
        print("%s: generated %s and %s"
              % (os.path.basename(sys.argv[0]), hppFile, cppFile))
    except Exception as ex:
        print("Error: " + str(ex))
        raise
        return 3
    # argparser_generator.crateSourceFile("CommandLine.cpp", helpText)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
