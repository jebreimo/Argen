import codegen

hppTemplate = """\
#ifndef [[[includeGuard]]]
#define [[[includeGuard]]]

#include <memory>
[[[IF hasStringMembers]]]
#include <string>
[[[ENDIF]]]
[[[IF hasVectorMembers]]]
#include <vector>
[[[ENDIF]]]

/** @file
  * Defines the function [[[functionName]]] and its result [[[className]]].
  */
[[[IF namespace]]]

[[[beginNamespace]]]
[[[ENDIF]]]

[[[IF hasTrackedOptions]]]
/** A struct private to the implementation.
  */
struct TrackedOptions;
[[[ENDIF]]]

/** @brief The result of [[[functionName]]]
  */
struct [[[className]]]
{
    /** @brief Assigns the default values to all members.
      */
    [[[className]]]();
    /** @brief Assigns the default values to all members.
      */
    ~[[[className]]]();

    [[[members]]]

    enum Result {
        /** @brief [[[functionName]]] parsed the arguments successfully.
          */
        RESULT_OK,
[[[IF hasInfoOptions]]]
        /** @brief [[[functionName]]] encountered one or more info options.
          *
          * Only options have been parsed. Arguments are ignored and
          * validation has been restricted to illegal or invalid options.
          * The only members that can be relied upon are the ones
          * corresponding to the info options.
          */
        RESULT_INFO,
[[[ENDIF]]]
        /** @brief [[[functionName]]] encountered a help option.
          *
          * The help message has been displayed. The option and argument
          * members of this struct can not be relied upon.
          */
        RESULT_HELP,
        /** @brief There are invalid or missing options or arguments.
          *
          * An error message has been displayed. The option and argument
          * members of this struct can not be relied upon.
          */
        RESULT_ERROR
    };

    /** @brief The exit status of [[[functionName]]].
      *
      * This member should always be checked before any of the other members
      * are read.
      */
    Result [[[functionName]]]_result;
    [[[IF hasTrackedOptions]]]

    /** This member is reserved for internal use in [[[functionName]]].
      *
      * It's always nullptr.
      */
    TrackedOptions* reserved_for_internal_use;
    [[[ENDIF]]]
};

/** @brief Parses the arguments in @a argv.
  *
  * @param argc the number of values in argv.
  * @param argv the arguments (an array of char-strings).
  * @returns an instance of [[[className]]] with values in
  *     accordance with the parsed arguments. If @a argc is 0 the
  *     returned value is a nullptr.
  */
std::unique_ptr<[[[className]]]> [[[functionName]]](int argc, char* argv[]);

[[[IF namespace]]]
[[[endNamespace]]]

[[[ENDIF]]]
#endif
"""

class HppExpander(codegen.Expander):
    def __init__(self, members, className="Arguments",
                 fileName="ParseArguments.hpp",
                 functionName="parseArguments", namespace=""):
        codegen.Expander.__init__(self)
        self.className = className
        self.includeGuard = codegen.makeMacroName(fileName)
        self.functionName = functionName
        self.namespace = namespace.split("::")
        self.hasInfoOptions = any(m for m in members if m.type == "info")
        def isMandatory(m): return m.isOption and m.count == (1, 1)
        def isDefaultList(m): return m.type == "list" and m.default
        def isTrackable(m): return isMandatory(m) or isDefaultList(m)
        self.hasTrackedOptions = any(m for m in members if isTrackable(m))
        if not self.namespace[0]:
            self.namespace = []
        self._members = members

    def members(self, params, context):
        lines = []
        for m in self._members:
            if m.type != "final":
                if m.isOption:
                    lines.append("/** @brief Member for options: " + m.flags)
                else:
                    args = ", ".join(a.name for a in m.arguments)
                    lines.append("/** @brief Member for arguments: " + args)
                lines.append("  */")
                lines.append("%(memberType)s %(name)s;" % m)
        return lines

    def hasVectorMembers(self, params, context):
        for m in self._members:
            if m.type in ("list", "multivalue"):
                return True
        return False

    def hasStringMembers(self, params, context):
        for m in self._members:
            if m.valueType == "std::string":
                return True
        return False

    def beginNamespace(self, params, context):
        return "namespace " + " { namespace ".join(self.namespace) + " {"

    def endNamespace(self, params, context):
        return "}" * len(self.namespace)

def createFile(fileName, members, **kw):
    kw["fileName"] = fileName
    open(fileName, "w").write(codegen.makeText(hppTemplate,
                                               HppExpander(members, **kw)))
