ArgCounter = 0
OptCounter = 0

ArgumentProps = ["argument", "count", "delimiter", "delimitercount", "flags",
                 "index", "member", "text", "value"]
MemberProps = ["default", "type", "values", "valuetype"]
LegalTypeValues = ["final", "help", "info", "list", "multivalue", "value"]
LegalProps = ArgumentProps + MemberProps

class Error(Exception):
    def __init__(self, msg, lineNo="", fileName=""):
        Exception.__init__(self, msg)
        self.lineNo = lineNo
        self.fileName = fileName

    def formattedMsg(self):
        msg = Exception.__str__(self)
        if self.lineNo:
            return "%s[%s] Error: %s" % (self.fileName, self.lineNo, msg)
        elif self.fileName:
            return "%s Error: %s" % (self.fileName, msg)
        else:
            return "Error: " + msg

    def __str__(self):
        return self.formattedMsg()

class Argument(object):
    """This class represents an option or argument to be handled by the
       generated argument parser function.
    """
    def __init__(self, props):
        self.props = dict((k, props[k]) for k in props if k not in MemberProps)
        self.flags = props["flags"].split() if "flags" in props else []
        self.value = props.get("value")
        self.member = None
        self.memberName = props["member"]
        self.memberProps = dict((k, props[k])
                                for k in MemberProps if k in props)
        self.index = int(props["index"]) if "index" in props else None
        self.name = props["name"]
        self.delimiter = props.get("delimiter", "")
        self.delimiterCount = parseCount(props.get("delimitercount", "0"))
        self.minDelimiters, self.maxDelimiters = self.delimiterCount
        self.count = parseCount(props["count"])
        self.minCount, self.maxCount = self.count
        self.lineNo = props["lineno"]

    def __getitem__(self, key):
        return self.__getattribute__(key)

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.flags:
            return "option(%s)" % " ".join(self.flags)
        else:
            return "argument(%s)" % self.memberName

    #def inferMemberCount(self):
    #    if self.maxDelimiters == -1 or self.count[1] == -1:
    #        _max = -1
    #    else:
    #        _max = self.count[1] * (self.maxDelimiters + 1)
    #    return self.count[0], _max

class Member(object):
    """This class represents a member variable in the struct that is
       returned by the generated argument parser function.
    """
    def __init__(self, props):
        self.default = props["default"]
        self.props = props
        self.arguments = props["arguments"]
        self.name = props["name"]
        self.values = parseValues(props.get("values", ""))
        self.valueType = props["valuetype"]
        self.count = parseCount(props["count"])
        self.minCount, self.maxCount = self.count
        # self.valueCount = parseCount["valueCount"]
        self.type = props.get("type")
        if not self.type:
            self.type = "value" if self.maxCount == 1 else "list"
        if self.type in ("list", "multivalue"):
            self.memberType = "std::vector<%s>" % self.valueType
        else:
            self.memberType = self.valueType
        self.isOption = not any(a for a in self.arguments if not a.flags)

    def __getitem__(self, key):
        return self.__getattribute__(key)

    def __str__(self):
        return "%s %s;" % (self.memberType, self.name)

    @property
    def lineNo(self):
        return ", ".join(a.lineNo for a in self.arguments)

    @property
    def flags(self):
        flags = []
        for a in self.arguments:
            flags.extend(a.flags)
        return ", ".join(flags)

class ParserResult:
    def __init__(self, text, args, members, argLineNos):
        self.text = text
        self.options = [a for a in args if a.flags]
        self.arguments = [a for a in args if not a.flags]
        self.members = members
        self.definitionLineNos = argLineNos

def updateProperties(props, other):
    for key in other:
        if key not in props:
            props[key] = other[key]
        elif props[key] != other[key]:
            raise Error(
                    "Multiple definitions of property %s: \"%s\" and \"%s\"" %
                    (key, props[key], other[key]))

