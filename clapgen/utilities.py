"""
"""

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
    values = []
    for value in s.split():
        c = value.count('"')
        if c not in (0, 2):
            raise Error("values contains invalud string: \"" + value + "\"")
        minmax = value.split("..", 1)
        if len(minmax) == 2:
            s, e = minmax
            if not s:
                sCmp = ""
            elif s[0] != "(":
                sCmp = "ge"
            else:
                sCmp = "g"
            if s and s[0] in "[(":
                s = s[1:]
            if not e:
                eCmp = ""
            elif e[-1] != ")":
                eCmp = "le"
            else:
                eCmp = "l"
            if e and e[-1] in "])":
                e = e[:-1]
            if s or e:
                values.append((s, e, sCmp, eCmp))
        else:
            values.append((value, value, "e", "e"))
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
