import constants
import utilities

class Argument(object):
    """This class represents an option or argument to be handled by the
       generated argument parser function.
    """
    def __init__(self, props):
        self.props = dict((k, props[k]) for k in props
                          if k not in constants.MemberProps)
        self.flags = props["flags"].split() if "flags" in props else []
        self.value = props.get("value")
        self.member = None
        self.memberName = props["member"]
        self.memberProps = dict((k, props[k])
                                for k in constants.MemberProps if k in props)
        self.index = int(props["index"]) if "index" in props else None
        self.name = props["name"]
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

