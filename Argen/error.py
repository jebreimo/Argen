"""
    Defines the exception class Error used to report errors by parser.py and
    properties.py
"""
class Error(Exception):
    def __init__(self, msg, lineNo="", fileName=""):
        Exception.__init__(self, msg)
        self.lineNo = lineNo
        self.fileName = fileName

    def formattedMsg(self):
        msg = Exception.__str__(self)
        if self.lineNo:
            return "%s[%s] Error: %s" % (self.fileName, self.lineNo, msg)
        elif self.fileName:
            return "%s Error: %s" % (self.fileName, msg)
        else:
            return "Error: " + msg

    def __str__(self):
        return self.formattedMsg()
