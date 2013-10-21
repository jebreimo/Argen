ArgumentProps = set(("argument", "count", "delimiter", "delimitercount",
                     "flags", "index", "member", "text", "value"))
MemberProps = set(("action", "condition", "conditionmessage", "default", "include",
                   "includecpp", "type", "values", "valuetype"))
LegalProps = set(ArgumentProps).union(MemberProps)
LegalTypeValues = set(("final", "help", "info", "list", "multivalue", "value"))

DefaultStartDefinition = "${"
DefaultEndDefinition = "}$"
DefaultDefinitionSeparator = "|"

IntegerArguments = set(("NUM", "COUNT", "INT", "SIZE", "LEN", "LENGTH"))
