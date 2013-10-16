class Error(Exception):
    pass

def _tokenize(tmplStr):
    for line in tmplStr.split("\n"):
        start = 0
        while True:
            end = line.find("[[[", start)
            if end == -1:
                if start != len(line):
                    yield "TEXT", line[start:]
                yield "NEWLINE", ""
                break
            yield "TEXT", line[start:end]
            start = end + 3
            end = line.find("]]]", start)
            if end == -1:
                raise Error("[[[ not followed by ]]] on the same line.")
            if line[start:].startswith("IF "):
                yield tuple(line[start:end].split(None, 2))
            elif line[start:].startswith("ELIF "):
                yield tuple(line[start:end].split(None, 2))
            elif line[start:end] in ("|", ">", "<"):
                yield line[start:end], ""
            elif line[start:].startswith("ELSE"):
                yield "ELSE", ""
            elif line[start:].startswith("ENDIF"):
                yield "ENDIF", ""
            elif line[start:].startswith("SET "):
                yield "SET", line[start + 4:end].lstrip()
            else:
                yield "EXPAND", line[start:end]
            start = end + 3

class Expander(object):
    def __init__(self, context=("", 0)):
        self.context = context

    def __call__(self, key, params, context):
        if callable(self.__getattribute__(key)):
            context = (self.context[0] + context[0],
                       self.context[1] + context[1])
            return self.__getattribute__(key)(params, context)
        else:
            return self.__getattribute__(key)

    def _assign_value_(self, identifier, value):
        self.__setattr__(identifier, value)

class DictExpander(Expander):
    def __init__(self, dict):
        Expander.__init__(self)
        self._dict = dict

    def __call__(self, key, params, context):
        return self._dict[key]

    def _assign_value_(self, identifier, value):
        self._dict[identifier] = value

class FuncExpander(Expander):
    def __init__(self, expandFunc, assignFunc = None):
        Expander.__init__(self)
        self._expand = expandFunc
        self._assign = assignFunc

    def __call__(self, key, params, context):
        return self._expand(key, params, context)

    def _assign_value_(self, identifier, value):
        if self._assign:
            self._assign(identifier, value)

def isEmptyOrSpace(s):
    return not s or s.isspace()

