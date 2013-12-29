"""
"""

def findToken(s, startToken, endToken, startIndex=0):
    start = s.find(startToken, startIndex)
    if start == -1:
        return -1, -1, ""
    end = s.find(endToken, start + len(startToken))
    if end == -1:
        return start, len(s), s[start + len(startToken):]
    else:
        return start, end + len(endToken), s[start + len(startToken):end]

def verbalJoin(words):
    if len(words) <= 1:
        return "".join(words)
    return ", ".join(words[:-1]) + " and " + words[-1]

def parseCount(s):
    parts = s.split("..")
    if len(parts) == 1:
        return int(s), int(s)
    elif len(parts) != 2:
        raise Error("Invalid count: " + s)
    else:
        count = (int(parts[0]) if parts[0] else 0,
                 int(parts[1]) if parts[1] else -1)
        if count[1] != -1 and count[1] < count[0]:
            raise Error("Invalid range: \"%s\"" % s)
        return count

def parseValues(s):
    """parseValues(s) -> list of (min, max, min-comparison, max-comparison)

    Parses the value of the Values property.
    """
    values = []
    for value in s.split():
        c = value.count('"')
        if c not in (0, 2):
            raise Error("values contains invalud string: \"" + value + "\"")
        minmax = value.split("..", 1)
        if len(minmax) == 2:
            lo, hi = minmax
            if s[0] in "[<" and s[-1] in "]>":
                loPar, hiPar = s[0], s[-1]
                lo, hi = lo[1:], hi[:-1]
            else:
                loPar, hiPar = "", ""
            if not lo:
                loCmp = ""
            elif loPar != "<":
                loCmp = "<="
            else:
                loCmp = "<"
            if not hi:
                hiCmp = ""
            elif hiPar != ">":
                hiCmp = "<="
            else:
                hiCmp = "<"
            if lo or hi:
                values.append((lo, hi, loCmp, hiCmp))
        else:
            values.append((value, value, "=", "="))
    return values

def translateToSpace(s, chars):
    # Slow (but not noticably so in this context) replacement for maketrans
    # and translate. I couldn't find a way to use maketrans and translate that
    # worked under both python2 and python3
    if chars not in translateToSpace.transforms:
        translateToSpace.transforms[chars] = set(c for c in chars)
    transform = translateToSpace.transforms[chars]
    return "".join(" " if c in transform else c for c in s)
translateToSpace.transforms = {}
