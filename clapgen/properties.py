from error import Error
from member import Member
import utilities

def updateProperties(props, other):
    for key in other:
        if key not in props:
            props[key] = other[key]
        elif props[key] != other[key]:
            raise Error(
                    "Multiple definitions of property %s: \"%s\" and \"%s\"" %
                    (key, props[key], other[key]))

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

def inferValueType(props):
    vals = []
    if "default" in props:
        vals.append(props["default"].split("|")[0])
    if "values" in props:
        vals.extend(utilities.translateToSpace(
                props["values"].replace("..", " "),
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
        vals = utilities.parseValues(props["values"])
        print(vals)
        if vals and vals[0][2] == "le":
            value = utilities.parseValues(props["values"])[0][0]
    if not value:
        if props["valuetype"] == "bool":
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
    elif props["default"] and count[0] != 0:
        raise Error("%(name)s: can't have default value when minimum count "
                    "is non-zero." % props)

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
                raise Error("Options of type %(type)s can't take an argument."
                            % props)
            elif props["value"] != "true":
                raise Error('Options of type %(type)s must have value "true".'
                            % props)
    if "default" in props and "delimiter" in props:
        count = utilities.parseCount(props["delimitercount"])
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
        c = utilities.parseCount(props["count"])
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
