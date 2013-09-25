"""
    Name: Command Line Argument Parser Generator

    CLAPG

    CLARPAGE
    CLAParse
    CoLiArPaGe
    CLAPGen

    New option syntax:

    <options> [| key: value [| key: value ...]]

    Where key is one of:
        Count: either a single integer or two integers separated by two dots
            (i.e. min..max). The default for options is 0..1 and for arguments
            it is 1.
            If the maximum isn't 1 the type automatically becomes a list
            If the maximum is 0 there is no upper bound for how many values
            the option accepts.
        Default: the default value for the variable
        Delimiter: a single character (e.g. comma) used to separate values in
            a list
        DelimiterCount: 0..2 3..
        Flags
        Index
        Member: the name of the member variable
        Name: the name of the value that will be used in error messages and
            also the name of the member unless "member" is also specified
            (any characters in the name that are illegal in member names are
             replaced with underscores).
        OptionType: ignored if set, it's always deduced from other parameters
            Value
            Argument
            DelimitedValue
            DelimitedArgument
        Text: overide the auto-generated text for the argument or option
        Type:
            Help
            Info
            MultiValue
            Value
            List    values are stored in a vector
            Final   the option marks the end of all options, all remaining
                    arguments are treated as arguments even if they start with
                    a dash. POSIX-compliant program should make "--" the
                    final option. There won't be a members for final options in
                    the Arguments struct.
        # Text: overide the auto-generated text for the argument or option
        Value: the value that will be assigned (or appended) to the variable
            if the flag is given.
        Values: the legal values for the argument or option. The same set of
            legal values applies to all values when "type" is "list" or
            "multi-value".
        ValueType: must be one of:
            # int int8_t int16_t int32_t int64_t
            # unsigned uint8_t uint16_t uint32_t uint64_t
            # float double
            String
        Visible: set to False if the option or argument shouldn't be shown
            in the help text

This is actually a language consisting of the following constructs:

Members:
    (count) - from delimiterCount
    default - from valueType
    maxCount - from count or maxDelimiters
    memberType - from count, valueType
    minCount - from count or minDelimiters
    name - from member
    type - from flag or count
    values
    valueType - from default, values, option-value, option/argument

Options:
    (argument) - from text
    delimiter - from argument or value
    (delimiterCount) - from delimiter
    flags - from text
    maxDelimiters - from delimiterCount
    member - from flags
    minDelimiters - from delimiterCount
    (text)
    value - from flags (true)
    (visible) - from text

Arguments:
    (argument) - from text
    delimiter - from text
    delimiterCount - from delimiter and text
    index
    member - from text
    (text)
    (visible) - from text
"""
import argparse
import os.path
import sys
import textwrap
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
    ap.add_argument("-w", "--width", metavar="N", type=int,
                    dest="width", default=79,
                    help='line width for word wrapping (default is 79)')
    ap.add_argument("-i", "--indent", metavar="N", type=int,
                    dest="indent", default=-1,
                    help="indentation width when option help text is word-wrapped")
    ap.add_argument("-c", "--class", metavar="NAME",
                    dest="className", default="ParseArguments",
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
    ap.add_argument("--ns", metavar="NAME",
                    dest="namespace", default="",
                    help="the namespace of the generated functions and classes")
    ap.add_argument("--func", metavar="NAME",
                    dest="functionName", default="parse_arguments",
                    help="the name of the generated function (default is parse_arguments)")
    ap.add_argument("--list",
                    dest="listProperties", action="store_const",
                    const=True, default=False,
                    help="list the parser result without generating files")
    ap.add_argument("--test",
                    dest="includeTest", action="store_const",
                    const=True, default=False,
                    help="don't include test code at the end of the cpp file")
    ap.add_argument("helpfile", metavar="text file",
                    help="a text file containing the help text")
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
        parserResult = helptextparser.parseFile(args.helpfile)
    except helptextparser.Error as ex:
        print(ex)
        return 2
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
        argparser_cpp.createFile(args.fileName + "." + args.cpp,
                                 text,
                                 parserResult.options,
                                 parserResult.arguments,
                                 parserResult.members,
                                 className=args.className,
                                 functionName=args.functionName,
                                 namespace=args.namespace,
                                 headerFileName=os.path.basename(hppFile),
                                 includeTest=args.includeTest)
    except Exception as ex:
        print("Error: " + str(ex))
        raise
        return 3
    # argparser_generator.crateSourceFile("CommandLine.cpp", helpText)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
