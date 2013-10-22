ArgumentProps = set(("action", "argument", "condition", "conditionmessage",
                     "count", "delimiter", "delimitercount",
                     "flags", "index", "member", "postcondition",
                     "postconditionmessage", "text", "value"))
MemberProps = set(("default",
                   "include", "includecpp", "type", "values", "valuetype"))
PropAliases = {
    "cond": "condition",
    "condmessage": "conditionmessage",
    "condmsg": "conditionmessage",
    "del": "delimiter",
    "delcount": "delimitercount",
    "postcond": "postcondition",
    "postcondmessage": "postconditionmessage",
    "postcondmsg": "postconditionmessage",
    "vtype": "valuetype"
}
LegalProps = set(ArgumentProps).union(MemberProps)
LegalTypeValues = set(("final", "help", "info", "list", "multivalue", "value"))

DefaultStartDefinition = "${"
DefaultEndDefinition = "}$"
DefaultDefinitionSeparator = "|"

IntegerArguments = set(("NUM", "COUNT", "INT", "SIZE", "LEN", "LENGTH"))
