import codegen
import os

def isMandatory(member):
    return member.isOption and member.minCount == 1 and member.type != "list"

def isDefaultList(member):
    return member.type == "list" and member.default

def isTrackable(member):
    return isMandatory(member) or isDefaultList(member)

class CppExpander(codegen.Expander):
    def __init__(self, text, opts, args, members, className="ParseArguments",
                 fileName="ParseArguments.cpp",
                 functionName="parseArguments", namespace="",
                 headerFileName="ParseArguments.hpp",
                 includeTest=True):
        codegen.Expander.__init__(self)
        self._options = sorted(opts, key=lambda o: o.name)
        self._args = args
        self._members = members
        self.headerFileName = headerFileName
        self.namespace = namespace.split("::") if namespace else []
        self.helpText = ['"%s\\n"' % s for s in
                         text.replace("\\", r"\\").replace('"', r'\"')
                             .split("\n")]
        self.hasShortOptions = self.__hasShortOptions()
        self.hasDashOptions = any(o for o in opts if
                                  any(f for f in o.flags
                                      if len(f) == 2 and f[0] == '-'))
        self.hasSlashOptions = any(o for o in opts if any(f for f in o.flags
                                                          if f[0] == '/'))
        if self.hasShortOptions:
            self.hasNormalOptions = any(o for o in opts if
                                        any(f for f in o.flags
                                            if len(f) > 2 and f[:2] == '--'))
        else:
            self.hasNormalOptions = any(o for o in opts if
                                        any(f for f in o.flags
                                            if len(f) > 1 and f[0] in "-/"))
        self.hasLongOptions = self.hasShortOptions and self.hasNormalOptions
        self.helpFlag = self.__helpFlag()
        self.className = className
        self.qualifiedClassName = namespace + "::" + className
        self.functionName = functionName
        self.qualifiedFunctionName = namespace + "::" + functionName
        self.hasTrackedOptions = any(m for m in members if isTrackable(m))
        self.hasMandatoryOptions = any(m for m in members if isMandatory(m))
        self.includeTest = includeTest
        self.memberWidth = min(20, max(len(m.name) + 1 for m in members))
        self.hasFinalOption = any(m for m in members if m.type == "final")
        self.hasDelimitedValues = any(m for m in members
                                      if m.type == "multivalue")
        self.hasMinimumListLengths = any(m for m in members if m.type == "list"
                                         and m.minCount != 0)
        self.minArguments, self.maxArguments = self.__argumentCount()
        self.hasMinArguments = self.minArguments != 0
        self.hasMaxArguments = self.maxArguments != -1
        self.hasFixedNumberOfArguments = self.minArguments == self.maxArguments
        self.hasValueWithCheck = any(o for o in opts
                        if not o.delimiter and o.member.values)
        self.hasValueWithoutCheck = any(o for o in opts
                        if not o.delimiter and not o.member.values)
        self.hasDelimitedValuesWithCheck = any(o for o in opts
                        if o.delimiter and o.member.values)
        self.hasDelimitedValuesWithoutCheck = any(o for o in opts
                        if o.delimiter and not o.member.values)
        self.hasInfoOptions = any(m for m in members if m.type == "info")

    def __argumentCount(self):
        minc, maxc = 0, 0
        for a in self._args:
            minc += a.minCount
            if a.maxCount == -1:
                maxc = -1
            elif maxc != -1:
                maxc += a.maxCount
        return minc, maxc

    def __hasMandatoryOptions(self):
        for m in self._members:
            if (m.isOption and m.type in ("value", "multivalue") and
                            m.minCount != 0):
                return True
        return False

    def __hasShortOptions(self):
        dashes = set()
        slashes = set()
        for o in self._options:
            for f in o.flags:
                if len(f) == 1:
                    return False
                elif len(f) == 2:
                    if f[0] == "-":
                        dashes.add(f[1])
                    elif f[0] == '/':
                        slashes.add(f[1])
                    else:
                        return False
                elif len(f) > 2 and f[:2] != "--":
                    return False
        return ((len(dashes) != 0 and len(slashes) == 0) or
                (len(dashes) == 0 and len(slashes) != 0) or
                (len(dashes) != 0 and dashes == slashes))

    def __helpFlag(self):
        for m in self._members:
            if m.type == "help":
                return m.arguments[0].flags[0]
        return ""

    def includeVector(self, params, context):
        for m in self._members:
            if m.type in ("list", "multivalue"):
                return False
        return True

    def includeString(self, params, context):
        for m in self._members:
            if m.valueType == "std::string":
                return False
        return True

    def beginNamespace(self, params, context):
        return "namespace " + " { namespace ".join(self.namespace) + " {"

    def endNamespace(self, params, context):
        return "}" * len(self.namespace)

    def memberInitializers(self, params, context):
        lines = []
        for m in self._members:
            if m.type in ("list", "multivalue") and m.minCount == 0:
                if m.default:
                    v = m.default.split("|")
                    if len(set(v)) == 1 and v[0]:
                        lines.append("%s(%d, %s)" % (m["name"], len(v), v[0]))
                    else:
                        lines.append("%s(%d)" % (m["name"], len(v)))
                else:
                    lines.append("%(name)s(%(maxCount)d)" % m)
            elif m.default and m.type not in  ("final", "list", "multivalue"):
                lines.append("%(name)s(%(default)s)" % m)
        for i in range(len(lines) - 1):
            lines[i] += ","
        return lines

    def multiValueInitialization(self, params, context):
        lines = []
        for m in self._members:
            if m.type not in ("list", "multivalue") or not m.default:
                continue
            v = m.default.split("|")
            if len(set(v)) > 1:
                for i in range(len(v)):
                    lines.append("%s[%d] = %s;" % (m["name"], i, v[i]))
        return lines

    def printMembers(self, params, context):
        lines = []
        for m in self._members:
            if m.type in ("list", "multivalue"):
                lines.append("PRINT_LIST(%(name)s);" % m)
            elif m.valueType == "std::string":
                lines.append("PRINT_STRING(%(name)s);" % m)
            elif m.type != "final":
                lines.append("PRINT_VALUE(%(name)s);" % m)
        lines.append("PRINT_VALUE(%s_result);" % self.functionName)
        return lines

    def implementOtionProcessors(self, params, context):
        lines = []
        processed = set()
        for o in self._options:
            m = o.member
            if m in processed:
                continue
            poe = ProcessOptionExpander(context, self, m, o)
            if m.type == "help":
                lines.extend(codegen.makeLines(processHelpOptionTemplate, poe))
                processed.add(m)
            elif m.type == "info":
                lines.extend(codegen.makeLines(processInfoOptionTemplate, poe))
                processed.add(m)
            elif m.type == "multivalue":
                lines.extend(codegen.makeLines(processMultivalueOptionTemplate, poe))
            elif m.type == "list" and o.delimiter:
                lines.extend(codegen.makeLines(processMultivalueListOptionTemplate, poe))
            elif m.type == "list":
                lines.extend(codegen.makeLines(processListOptionTemplate, poe))
            elif m.type != "final":
                lines.extend(codegen.makeLines(processOptionTemplate, poe))
        return lines

    def declareOptionProcessors(self, params, context):
        words = []
        for o in self._options:
            m = o.member
            if m.type in ("help", "info"):
                for f in o.flags:
                    words.append('OptionProcessor("%s", process_%s_option)' %
                                 (f, m.name))
            elif m.type not in ("final"):
                for f in o.flags:
                    words.append('OptionProcessor("%s", process_%s_option)' %
                                 (f, o.name))
            else:
                pass
        return codegen.join(words, 79 - context[1], ", ", ",")

    def checkFinalOption(self, params, context):
        words = []
        for m in self._members:
            if m.type == "final":
                for a in m.arguments:
                    for f in a.flags:
                        words.append("arg == \"%s\"" % f)
        return codegen.join(words, 79 - context[1], " || ", " ||")

    def checkListLengths(self, params, context):
        words = []
        for m in self._members:
            if m.isOption and m.type == "list" and m.minCount != 0:
                words.append("if (result.%(name)s.size() < %(minCount)d)" % m)
                words.append('    return error("%(flags)s", result, ' %m)
                words.append('                 "too few values (received " +' % m)
                words.append('                 '
                             'toString(result.%(name)s.size()) + '
                             '", requires %(minCount)d).");' % m)
        return words

    def implementArgumentProcessors(self, params, context):
        def isSimple(m):
            return m.valueType == "std::string" and not m.values
        lines = []
        for a in self._args:
            m = a.member
            poe = ProcessOptionExpander(context, self, m, a)
            if m.type == "multivalue" and (a.delimiter or not isSimple(a)):
                lines.extend(codegen.makeLines(processMultivalueArgumentTemplate, poe))
            elif m.type == "list" and a.delimiter:
                lines.extend(codegen.makeLines(processMultivalueListArgumentTemplate, poe))
            elif m.type == "list" and not isSimple(m):
                lines.extend(codegen.makeLines(processListArgumentTemplate, poe))
            elif not isSimple(m):
                lines.extend(codegen.makeLines(processArgumentTemplate, poe))
        return lines

    def __processArgument(self, arg):
        def isSimple(m):
            return m.valueType == "std::string" and not m.values
        lines = []
        a, m = arg, arg.member
        if m.type == "multivalue" and not a.delimiter and isSimple(m):
            lines.append("result->%s.clear();" % m.name)
            lines.append("result->%s.push_back(*it++);" % m.name)
        elif m.type == "list" and not a.delimiter and isSimple(m):
            lines.append("result->%s.push_back(*it++);" % m.name)
        elif m.type == "value" and isSimple(m):
            lines.append("result->%s = *it++;" % m.name)
        else:
            lines.append("if (!process_%s_argument(*it++, *result))"
                         % a.name)
            lines.append("    return result;")
        return lines

    def processArguments(self, params, context):
        lines = []
        for a in self._args:
            if a.minCount == 1:
                lines.extend(self.__processArgument(a))
            elif a.minCount > 1:
                lines.append("for (size_t i = 0; i != %(minCount)d; ++i)" % a)
                lines.append("{")
                lines.extend("    " + s for s in self.__processArgument(a))
                lines.append("}")

            if a.minCount != a.maxCount:
                if a.maxCount - a.minCount == 1:
                    lines.append("if (excess != 0)")
                else:
                    lines.append("for (size_t i = %d; excess && i < %d; ++i)"
                             % (a.minCount, a.maxCount))
                lines.append("{")
                lines.extend("    " + s for s in self.__processArgument(a))
                lines.extend(["    --excess;", "}"])
        return lines

    def initializeTrackedOptions(self, params, context):
        lines = []
        for m in self._members:
            if isTrackable(m):
                lines.append("%(name)s(false)" % m)
        return codegen.join(lines, 79 - context[1], ", ", ",")

    def trackedOptions(self, params, context):
        lines = []
        for m in self._members:
            if isTrackable(m):
                lines.append("bool %(name)s;" % m)
        return lines

    def mandatoryOptionChecks(self, params, context):
        lines = []
        for m in self._members:
            if isMandatory(m):
                lines.append("if (!result.reserved_for_internal_use->%(name)s)"
                             % m)
                lines.append('    return error("%(flags)s", result, '
                             '"missing mandatory option.");' % m)
        return lines

