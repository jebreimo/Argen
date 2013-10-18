from argument import Argument
import constants
from error import Error
#from member import Member
import properties
import utilities

ArgCounter = 0
OptCounter = 0
StartDefinition = "${"
EndDefinition = "}$"
DefinitionSeparator = "|"

class ParserResult:
    def __init__(self, text, args, members, argLineNos):
        self.text = text
        self.options = [a for a in args if a.flags]
        self.arguments = [a for a in args if not a.flags]
        self.members = members
        self.definitionLineNos = argLineNos

########################
## PARSING THE HELP TEXT
########################

def isOption(s):
    return s and len(s) >= 2 and s[0] in "-/" and not s[1].isspace()

def variableName(s):
    return "_".join(utilities.translateToSpace(
                        s, "'!\"#$%&/()=?+*@.:,;<>^`-[]{}").split())

def variableNameFromFlags(flags):
    name = ""
    for flag in flags:
        if flag in ("/?", "-?"):
            return "help"
        elif flag == "--":
            return "end_of_options"
        else:
            newName = variableName(flag)
            if not name:
                name = newName
            elif len(name) <= 1 and len(newName) > 1:
                name = newName
    if not name:
        global OptCounter
        name = "option_" + str(OptCounter)
    return name

def parseFlags(text):
    flags = []
    argName = None
    prevWasFlag = False
    for word in text.split():
        if word[-1] == ",":
            word = word[:-1]
        if word[0] in "-/":
            index = word.find("=")
            if index in (-1, 1) or word[:3] == "--=":
                flag, arg = word, None
                prevWasFlag = True
            elif len(word) >= 2:
                flag, arg = word[:index], word[index + 1:] or "VALUE"
                prevWasFlag = False
            else:
                raise Error("Invalid option: " + word)
        elif prevWasFlag:
            prevWasFlag = False
            flag, arg = None, word
        else:
            raise Error("Invalid option: " + word)

        if flag:
            flags.append(flag)
        if arg:
            argName = arg
    return flags, argName

def isLegalFlag(f):
    if 1 <= len(f) <= 2:
        return True
    elif len(f) > 2 and f[0] in "-/" and "=" in f:
        return False
    else:
        return f

def findSingle(s, sub, start = 0):
    """findSingle(s, sub[, start]) -> int

       Returns the index of the first instance of sub in s which isn't
       immediately followed by another instance of sub. The search starts at
       start.
    """
    index = s.find(sub, start)
    while index != -1:
        nextStart = index + len(sub)
        while s[nextStart:nextStart + len(sub)] == sub:
            nextStart += len(sub)
        if (nextStart == index + len(sub)):
            return index
        index = s.find(sub, nextStart)
    return index

def splitSingle(s, separator, maxCount=-1):
    """
    splitSingle(s, separator[, maxCount]) -> list of strings

    Essentially performs the same operation as
    s.split(separator, maxCount), but sequences of separators are
    left alone (e.g. the C++ logical or-operator "||" is not considered a
    separator when separator is "|").
    """
    result = []
    start = 0
    next = findSingle(s, separator)
    while next != -1 and maxCount != 0:
        result.append(s[start:next])
        start = next + len(separator)
        next = findSingle(s, separator, start)
        maxCount -= 1
    result.append(s[start:])
    return result

def parseProperties(s):
    parts = [p.strip() for p in splitSingle(s, DefinitionSeparator)]
    props = dict((k.strip().lower(), v.strip())
                  for k, v in (s.split(":", 1) for s in parts))
    if "flags" in props:
        flags = props["flags"].split()
        for f in flags:
            if not isLegalFlag(f):
                raise Error("\"%s\" is an illegal flag (it contains =)" % f)
    if "type" in props:
        props["type"] = props["type"].lower()
        if props["type"] not in constants.LegalTypeValues:
            raise Error("%(type)s is an illegal value for the type property" %
                        props)
    return props

def parseArg(s):
    global ArgCounter
    if s:
        props = dict(argument=s, visible=True)
    else:
        props = dict(argument="arg %d" % ArgCounter, visible=False)
    props["member"] = variableName(props["argument"])
    props["name"] = props["member"]
    props["autoindex"] = str(ArgCounter)
    ArgCounter += 1
    if s:
        if s[0] == "[":
            if s.endswith("...") or s.endswith("...]"):
                props["count"] = "0.."
            else:
                props["count"] = "0..1"
        elif s.endswith("..."):
            props["count"] = "1.."
        else:
            props["count"] = "1"
    return props

def parseOption(s):
    global OptCounter
    flags, argument = parseFlags(s)
    name = variableNameFromFlags(flags)
    props = dict(flags=" ".join(flags),
                 member=name,
                 name=name,
                 visible=True)
    if argument:
        props["argument"] = argument
    OptCounter += 1
    return props

def parseFlagsProperty(flags):
    global OptCounter
    name = variableNameFromFlags(flags.split())
    OptCounter += 1
    return dict(member=name,
                name=name)

def parseDefinition(s):
    parts = splitSingle(s, DefinitionSeparator, 1)
    text = parts[0]
    if len(parts) == 2:
        explicitProps = parseProperties(parts[1])
    else:
        explicitProps = {}
    for key in explicitProps:
        if key not in constants.LegalProps:
            raise Error("Unknown property name: " + key)
    stripped = explicitProps.get("text", text).strip()
    if "flags" in explicitProps:
        props = parseFlagsProperty(explicitProps["flags"])
    elif isOption(stripped):
        props = parseOption(stripped)
    else:
        props = parseArg(stripped)
    props.update(explicitProps)
    properties.inferArgumentProperties(props)
    if "index" in props and "flags" in props:
        raise Error("Options can't have the index property.")
    return text, props