class TemplateProcessor:
    def __init__(self, template, expander):
        self.template = template
        self.expander = expander
        self.lines = []
        self.curline = []
        self.column = 0
        self.scope = ["active"]
        self.lineNo = 1
        self.alignments = []

    def __call__(self):
        ignoreNewline = False
        try:
            for ttype, tstr in _tokenize(self.template):
                if ignoreNewline:
                    ignoreNewline = False
                    if ttype == "NEWLINE":
                        if isEmptyOrSpace("".join(self.curline)):
                            self.curline = []
                        self.lineNo += 1
                        continue

                if ttype == "NEWLINE":
                    self.handleNEWLINE()
                elif ttype == "IF":
                    self.handleIF(tstr)
                    ignoreNewline = isEmptyOrSpace("".join(self.curline))
                elif ttype == "ENDIF":
                    self.handleENDIF()
                    ignoreNewline = isEmptyOrSpace("".join(self.curline))
                elif self.scope[-1] == "done":
                    pass
                elif ttype == "ELIF":
                    self.handleELIF(tstr)
                    ignoreNewline = isEmptyOrSpace("".join(self.curline))
                elif ttype == "ELSE":
                    self.handleELSE()
                    ignoreNewline = isEmptyOrSpace("".join(self.curline))
                elif self.scope[-1] == "inactive":
                    pass
                elif ttype == "TEXT":
                    self._addText(tstr)
                elif ttype == "EXPAND":
                    ignoreNewline = (not self.handleEXPAND(tstr) and
                                     not "".join(self.curline))
                elif ttype == "SET":
                    self.handleSET(tstr)
                    ignoreNewline = isEmptyOrSpace("".join(self.curline))
                elif ttype == ">":
                    self.pushAlignment()
                elif ttype == "|":
                    self.align()
                elif ttype == "<":
                    self.popAlignment()
                else:
                    raise Error("Unknown token: " + ttype)
            if len(self.scope) != 1:
                raise Error("Number of IFs without closing ENDIFs: %d" %
                            (len(self.scope) - 1))
        except Error as ex:
            raise Error("[line %d]: %s" % (self.lineNo, str(ex)))

    def handleNEWLINE(self):
        self.lineNo += 1
        if self.scope[-1] != "active":
            return
        self.lines.append("".join(self.curline).rstrip())
        self.curline = []
        self.column = 0

    def handleEXPAND(self, key):
        if self.scope[-1] != "active":
            return False
        text = self._expand(key)
        if type(text) == str:
            if not text:
                return False
            self._addText(text)
        elif type(text) == list:
            if not text:
                return False
            self._addLines(text)
        else:
            self._addText(str(text))
        return True

    def handleIF(self, key):
        if self.scope[-1] != "active":
            self.scope.append("done")
        elif self._expand(key):
            self.scope.append("active")
        else:
            self.scope.append("inactive")

    def handleENDIF(self):
        if len(self.scope) == 1:
            raise Error("ENDIF must be preceded by IF")
        self.scope.pop()

    def handleELIF(self, key):
        if len(self.scope) == 1:
            raise Error("ELIF must be preceded by IF")
        elif self.scope[-1] == "active":
            self.scope[-1] = "done"
        elif self.scope[-1] == "inactive" and self._expand(key):
            self.scope[-1] = "active"

    def handleELSE(self):
        if len(self.scope) == 1:
            raise Error("ELSE must be preceded by IF")
        elif self.scope[-1] == "active":
            self.scope[-1] = "done"
        elif self.scope[-1] == "inactive":
            self.scope[-1] = "active"

    def handleSET(self, text):
        parts = text.split("=", 1)
        if len(parts) == 1 or not parts[0]:
            raise Error('"SET %s": invalid format for SET. '
                        'Correct format is "SET identifier=value".' % text)
        self.expander._assign_value_(parts[0], parts[1])

    def pushAlignment(self):
        self.alignments.append(self._alignment())

    def popAlignment(self):
        self.alignments.pop()

    def align(self):
        self.curline.append(self.alignments[-1][self.column:])

    def _addLines(self, lines):
        if not lines:
            return
        self.curline.append(lines[0])
        if len(lines) > 1:
            align = self._alignment()
            self.lines.append("".join(self.curline))
            self.curline = []
            self.column = 0
            for line in lines[1:-1]:
                self.lines.append(align + line)
            self._addText(align + lines[-1])

    def _addText(self, text):
        npos = text.rfind("\n")
        if npos == -1:
            self.curline.append(text)
            self.column += len(text)
        else:
            self.curline.append(text[:npos])
            self.lines.append("".join(self.curline))
            self.curline = [text[npos + 1:]]
            self.column = len(text) - npos + 1

    def _splitKey(self, text):
        b = text.find("(")
        if b == -1:
            return text, ()
        e = text.find(")", b + 1)
        if e == -1:
            raise Error("No closing parenthesis: " + text)
        return text[:b], [s.strip() for s in text[b + 1:e].split(",")]

    def _expand(self, key):
        key, params = self._splitKey(key)
        return self.expander(key, params, (self._indentation(), self.column))

    def _indentation(self):
        for i, s in enumerate(self.curline):
            for j, c in enumerate(s):
                if c not in "\t ":
                    return "".join(self.curline[:i] + [self.curline[i][:j]])
        return ""

    def _alignment(self):
        ind = self._indentation()
        return ind + " " * (self.column - len(ind))

def makeLines(template, expanderFunc):
    proc = TemplateProcessor(template, expanderFunc)
    proc()
    return proc.lines

def makeText(template, expanderFunc):
    return "\n".join(makeLines(template, expanderFunc))

