import constants
import utilities

class Argument(object):
    """This class represents an option or argument to be handled by the
       generated argument parser function.
    """
    def __init__(self, props):
        self.props = dict((k, props[k]) for k in props
                          if k not in constants.MemberProps)
        self.argument = props.get("argument", "")
        self.flags = props["flags"].split() if "flags" in props else []
        self.value = props.get("value")
        self.member = None
        self.memberProps = dict((k, props[k])
                                for k in constants.MemberProps if k in props)
        self.index = int(props["index"]) if "index" in props else None
        self.name = props["name"]
        self.memberName = props["member"]
        self.action = props.get("action")
        self.condition = props.get("condition")
        self.conditionMessage = props.get("conditionmessage")
        self.delimiter = props.get("delimiter", "")
        self.delimiterCount = utilities.parseCount(props.get("delimitercount", "0"))
        self.minDelimiters, self.maxDelimiters = self.delimiterCount
        self.count = utilities.parseCount(props["count"])
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

class Argument2(object):
    def __init__(self):
        self.action = ""
        self.explicitAction = False
        self.argument = ""
        self.explicitArgument = False
        self.condition = ""
        self.explicitCondition = False
        self.conditionMessage = ""
        self.explicitConditionMessage = False
        self.count = ""
        self.explicitCount = False
        self.delimiter = ""
        self.explicitDelimiter = False
        self.delimiterCount = ""
        self.explicitDelimiterCount = False
        self.flags = ""
        self.explicitFlags = False
        self.index = ""
        self.explicitIndex = False
        self.lineNo = ""
        self.memberName = ""
        self.explicitMemberName = False
        self.text = ""
        self.explicitText = False
        self.value = ""
        self.explicitValue = False

    def update(self, values, explicit = True):
        for key in values:
            if key == "action":
                self.action = values[key]
                self.explicitAction = explicit
            elif key == "argument":
                self.argument = values[key]
                self.explicitArgument = explicit
            elif key == "condition":
                self.condition = values[key]
                self.explicitCondition = explicit
            elif key == "conditionMessage":
                self.conditionMessage = values[key]
                self.explicitConditionMessage = explicit
            elif key == "count":
                self.count = values[key]
                self.explicitCount = explicit
            elif key == "delimiter":
                self.delimiter = values[key]
                self.explicitDelimiter = explicit
            elif key == "delimiterCount":
                self.delimiterCount = values[key]
                self.explicitDelimiterCount = explicit
            elif key == "flags":
                self.flags = values[key]
                self.explicitFlags = explicit
            elif key == "index":
                self.index = values[key]
                self.explicitIndex = explicit
            elif key == "lineNo":
                self.lineNo = values[key]
            elif key == "memberName":
                self.memberName = values[key]
                self.explicitMemberName = explicit
            elif key == "text":
                self.text = values[key]
                self.explicitText = explicit
            elif key == "value":
                self.value = values[key]
                self.explicitValue = explicit