def translateToSpace(s, chars):
    # Slow (but not noticably so in this context) replacement for maketrans
    # and translate. I couldn't find a way to use maketrans and translate that
    # worked under both python2 and python3
    if chars not in translateToSpace.transforms:
        translateToSpace.transforms[chars] = set(c for c in chars)
    transform = translateToSpace.transforms[chars]
    return "".join(" " if c in transform else c for c in s)
translateToSpace.transforms = {}

def maxCount(a, b):
    return -1 if -1 in (a, b) else max(a, b)

def getValueType(s):
    if s in ("true", "false"):
        return "bool"
    elif len(s) > 1 and s[0] == '"' and s[-1] == '"':
        return "std::string"
    try:
        int(s)
        return "int"
    except ValueError:
        pass
    try:
        float(s)
        return "double"
    except ValueError:
        pass
    return ""

def parseCount(s):
    parts = s.split("..")
    if len(parts) == 1:
        return int(s), int(s)
    elif len(parts) != 2:
        raise Error("Invalid count: " + s)
    else:
        count = (int(parts[0]) if parts[0] else 0,
                 int(parts[1]) if parts[1] else -1)
        if count[1] != -1 and count[1] < count[0]:
            raise Error("Invalid range: \"%s\"" % s)
        return count

def parseValues(s):
    values = []
    for value in s.split():
        c = value.count('"')
        if ((c not in (0, 2)) or
            ((c == 2) and (value[0] != '"' or value[-1] != '"'))):
            raise Error("values contains invalud string: \"" + value + "\"")
        minmax = value.split("..", 1)
        if len(minmax) == 2:
            s, e = minmax
            if not s:
                sCmp = ""
            elif s[0] != "(":
                sCmp = "ge"
            else:
                sCmp = "g"
            if s and s[0] in "[(":
                s = s[1:]
            if not e:
                eCmp = ""
            elif e[0] != ")":
                eCmp = "le"
            else:
                eCmp = "l"
            if e and e[-1] in "])":
                e = e[:-1]
            if s or e:
                values.append((s, e, sCmp, eCmp))
        else:
            values.append((value, value, "e", "e"))
    return values

def inferValueType(props):
    vals = []
    if "default" in props:
        vals.append(props["default"].split("|")[0])
    if "values" in props:
        vals.extend(translateToSpace(props["values"].replace("..", " "),
                                     "[]()").split())
    vals.extend(a.value for a in props["arguments"] if a.value)
    if not vals:
        return "std::string"
    types = set(v for v in [getValueType(s) for s in vals] if v)
    if len(types) == 1:
        return list(types)[0]
    elif len(types) == 2 and "int" in types and "double" in types:
        return "double"
    elif types:
        raise Error("%s: unable to infer correct value type, can be any of %s."
                    % (props["name"], ", ".join(types)),
                    ", ".join(a.lineNo for a in props["arguments"]))
    else:
        raise Error("%s: unable to infer correct value type. "
                    "(String values must be enclosed by quotes, e.g. \"foo\")"
                    % (props["name"]),
                    ", ".join(a.lineNo for a in props["arguments"]))
inferValueType.trans = {ord(x): ord(" ") for x in "[]()"}

def inferIndexProperties(propsList):
    propsWithIndex = [p for p in propsList if "autoindex" in p]
    propsWithIndex.sort(key=lambda p: int(p["autoindex"]))
    indexedProps = [None] * len(propsWithIndex)
    for props in propsWithIndex:
        if "index" in props:
            try:
                i = int(props["index"])
            except ValueError:
                raise Error("Invalid index property: %(index)s" % props,
                            props["lineno"])
            if 0 > i or i >= len(indexedProps):
                raise Error("Index is too large, it is %d, maximum is %d."
                            % (i, len(indexedProps) - 1), props["lineno"])
            elif indexedProps[i]:
                raise Error("Two arguments can't have the same index.",
                            indexedProps[i]["lineno"] + ", " + props["lineno"])
    i = 0
    for p in propsWithIndex:
        if "index" not in props:
            while indexedProps[i]:
                i += 1
            p["index"] = str(i)
            i += 1

