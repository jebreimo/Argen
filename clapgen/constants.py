ArgumentProps = set(("action", "argument", "condition", "conditionmessage",
                     "count", "delimiter", "delimitercount",
                     "flags", "index", "member", "text", "value"))
MemberProps = set(("default", "include", "includecpp", "memberaction",
                   "membercondition",
                   "memberconditionmessage", "type", "values", "valuetype"))
PropAliases = {
    "cond": "condition",
    "condmessage": "conditionmessage",
    "condmsg": "conditionmessage",
    "del": "delimiter",
    "delcount": "delimitercount",
    "memcond": "membercondition",
    "memcondmessage": "memberconditionmessage",
    "memcondmsg": "memberconditionmessage",
    "vtype": "valuetype"
}
LegalProps = set(ArgumentProps).union(MemberProps)
LegalTypeValues = set(("final", "help", "info", "list", "multivalue", "value"))

DefaultStartDefinition = "${"
DefaultEndDefinition = "}$"
DefaultDefinitionSeparator = "|"

IntegerArguments = set(("NUM", "COUNT", "INT", "SIZE", "LEN", "LENGTH"))