processMultivalueListOptionTemplate = """\
bool process_[[[name]]]_option([[[>]]]const std::string& flag,
[[[|]]]ArgumentIterator& argIt,
[[[|]]][[[className]]]& result[[[<]]])
{
[[[IF hasDefault]]]
    if (!result.reserved_for_internal_use->[[[memberName]]])
    {
        result.[[[memberName]]].clear();
        result.reserved_for_internal_use->[[[memberName]]] = true;
    }
[[[ENDIF]]]
[[[IF value]]]
    [[[multivalueValueAssignment]]]
[[[IF hasNormalOptions]]]
[[[IF hasShortOptions]]]
    if (!resemblesShortOption(flag.c_str()) && argIt.hasValue())
[[[ELSE]]]
    if (argIt.hasValue())
[[[ENDIF]]]
        return error(flag, result, "option does not take a value.");
[[[ENDIF]]]
[[[ELSE]]]
[[[IF hasMinOrMaxValues]]]
    size_t prevSize = result.[[[memberName]]].size();
[[[ENDIF]]]
    if (!addDelimitedValues(result.[[[memberName]]], '[[[delimiter]]]', [[[IF hasValueCheck]]]
                            []([[[parameterType]]] v)
                            {return [[[valueCheck(v)]]];},
                            [[[ENDIF]]]flag, argIt, result))
        return false;
[[[IF hasFixedNumberOfValues]]]
    if (result.[[[memberName]]].size() - prevSize != [[[minValues]]])
        return error(flag, result, "option argument must contain [[[minValues]]] values.");
[[[ELSE]]]
[[[IF hasMinValues]]]
    if (result.[[[memberName]]].size() - prevSize < [[[minValues]]])
        return error(flag, result, "option argument must contain at least [[[minValues]]] values.");
[[[ENDIF]]]
[[[IF hasMaxValues]]]
    if (result.[[[memberName]]].size() - prevSize > [[[maxValues]]])
        return error(flag, result, "option argument can't contain more than [[[maxValues]]] values.");
[[[ENDIF]]]
[[[ENDIF]]]
[[[IF hasMaxCount]]]
    if (result.[[[memberName]]].size() > [[[maxCount]]])
        return error(flag, result, "too many values (max is [[[maxCount]]]).");
[[[ENDIF]]]
[[[ENDIF]]]
    return true;
}
"""