def inferDefaultValue(props):
    value = ""
    if "values" in props:
        value = parseValues(props["values"])[0][0]
    elif props["valuetype"] == "bool":
        value = "false"
    elif props["valuetype"] != "std::string":
        value = "0"
    if props["type"] == "multivalue":
        count = min(a.minDelimiters for a in props["arguments"])
        value = "|".join([value] * count)
    return value

def minmaxCount(counts):
    mi, ma = 0, 0
    for c in counts:
        if c[1] == -1:
            ma = -1
        elif ma != -1:
            ma = max(c[1], ma)
        mi = min(c[0], mi)
    return mi, ma

def inferMemberProperties(props):
    args = props["arguments"]

    minDel, maxDel = minmaxCount(a.delimiterCount for a in args)
    if args[0].flags:
        counts = list(set(a.count for a in args))
        if len(counts) == 1:
            count = counts[0]
        elif len(counts) == 2 and (0, 1) in counts:
            count = counts[1] if counts[0] == (0, 1) else counts[0]
        else:
            raise Error("%(name)s: conflicting count properties. "
                        "Options writing to the same member must have "
                        "the same count." % props)
    else:
        count = (0, 0)
        for lo, hi in (a.count for a in args):
            if count[1] == -1:
                hi = -1
            elif hi != -1:
                hi += count[1]
            lo += count[0]
            count = lo, hi
    if count[1] == -1 or maxDel == -1:
        props["count"] = "%d..-1" % (count[0] * (minDel + 1))
    else:
        props["count"] = "%d..%d" % (count[0] * (minDel + 1),
                                     count[1] * (maxDel + 1))
    #if "type" not in props and propC[1] != 1 and propC[1] != infC[1]:
    #        props["type"] = "list"
    if "valuetype" not in props:
        props["valuetype"] = inferValueType(props)
    if "type" not in props:
        if (props["valuetype"] == "bool" and count == (0, 1) and
                not [a for a in args if not a.flags]):
            if props["name"] == "help":
                props["type"] = "help"
            elif props["name"] == "end_of_options":
                props["type"] = "final"
            else:
                props["type"] = "value"
        elif count[1] != 1 or maxDel == -1:
            props["type"] = "list"
        elif maxDel == 0:
            props["type"] = "value"
        elif minDel == maxDel:
            props["type"] = "multivalue"
        else:
            for lo, hi in (a.delimiterCount for a in args):
                if lo != hi:
                    props["type"] = "list"
                    break
            else:
                props["type"] = "multivalue"
    elif props["type"] == "multivalue":
        for lo, hi in (a.delimiterCount for a in args):
            if lo != hi:
                raise Error("%(name)s: type \"multivalue\" requires a "
                            "fixed number of delimiters.")
        for a in args:
            if a.minDelimiters != a.maxDelimiters:
                raise Error("%(name)s: type \"multivalue\" requires a "
                            "fixed number of delimiters.")
    elif props["type"] != "list" and count[1] != 1:
        raise Error('%(name)s: type must be "list" or "multivalue" when '
                    'the maximum count is greater than 1.' % props)
    elif props["type"] in ("help", "info", "final"):
        if props["valuetype"] != "bool":
            raise Error("%(name)s: when type is \"%(type)s\", valuetype "
                        "must be bool, not %(valuetype)s." % props)
        elif any(a for a in args if not a.flags):
            raise Error("only options can have type \"%(type)s\"." % props)
        elif "values" in props:
            raise Error("options of type \"%(type)s\" cant have "
                        "the \"values\" property." % props)
    if "default" not in props:
        props["default"] = inferDefaultValue(props)
    elif props["default"] and props["type"] == "list":
        raise Error("There can't be a default value when type is \"list\".")

