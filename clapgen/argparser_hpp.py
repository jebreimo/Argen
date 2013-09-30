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
[[[IF namespace]]]

[[[beginNamespace]]]
[[[ENDIF]]]

struct [[[className]]]
{
    [[[className]]]();
    ~[[[className]]]();

    [[[members]]]

    enum Result {RESULT_OK, RESULT_INFO, RESULT_HELP, RESULT_ERROR};
    Result [[[functionName]]]_result;
};

std::unique_ptr<[[[className]]]> [[[functionName]]](int argc, char* argv[]);

[[[IF namespace]]]
[[[endNamespace]]]

[[[ENDIF]]]
#endif
"""

class HppExpander(codegen.Expander):
    def __init__(self, members, className="Arguments",
                 fileName="ParseArguments.hpp", functionName="parseArguments",
                 namespace=""):
        codegen.Expander.__init__(self)
        self.className = className
        self.includeGuard = codegen.makeMacroName(fileName)
        self.functionName = functionName
        self.namespace = namespace.split("::")
        if not self.namespace[0]:
            self.namespace = []
        self._members = members

    def members(self, params, context):
        lines = []
        for m in self._members:
            if m.type != "final":
                if m.isOption:
                    comment = "/// Member for options " + m.flags
                else:
                    args = ", ".join(a.name for a in m.arguments)
                    comment = "/// Member for arguments " + args
                lines.append(comment)
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