processListOptionTemplate = """\
bool process_[[[name]]]_option([[[>]]]const std::string& flag,
[[[|]]]ArgumentIterator& argIt,
[[[|]]][[[className]]]& result[[[<]]])
{
[[[IF hasDefault]]]
    if (!result.reserved_for_internal_use->[[[memberName]]])
    {
        result.[[[memberName]]].clear();
        result.reserved_for_internal_use->[[[memberName]]] = true;
    }
[[[ENDIF]]]
[[[IF hasMaxCount]]]
    if (result.[[[memberName]]].size() == [[[maxCount]]])
        return error(flag, result, "too many values (max is [[[maxCount]]]).");
[[[ENDIF]]]
[[[IF value]]]
    result.[[[memberName]]].push_back([[[value]]]);
[[[IF hasNormalOptions]]]
[[[IF hasShortOptions]]]
    if (!resemblesShortOption(flag.c_str()) && argIt.hasValue())
[[[ELSE]]]
    if (argIt.hasValue())
[[[ENDIF]]]
        return error(flag, result, "option does not take a value.");
[[[ENDIF]]]
[[[ELSE]]]
    [[[valueType]]] value;
    if (!getValue(value, [[[IF hasValueCheck]]]
                  []([[[parameterType]]] v){return [[[valueCheck(v)]]];},
                  [[[ENDIF]]]flag, argIt, result))
        return false;
    result.[[[memberName]]].push_back(value);
[[[ENDIF]]]
    return true;
}
"""