def findDefinition(s, index=0):
    start = s.find(StartDefinition, index)
    if start == -1:
        return None
    end = s.find(EndDefinition, start + 2)
    if end == -1:
        return start, len(s), s[start + 2:]
    else:
        return start, end + 2, s[start + 2:end]

def appendText(lst, s):
    if s:
        lst.append(s)
    return s.count("\n")

def isStartOfLine(textList):
    for s in reversed(textList):
        i = s.rfind("\n")
        if i != -1:
            return i + 1 == len(s) or s[i + 1:].isspace()
        elif not s.isspace():
            return False
    return True

def parseText(text):
    outText = []
    argProps = []
    argLineNos = set()
    prv = (0, 0, None)
    cur = findDefinition(text)
    lineNo = 1
    skippedNewlines = 0
    while cur:
        lineNo += appendText(outText, text[prv[1]:cur[0]])
        if StartDefinition in cur[2]:
            raise Error("Definition seems to be missing a closing \"%s\""
                        % EndDefinition, lineNo)
        try:
            txt, props = parseDefinition(cur[2])
            props["lineno"] = str(lineNo)
        except Error as ex:
            ex.lineNo = str(lineNo)
            raise ex
        if txt and isStartOfLine(outText):
            argLineNos.add(lineNo - skippedNewlines - 1)
        if ((not txt) and
                (not outText or outText[-1][-1] == "\n") and
                (cur[1] != len(text) and text[cur[1]] == "\n")):
            lineNo += 1
            skippedNewlines += 1
            cur = cur[0], cur[1] + 1, cur[2]
        appendText(outText, txt)
        lineNo += cur[2].count("\n")
        argProps.append(props)
        prv = cur
        cur = findDefinition(text, cur[1])
    appendText(outText, text[prv[1]:])
    return "".join(outText), argProps, argLineNos

def parseFile(fileName):
    try:
        text, argProps, argLineNos = parseText(open(fileName).read())
        properties.inferIndexProperties(argProps)
        args = [Argument(p) for p in argProps]
        members = properties.makeMembers(args)
        for m in members:
            if m.type == "help":
                for a in m.arguments:
                    if not a.flags:
                        raise Error("Only options can be of type \"help\".",
                                    a.lineNo)
                break
        else:
            raise Error("There is no help-option. Use property "
                        "\"type: help\" to indicate the help-option.")
        return ParserResult(text, args, members, argLineNos)
    except Error as ex:
        ex.fileName = fileName
        raise ex

if __name__ == "__main__":
    import sys

    def test(lines, args, s):
        try:
            txt, argProps, argLines = parseText(s)
            properties.inferIndexProperties(argProps)
            arg = [Argument(p) for p in argProps]
            args.extend(arg)
            lines.append(txt)
        except Error as ex:
            print(ex)

    def main(args):
        args = []
        lines = []
        # test(lines, args, "${<file1>}$")
        # test(lines, args, "${<file2 ...>}$")
        # test(lines, args, "${[file3]}$")
        # test(lines, args, "${[file4 ...]}$")
        # test(lines, args, "${knut VALUE, finn VALUE|flags: knut finn|argument: VALUE}$")
        # test(lines, args, "${-s TEXT| count: ..10}$\n${--special| member: s | value: \"$spec$\"}$")
        # test(lines, args, "${-h,      --help        }$  Show help.")
        # test(lines, args, "${-o,      --outfile=FILE}$  Output file for logging info.")
        # test(lines, args, "${-o FILE, --outfile=FILE}$  Output file for logging info.")
        # test(lines, args, "${-p,      --point=X,Y,Z | Default: 0.0}$  Set the point.")
        # test(lines, args, "${-i PATH, --include=PATH| delimiter: :}$  Set paths to include.")
        # test(lines, args, "With${| Text: --top-secret}$\nnewline")
        # test(lines, args, "${| Text: --secret}$\nNo newline")
        test(lines, args, "${--                     }$  End of options, remainder are arguments.")
        # test(lines, args, "${YYYY-MM-DD| delimiter: - | Member: date}$")
        # test(lines, args, "${HH:MM:SS| delimiter: : | Member: time}$")
        # test(lines, args, "${<Kid yoU not>|index:3}$")
        # test(lines, args, "${}$")
        # test(lines, args, "${-a                     | text: -a -A -all}$  All of them")
        # test(lines, args, "Kjell\n${|Text:--foo=N}$${|Text:--bar=N}$\nKaare")
        # test(lines, args, "[OPTIONS]\n\t${-b}$\n\t${-c}$\n\t${-d}$")
        # test(lines, args, "${-e=N| values: [0.0..5.0)}$  All of them")
        # test(lines, args, "${-a --bah|flags: foot ball}$  Odd options")
        print("\n".join(lines))
        for arg in args:
            print(arg, arg.props)
        try:
            members = properties.makeMembers(args)
            for m in members:
                print(m)
        except Error as ex:
            print(str(ex))
        return 0

    sys.exit(main(sys.argv[1:]))