def getMemberProperties(args):
    members = {}
    for arg in args:
        name = arg.memberName
        if name in members:
            memargs = members[name]["arguments"]
            memargs.append(arg)
            if (len(arg.flags) != 0) != (len(memargs[0].flags) != 0):
                lineNos = ", ".join(a.lineNo for a in memargs)
                raise Error(name + ": arguments and options can't write to "
                            "the same member. (Use the \"member\" propery to "
                            "set a different member name)", lineNos)
            try:
                updateProperties(members[name], arg.memberProps)
            except Error as e:
                lineNos = ", ".join(a.lineNo for a in memargs)
                raise Error(name + ": " + str(e), lineNos)
        else:
            members[name] = arg.memberProps.copy()
            members[name]["arguments"] = [arg]
            members[name]["name"] = name
    return members

def inferArgumentProperties(props):
    if not props.get("flags", " "):
        raise Error("Flags property can't be empty.")
    if "flags" not in props and "value" in props:
        raise Error("Arguments can't have the value property.")
    if "argument" in props and "value" in props:
        raise Error("An option can't have both argument and value properties.")
    if not props.get("argument", props.get("flags")):
        props["argument"] = "VALUE"
    if not props.get("value", " "):
        raise Error("Value property can't be empty.")
    if "value" not in props and "argument" not in props:
        props["value"] = "true"
    if "delimiter" not in props:
        s = props.get("value") or props.get("argument", "")
        if "," in s:
            props["delimiter"] = ","
    if len(props.get("delimiter", " ")) != 1:
        msg = "Delimiter must be a single non-whitespace character."
        if "," in props.get("value") or props.get("argument", ""):
            msg += " Use \"DelimiterCount: 0\" to disable the comma-delimiter."
        raise Error(msg)
    if "delimiter" not in props and props.get("delimitercount", "0") != "0":
        raise Error("DelimiterCount property where there is no delimiter.")
    if "delimiter" in props and "delimitercount" not in props:
        s = props.get("value") or props.get("argument", "")
        n = s.count(props["delimiter"])
        if n != 0:
            props["delimitercount"] = str(n)
        else:
            props["delimitercount"] = "0.."
    if "value" in props and "delimiter" in props:
        props["value"] = "|".join(props["value"].split(props["delimiter"]))
    if "type" in props:
        props["type"] = props["type"].lower()
        if props["type"] in ("help", "info", "final"):
            if "value" not in props:
                raise Error("Options of type %(type)s can't take an argument." % props)
            elif props["value"] != "true":
                raise Error("Options of type %(type)s must have \"true\" as its value." % props)
    if "default" in props and "delimiter" in props:
        count = parseCount(props["delimitercount"])
        defvals = props["default"].split(props["delimiter"], count[1])
        if len(defvals) > 1 and count[0] <= len(defvals) <= count[1]:
            raise Error("Default has too few delimited values (expects %d)." %
                        count[0])
        elif len(defvals) == 1 and count[0] > 1:
            defvals = defvals * count[0]
        props["default"] = "|".join(defvals)
    if "count" not in props:
        props["count"] = "0..1" if "flags" in props else "1"
    else:
        c = parseCount(props["count"])
        if c[0] < 0:
            raise Error("Min-count can't be less than 0.")
        elif c[1] == 0:
            raise Error("Max-count can't be 0.")
    if props.get("valuetype") == "string":
        props["valuetype"] = "std::string"

def makeMembers(args):
    """makeMembers(list of Argument instances) -> list of Member instances

    Create Member instances based on the memberName- and memberProps-members
    of the Argument instances in args.
    """
    members = {}
    props = getMemberProperties(args)
    for key in props:
        try:
            inferMemberProperties(props[key])
            members[key] = Member(props[key])
        except Error as ex:
            ex.lineNo = ", ".join(a.lineNo for a in props[key]["arguments"])
            raise ex
    for arg in args:
        arg.member = members[arg.memberName]
    return sorted(members.values(), key=lambda m: m.name)

def ensureUniqueNames(args):
    names = set()
    for a in args:
        if a.name in names:
            name = a.name
            i = 1
            while name in names:
                name = a.name + str(i)
            a.name = name
        names.add(a.name)