processMultivalueOptionTemplate =  """\
bool process_[[[name]]]_option([[[>]]]const std::string& flag,
[[[|]]]ArgumentIterator& argIt,
[[[|]]][[[className]]]& result[[[<]]])
{
[[[IF isMandatory]]]
    result.reserved_for_internal_use->[[[memberName]]] = true;
[[[ENDIF]]]
    result.[[[memberName]]].clear();
[[[IF value]]]
    [[[multivalueValueAssignment]]]
[[[IF hasNormalOptions]]]
[[[IF hasShortOptions]]]
    if (!resemblesShortOption(flag.c_str()) && argIt.hasValue())
        return error(flag, result, "option does not take a value.");
[[[ELSE]]]
    if (argIt.hasValue())
        return error(flag, result, "option does not take a value.");
[[[ENDIF]]]
[[[ENDIF]]]
[[[ELSE]]]
[[[IF delimiter]]]
    if (!addDelimitedValues(result.[[[memberName]]], '[[[delimiter]]]', [[[IF hasValueCheck]]]
                            []([[[parameterType]]] v)
                            {return [[[valueCheck(v)]]];},
                            [[[ENDIF]]]flag, argIt, result))
        return false;
    if (result.[[[memberName]]].size() != [[[minValues]]])
        return error(flag, result, "option argument must contain [[[minValues]]] "
                                   "values separated by \\"[[[delimiter]]]\\".");
[[[ELSE]]]
    [[[valueType]]] value;
    return getValue(value, [[[IF hasValueCheck]]]
                    []([[[parameterType]]] v){return [[[valueCheck(v)]]];},
                    [[[ENDIF]]]flag, argIt, result);
    result.[[[memberName]]].push_back(value);
[[[ENDIF]]]
[[[ENDIF]]]
    return true;
}
"""