class LineBuilder:
    def __init__(self, lineWidth=80):
        self.lineWidth = lineWidth
        self.lines = []
        self.curLine = []
        self.curLineWidth = 0

    def append(self, text, sep=" ", newlineSep="", firstSep=""):
        if self.curLineWidth == 0:
            self._addText(firstSep, text)
        elif self.curLineWidth + len(text) + len(sep) <= self.lineWidth:
            self._addText(sep, text)
        elif self.curLineWidth + len(newlineSep) <= self.lineWidth:
            self.curLine.append(newlineSep)
            self.newline()
            self._addText(text)
        elif len(self.curLine) == 1:
            self.curLine.append(newlineSep)
            self.newline()
            self._addText(text)
        else:
            last = self.curLine[-1]
            del self.curLine[-2:]
            self.curLine.append(newlineSep)
            self.newline()
            self._addText(last)
            self.append(text, sep, newlineSep)

    def join(self, strings, sep=" ", newlineSep="", firstSep="", firstNewlineSep=""):
        try:
            i = iter(strings)
            self.append(next(i), firstSep, firstNewlineSep)
            while True:
                self.append(next(i), sep, newlineSep)
        except StopIteration:
            pass

    def newline(self):
        self.lines.append("".join(self.curLine))
        self.curLine = []
        self.curLineWidth = 0

    def build(self):
        if self.curLine:
            self.newline()
        return self.lines

    def _addText(self, *strings):
        self.curLine.extend(s for s in strings if s)
        self.curLineWidth += sum(len(s) for s in strings)

def join(strings, lineWidth=80, sep=" ", newlineSep="", firstSep="", firstNewlineSep=""):
    lb = LineBuilder(lineWidth)
    lb.join(strings, sep, newlineSep, firstSep, firstNewlineSep)
    return lb.build()

def _translateToSpace(s, chars):
    # Slow (but not noticably so in this context) replacement for maketrans and
    # translate. I couldn't find a way to use maketrans and translate that
    # worked under both python2 and python3
    if chars not in _translateToSpace.transforms:
        _translateToSpace.transforms[chars] = set(c for c in chars)
    transform = _translateToSpace.transforms[chars]
    return "".join(" " if c in transform else c for c in s)
_translateToSpace.transforms = {}

_BadCppChars = "'!\"#$%&/()=?+*@.:,;<>^`-_[]{}"

def makeMacroName(s):
    return "_".join(_translateToSpace(s.upper(), _BadCppChars).split())

def variableName(s):
    return "_".join(translateToSpace(s, _BadCppChars).split())

if __name__ == "__main__":
    import sys

    def main(args):
        teststring = """\
std::unique_ptr<CommandLine> parseArgs(int argc, char* argv[])
{
    auto cmdLine = std::make_unique<CommandLine>();
    initialize(cmdLine->argParser);
    cmdLine->parseArgs(cmdLine->parsedArgs, argc, argv);

    if (!cmdLine->parsedArgs)
    {
        cmdLine->argParser.writeErrors(cmdLine->parsedArgs);
        return cmdLine;
    }
    if ([[[readHelpOpts]]])
    {
        cmdLine.writeHelp();
        cmdLine->result = CommandLine::Help;
        return cmdLine;
    }
[[[IF hasInfoOpts]]]
    if ([[[readInfoOpts]]])
    {
        cmdLine->result = CommandLine::Info;
        return cmdLine;
    }
[[[ENDIF]]]
    if ([[[incorrectArgCount]]])
    {
        cmdLine->argParser.writeMessage("Invalid number of arguments.");
        return cmdLine;
    }
[[[IF hasNormalOpts]]]
    [[[readNormalOpts]]]
[[[ENDIF]]]
[[[IF hasArgs]]]
    [[[readArgs]]]
[[[ENDIF]]]

    cmdLine->result = CommandLine::Ok;

    return cmdLine;
}"""
        print("\n".join(generateLines(teststring, lookup=dict(
                hasInfoOpts=True,
                readInfoOpts=["kjell &&", "arne &&", "bjarne"],
                readHelpOpts="finn ||\n        tom"))))
        return 0

    sys.exit(main(sys.argv[1:]))
