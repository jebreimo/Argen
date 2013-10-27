import codegen
import os

class HppExpander(codegen.Expander):
    def __init__(self, members, className="Arguments",
                 fileName="ParseArguments.hpp",
                 functionName="parseArguments", namespace=""):
        codegen.Expander.__init__(self)
        self.className = className
        self.includeGuard = codegen.makeMacroName(fileName)
        self.functionName = functionName
        self.namespace = [s for s in namespace.split("::") if s]
        self.hasInfoOptions = any(m for m in members if m.type == "info")
        def isTrackable(m):
            return ((m.isOption and
                     (m.count == (1, 1)) or
                     (m.type == "list" and m.default)) or
                    (m.action) or
                    (m.condition))
        self.hasTrackedOptions = any(m for m in members if isTrackable(m))
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
        if not self.namespace:
            return ""
        else:
            return "namespace " + " { namespace ".join(self.namespace) + " {"

    def endNamespace(self, params, context):
        return "}" * len(self.namespace)

    def customIncludes(self, params, context):
        lines = []
        for inc in set(m.include for m in self._members if m.include):
            lines.append("#include " + inc)
        return lines

def createFile(fileName, members, **kw):
    hppFile = os.path.join(os.path.dirname(__file__), "hpp_template.txt")
    hppTemplate = open(hppFile).read()
    kw["fileName"] = fileName
    open(fileName, "w").write(codegen.makeText(hppTemplate,
                                               HppExpander(members, **kw)))