processOptionTemplate = """\
bool process_[[[name]]]_option([[[>]]]const std::string& flag,
[[[|]]]ArgumentIterator& argIt,
[[[|]]][[[className]]]& result[[[<]]])
{
[[[IF isMandatory]]]
    result.reserved_for_internal_use->[[[memberName]]] = true;
[[[ENDIF]]]
[[[IF value]]]
    result.[[[memberName]]] = [[[value]]];
[[[IF hasNormalOptions]]]
[[[IF hasShortOptions]]]
    if (!resemblesShortOption(flag.c_str()) && argIt.hasValue())
        return error(flag, result, "option does not take a value.");
[[[ELSE]]]
    if (argIt.hasValue())
        return error(flag, result, "option does not take a value.");
[[[ENDIF]]]
[[[ENDIF]]]
    return true;
[[[ELSE]]]
    return getValue(result.[[[memberName]]], [[[IF hasValueCheck]]]
                    []([[[parameterType]]] v){return [[[valueCheck(v)]]];},
                    [[[ENDIF]]]flag, argIt, result);
[[[ENDIF]]]
}
"""

processHelpOptionTemplate = """\
bool process_[[[memberName]]]_option([[[>]]]const std::string& flag,
[[[|]]]ArgumentIterator& argIt,
[[[|]]][[[className]]]& result[[[<]]])
{
    writeHelp();
    result.[[[memberName]]] = true;
    result.[[[functionName]]]_result = [[[className]]]::RESULT_HELP;
    return false;
}
"""

processInfoOptionTemplate = """\
bool process_[[[memberName]]]_option([[[>]]]const std::string& flag,
[[[|]]]ArgumentIterator& argIt,
[[[|]]][[[className]]]& result[[[<]]])
{
    result.[[[memberName]]] = true;
    result.[[[functionName]]]_result = [[[className]]]::RESULT_INFO;
    return true;
}
"""

processArgumentTemplate = """\
bool process_[[[name]]]_argument([[[>]]]const std::string& value,
[[[|]]][[[className]]]& result[[[<]]])
{
[[[IF isStringMember]]]
    result.[[[memberName]]] = value;
[[[ELSE]]]
    if (!fromString(value, result.[[[memberName]]]))
        return error("[[[name]]]", result, "invalid argument value \\"" + value + "\\".");
[[[ENDIF]]]
[[[IF hasValueCheck]]]
    if (!([[[valueCheck]]]))
        return error("[[[name]]]", result, "illegal argument value \\"" + value + "\\".");
[[[ENDIF]]]
    return true;
}
"""

