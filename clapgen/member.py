import utilities

class Member(object):
    """This class represents a member variable in the struct that is
       returned by the generated argument parser function.
    """
    def __init__(self, props):
        self.default = props["default"]
        self.props = props
        self.arguments = props["arguments"]
        self.name = props["name"]
        self.values = utilities.parseValues(props.get("values", ""))
        self.valueType = props["valuetype"]
        self.count = utilities.parseCount(props["count"])
        self.minCount, self.maxCount = self.count
        self.include = props.get("include")
        self.includeCpp = props.get("includecpp")
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