########################
## PARSING THE HELP TEXT
########################

def isOption(s):
    return s and len(s) >= 2 and s[0] in "-/" and not s[1].isspace()

def variableName(s):
    return "_".join(translateToSpace(s, "'!\"#$%&/()=?+*@.:,;<>^`-[]{}").split())

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
    for word in text.replace(", ", " ").split():
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

def parseProperties(s):
    parts = [p.strip() for p in s.split("|")]
    props = dict((k.strip().lower(), v.strip())
                  for k, v in (s.split(":", 1) for s in parts))
    if "flags" in props:
        flags = props["flags"].split()
        for f in flags:
            if not isLegalFlag(f):
                raise Error("\"%s\" is an illegal flag (it contains =)" % f)
    if "type" in props:
        props["type"] = props["type"].lower()
        if props["type"] not in LegalTypeValues:
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
    parts = s.split("|", 1)
    text = parts[0]
    if len(parts) == 2:
        explicitProps = parseProperties(parts[1])
    else:
        explicitProps = {}
    for key in explicitProps:
        if key not in LegalProps:
            raise Error("Unknown property name: " + key)
    stripped = explicitProps.get("text", text).strip()
    if "flags" in explicitProps:
        props = parseFlagsProperty(explicitProps["flags"])
    elif isOption(stripped):
        props = parseOption(stripped)
    else:
        props = parseArg(stripped)
    props.update(explicitProps)
    inferArgumentProperties(props)
    if "index" in props and "flags" in props:
        raise Error("Options can't have the index property.")
    return text, props

def findDefinition(s, index=0):
    start = s.find("${", index)
    if start == -1:
        return None
    end = s.find("}$", start + 2)
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
        if "${" in cur[2]:
            raise Error("Definition seems to be missing a closing \"}$\"",
                        lineNo)
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
        inferIndexProperties(argProps)
        args = [Argument(p) for p in argProps]
        members = makeMembers(args)
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
            inferIndexProperties(argProps)
            args = [Argument(p) for p in argProps]
            args.extend(arg)
            lines.append(txt)
        except Error as ex:
            print(ex)

    def main(args):
        args = []
        lines = []
        test(lines, args, "${-s TEXT| count: ..10}$\n${--special| member: s | value: \"$spec$\"}$")
        test(lines, args, "${-h,      --help        }$  Show help.")
        test(lines, args, "${-o,      --outfile=FILE}$  Output file for logging info.")
        test(lines, args, "${-o FILE, --outfile=FILE}$  Output file for logging info.")
        test(lines, args, "${-p,      --point=X,Y,Z | Default: 0.0}$  Set the point.")
        test(lines, args, "${-i PATH, --include=PATH| delimiter: :}$  Set paths to include.")
        test(lines, args, "With${| Text: --top-secret}$\nnewline")
        test(lines, args, "${| Text: --secret}$\nNo newline")
        test(lines, args, "${--                     }$  End of options, remainder are arguments.")
        test(lines, args, "${YYYY-MM-DD| delimiter: - | Member: date}$")
        test(lines, args, "${HH:MM:SS| delimiter: : | Member: time}$")
        test(lines, args, "${<Kid yoU not>|index:3}$")
        test(lines, args, "${}$")
        test(lines, args, "${-a                     | text: -a -A -all}$  All of them")
        test(lines, args, "Kjell\n${|Text:--foo=N}$${|Text:--bar=N}$\nKaare")
        test(lines, args, "[OPTIONS]\n\t${-b}$\n\t${-c}$\n\t${-d}$")
        test(lines, args, "${-e=N| values: [0.0..5.0)}$  All of them")
        test(lines, args, "${-a --bah|flags: foot ball}$  Odd options")
        print("\n".join(lines))
        for arg in args:
            print(arg, arg.props)
        try:
            members = makeMembers(args)
            for m in members:
                print(m)
        except Error as ex:
            print(str(ex))
        return 0

    sys.exit(main(sys.argv[1:]))