processListArgumentTemplate = """\
bool process_[[[name]]]_argument([[[>]]]const std::string& value,
[[[|]]][[[className]]]& result[[[<]]])
{
[[[IF isStringMember]]]
[[[IF hasValueCheck]]]
    if (!([[[valueCheck(value)]]]))
        return error("[[[name]]]", result, "illegal argument value \\"" + value + "\\".");
[[[ENDIF]]]
    result.[[[memberName]]].push_back(value);
[[[ELSE]]]
    [[[valueType]]] v;
    if (!fromString(value, v))
        return error("[[[name]]]", result, "invalid argument value \\"" + value + "\\".");
[[[IF hasValueCheck]]]
    if (!([[[valueCheck(v)]]]))
        return error("[[[name]]]", result, "illegal argument value \\"" + value + "\\".");
[[[ENDIF]]]
    result.[[[memberName]]].push_back(v);
[[[ENDIF]]]
    return true;
}
"""

processMultivalueArgumentTemplate = """\
bool process_[[[name]]]_argument([[[>]]]const std::string& value,
[[[|]]][[[className]]]& result[[[<]]])
{
    result.[[[memberName]]].clear();
[[[IF delimiter]]]
    size_t first = 0;
    while (true)
    {
        size_t last = value.find_first_of('[[[delimiter]]]', first);
        size_t len = (last == std::string::npos ? value.size() : last) - first;
[[[IF isStringMember]]]
        [[[valueType]]] v = value.substr(first, len);
[[[ELSE]]]
        [[[valueType]]] v;
        if (!fromString(value.substr(first, len), v))
            return error("[[[name]]]", result, "invalid argument value \\""
                         + value.substr(first, len) + "\\".");
[[[ENDIF]]]
[[[IF hasValueCheck]]]
        if (!([[[valueCheck(v)]]]))
            return error("[[[name]]]", result, "illegal argument value \\"" +
                         value.substr(first, len) + "\\".");
[[[ENDIF]]]
        result.[[[memberName]]].push_back(v);
        if (last == std::string::npos)
            break;
        first = last + 1;
    }
    if (result.[[[memberName]]].size() != [[[minValues]]])
        return error("[[[name]]]", result, "option argument must contain [[[minValues]]] values.");
[[[ELIF isStringMember]]]
    if (!([[[valueCheck(value)]]]))
        return error("[[[name]]]", result, "illegal argument value \\"" + value + "\\".");
    result.[[[memberName]]].push_back(value);
[[[ELSE]]]
    [[[valueType]]] v;
    if (!fromString(value, v))
        return error("[[[name]]]", result, "invalid argument value \\"" + value + "\\".");
[[[IF hasValueCheck]]]
        if (!([[[valueCheck(value)]]]))
            return error("[[[name]]]", result, "illegal argument value \\"" +
                         value.substr(first, last) + "\\".");
[[[ENDIF]]]
    result.[[[memberName]]].push_back(v);
[[[ENDIF]]]
[[[ENDIF]]]
    return true;
}
"""

processMultivalueListArgumentTemplate = """\
bool process_[[[name]]]_argument([[[>]]]const std::string& value,
[[[|]]][[[className]]]& result[[[<]]])
{
[[[IF hasMinOrMaxValues]]]
    size_t prevSize = result.[[[memberName]]].size();
[[[ENDIF]]]
    size_t first = 0;
    while (true)
    {
        size_t last = value.find_first_of('[[[delimiter]]]', first);
        size_t len = (last == std::string::npos ? value.size() : last) - first;
[[[IF isStringMember]]]
        [[[valueType]]] v = value.substr(first, len);
[[[ELSE]]]
        [[[valueType]]] v;
        if (!fromString(value.substr(first, len), v))
            return error("[[[name]]]", result, "invalid argument value \\""
                         + value.substr(first, len) + "\\".");
[[[ENDIF]]]
[[[IF hasValueCheck]]]
            if (!([[[valueCheck(v)]]]))
                return error("[[[name]]]", result, "illegal argument value \\"" +
                             value.substr(first, len) + "\\".");
[[[ENDIF]]]
        result.[[[memberName]]].push_back(v);
        if (last == std::string::npos)
            break;
        first = last + 1;
    }
[[[IF hasFixedNumberOfValues]]]
    if (result.[[[memberName]]].size() - prevSize != [[[minValues]]])
        return error("[[[name]]]", result, "option argument must contain [[[minValues]]] values.");
[[[ELSE]]]
[[[IF hasMinValues]]]
    if (result.[[[memberName]]].size() - prevSize < [[[minValues]]])
        return error("[[[name]]]", result, "option argument must contain at least [[[minValues]]] values.");
[[[ENDIF]]]
[[[IF hasMaxValues]]]
    if (result.[[[memberName]]].size() - prevSize > [[[maxValues]]])
        return error("[[[name]]]", result, "option argument can't contain more than [[[maxValues]]] values.");
[[[ENDIF]]]
[[[ENDIF]]]
[[[IF hasMaxCount]]]
    if (result.[[[memberName]]].size() > [[[maxCount]]])
        return error("[[[name]]]", result, "too many values (max is [[[maxCount]]]).");
[[[ENDIF]]]
    return true;
}
"""

class ProcessOptionExpander(codegen.Expander):
    def __init__(self, context, parent, member, arg):
        codegen.Expander.__init__(self, context)
        self.member = member
        self.memberName = member.name
        self.name = arg.name
        self.value = arg.value
        self.hasValueCheck = member.values
        self.hasShortOptions = (parent.hasShortOptions and arg.flags and
                any(f for f in arg.flags if len(f) == 2 and f[0] in "-/"))
        self.hasNormalOptions = (parent.hasNormalOptions and arg.flags and
                any(f for f in arg.flags if len(f) > 2 and f[:2] == '--'))
        self.delimiter = arg.delimiter
        self.minValues = arg.minDelimiters + 1
        self.maxValues = arg.maxDelimiters + 1
        self.hasMinValues = self.minValues != 1
        self.hasMaxValues = self.maxValues != 0
        self.hasMinOrMaxValues = self.hasMinValues or self.hasMaxValues
        self.hasFixedNumberOfValues = self.minValues == self.maxValues
        self.valueType = member.valueType
        self.isStringMember = member.valueType == "std::string"
        self.parameterType = (("const %s&" if self.isStringMember else "%s")
                              % self.valueType)
        self.maxCount = member.maxCount
        self.hasMaxCount = self.maxCount != -1
        self.className = parent.className
        self.isMandatory = isMandatory(member)
        self.functionName = parent.functionName
        self.hasDefault = member.default

    def valueCheck(self, params, context):
        var = params[0] if params else "result." + self.memberName
        op = dict(g="<", ge="<=", l="<", le="<=")
        lines = []
        for v in self.member.values:
            v0, v1, o0, o1 = v
            if v0 == v1:
                lines.append("(%s == %s)" % (var, v0))
            elif not v1:
                lines.append("(%s %s %s)" %
                             (v0, op[o0], var))
            elif not v0:
                lines.append("(%s %s %s)" %
                             (var, op[o1], v1))
            else:
                lines.append("(%s %s %s && %s %s %s)" %
                             (v0, op[o0], var, var, op[o1], v1))
        if lines:
            return codegen.join(lines, 76 - context[1], " || ", " ||")
        else:
            return ["true"]

    def multivalueValueAssignment(self, params, context):
        s = "result.%s.push_back(%%s);" % self.member.name
        return [s % v for v in self.value.split("|")]

def createFile(fileName, text, opts, args, members, **kw):
    cppFile = os.path.join(os.path.dirname(__file__), "cpp_template.txt")
    cppTemplate = open(cppFile).read()
    kw["fileName"] = fileName
    open(fileName, "w").write(codegen.makeText(
            cppTemplate,
            CppExpander(text, opts, args, members, **kw)))
