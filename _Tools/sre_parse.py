#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/_Tools/sre_parse.py
"""Internal support module for sre"""
import sys
from sre_constants import *

def set(seq):
    s = {}
    for elem in seq:
        s[elem] = 1

    return s


SPECIAL_CHARS = '.\\[{()*+?^$|'
REPEAT_CHARS = '*+?{'
DIGITS = set('0123456789')
OCTDIGITS = set('01234567')
HEXDIGITS = set('0123456789abcdefABCDEF')
WHITESPACE = set(' \t\n\r\x0b\x0c')
ESCAPES = {'\\a': (LITERAL, ord('\x07')),
 '\\b': (LITERAL, ord('\x08')),
 '\\f': (LITERAL, ord('\x0c')),
 '\\n': (LITERAL, ord('\n')),
 '\\r': (LITERAL, ord('\r')),
 '\\t': (LITERAL, ord('\t')),
 '\\v': (LITERAL, ord('\x0b')),
 '\\\\': (LITERAL, ord('\\'))}
CATEGORIES = {'\\A': (AT, AT_BEGINNING_STRING),
 '\\b': (AT, AT_BOUNDARY),
 '\\B': (AT, AT_NON_BOUNDARY),
 '\\d': (IN, [(CATEGORY, CATEGORY_DIGIT)]),
 '\\D': (IN, [(CATEGORY, CATEGORY_NOT_DIGIT)]),
 '\\s': (IN, [(CATEGORY, CATEGORY_SPACE)]),
 '\\S': (IN, [(CATEGORY, CATEGORY_NOT_SPACE)]),
 '\\w': (IN, [(CATEGORY, CATEGORY_WORD)]),
 '\\W': (IN, [(CATEGORY, CATEGORY_NOT_WORD)]),
 '\\Z': (AT, AT_END_STRING)}
FLAGS = {'i': SRE_FLAG_IGNORECASE,
 'L': SRE_FLAG_LOCALE,
 'm': SRE_FLAG_MULTILINE,
 's': SRE_FLAG_DOTALL,
 'x': SRE_FLAG_VERBOSE,
 't': SRE_FLAG_TEMPLATE,
 'u': SRE_FLAG_UNICODE}

class Pattern():

    def __init__(self):
        self.flags = 0
        self.open = []
        self.groups = 1
        self.groupdict = {}

    def opengroup(self, name = None):
        gid = self.groups
        self.groups = gid + 1
        if name is not None:
            ogid = self.groupdict.get(name, None)
            if ogid is not None:
                raise error, 'redefinition of group name %s as group %d; was group %d' % (repr(name), gid, ogid)
            self.groupdict[name] = gid
        self.open.append(gid)
        return gid

    def closegroup(self, gid):
        self.open.remove(gid)

    def checkgroup(self, gid):
        return gid < self.groups and gid not in self.open


class SubPattern():

    def __init__(self, pattern, data = None):
        self.pattern = pattern
        if data is None:
            data = []
        self.data = data
        self.width = None

    def dump(self, level = 0):
        nl = 1
        seqtypes = (type(()), type([]))
        for op, av in self.data:
            print level * '  ' + op,
            nl = 0
            if op == 'in':
                print
                nl = 1
                for op, a in av:
                    print (level + 1) * '  ' + op, a

            elif op == 'branch':
                print
                nl = 1
                i = 0
                for a in av[1]:
                    if i > 0:
                        print level * '  ' + 'or'
                    a.dump(level + 1)
                    nl = 1
                    i = i + 1

            elif type(av) in seqtypes:
                for a in av:
                    if isinstance(a, SubPattern):
                        if not nl:
                            print
                        a.dump(level + 1)
                        nl = 1
                    else:
                        print a,
                        nl = 0

            else:
                print av,
                nl = 0
            if not nl:
                print

    def __repr__(self):
        return repr(self.data)

    def __len__(self):
        return len(self.data)

    def __delitem__(self, index):
        del self.data[index]

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, code):
        self.data[index] = code

    def __getslice__(self, start, stop):
        return SubPattern(self.pattern, self.data[start:stop])

    def insert(self, index, code):
        self.data.insert(index, code)

    def append(self, code):
        self.data.append(code)

    def getwidth(self):
        if self.width:
            return self.width
        lo = hi = 0L
        UNITCODES = (ANY,
         RANGE,
         IN,
         LITERAL,
         NOT_LITERAL,
         CATEGORY)
        REPEATCODES = (MIN_REPEAT, MAX_REPEAT)
        for op, av in self.data:
            if op is BRANCH:
                i = sys.maxint
                j = 0
                for av in av[1]:
                    l, h = av.getwidth()
                    i = min(i, l)
                    j = max(j, h)

                lo = lo + i
                hi = hi + j
            elif op is CALL:
                i, j = av.getwidth()
                lo = lo + i
                hi = hi + j
            elif op is SUBPATTERN:
                i, j = av[1].getwidth()
                lo = lo + i
                hi = hi + j
            elif op in REPEATCODES:
                i, j = av[2].getwidth()
                lo = lo + long(i) * av[0]
                hi = hi + long(j) * av[1]
            elif op in UNITCODES:
                lo = lo + 1
                hi = hi + 1
            elif op == SUCCESS:
                break

        self.width = (int(min(lo, sys.maxint)), int(min(hi, sys.maxint)))
        return self.width


class Tokenizer():

    def __init__(self, string):
        self.string = string
        self.index = 0
        self.__next()

    def __next(self):
        if self.index >= len(self.string):
            self.next = None
            return
        char = self.string[self.index]
        if char[0] == '\\':
            try:
                c = self.string[self.index + 1]
            except IndexError:
                raise error, 'bogus escape (end of line)'

            char = char + c
        self.index = self.index + len(char)
        self.next = char

    def match(self, char, skip = 1):
        if char == self.next:
            if skip:
                self.__next()
            return 1
        return 0

    def get(self):
        this = self.next
        self.__next()
        return this

    def tell(self):
        return (self.index, self.next)

    def seek(self, index):
        self.index, self.next = index


def isident(char):
    return 'a' <= char <= 'z' or 'A' <= char <= 'Z' or char == '_'


def isdigit(char):
    return '0' <= char <= '9'


def isname(name):
    if not isident(name[0]):
        return False
    for char in name[1:]:
        if not isident(char) and not isdigit(char):
            return False

    return True


def _class_escape(source, escape):
    code = ESCAPES.get(escape)
    if code:
        return code
    code = CATEGORIES.get(escape)
    if code:
        return code
    try:
        c = escape[1:2]
        if c == 'x':
            while source.next in HEXDIGITS and len(escape) < 4:
                escape = escape + source.get()

            escape = escape[2:]
            if len(escape) != 2:
                raise error, 'bogus escape: %s' % repr('\\' + escape)
            return (LITERAL, int(escape, 16) & 255)
        elif c in OCTDIGITS:
            while source.next in OCTDIGITS and len(escape) < 4:
                escape = escape + source.get()

            escape = escape[1:]
            return (LITERAL, int(escape, 8) & 255)
        elif c in DIGITS:
            raise error, 'bogus escape: %s' % repr(escape)
        if len(escape) == 2:
            return (LITERAL, ord(escape[1]))
    except ValueError:
        pass

    raise error, 'bogus escape: %s' % repr(escape)


def _escape(source, escape, state):
    code = CATEGORIES.get(escape)
    if code:
        return code
    code = ESCAPES.get(escape)
    if code:
        return code
    try:
        c = escape[1:2]
        if c == 'x':
            while source.next in HEXDIGITS and len(escape) < 4:
                escape = escape + source.get()

            if len(escape) != 4:
                raise ValueError
            return (LITERAL, int(escape[2:], 16) & 255)
        elif c == '0':
            while source.next in OCTDIGITS and len(escape) < 4:
                escape = escape + source.get()

            return (LITERAL, int(escape[1:], 8) & 255)
        elif c in DIGITS:
            if source.next in DIGITS:
                escape = escape + source.get()
                if escape[1] in OCTDIGITS and escape[2] in OCTDIGITS:
                    if source.next in OCTDIGITS:
                        escape = escape + source.get()
                        return (LITERAL, int(escape[1:], 8) & 255)
            group = int(escape[1:])
            if group < state.groups:
                if not state.checkgroup(group):
                    raise error, 'cannot refer to open group'
                return (GROUPREF, group)
            raise ValueError
        if len(escape) == 2:
            return (LITERAL, ord(escape[1]))
    except ValueError:
        pass

    raise error, 'bogus escape: %s' % repr(escape)


def _parse_sub(source, state, nested = 1):
    items = []
    itemsappend = items.append
    sourcematch = source.match
    while 1:
        itemsappend(_parse(source, state))
        if sourcematch('|'):
            continue
        if not nested:
            break
        if not source.next or sourcematch(')', 0):
            break
        else:
            raise error, 'pattern not properly closed'

    if len(items) == 1:
        return items[0]
    subpattern = SubPattern(state)
    subpatternappend = subpattern.append
    while 1:
        prefix = None
        for item in items:
            if not item:
                break
            if prefix is None:
                prefix = item[0]
            elif item[0] != prefix:
                break
        else:
            for item in items:
                del item[0]

            subpatternappend(prefix)
            continue

        break

    for item in items:
        if len(item) != 1 or item[0][0] != LITERAL:
            break
    else:
        set = []
        setappend = set.append
        for item in items:
            setappend(item[0])

        subpatternappend((IN, set))
        return subpattern

    subpattern.append((BRANCH, (None, items)))
    return subpattern


def _parse_sub_cond(source, state, condgroup):
    item_yes = _parse(source, state)
    if source.match('|'):
        item_no = _parse(source, state)
        if source.match('|'):
            raise error, 'conditional backref with more than two branches'
    else:
        item_no = None
    if source.next and not source.match(')', 0):
        raise error, 'pattern not properly closed'
    subpattern = SubPattern(state)
    subpattern.append((GROUPREF_EXISTS, (condgroup, item_yes, item_no)))
    return subpattern


_PATTERNENDERS = set('|)')
_ASSERTCHARS = set('=!<')
_LOOKBEHINDASSERTCHARS = set('=!')
_REPEATCODES = set([MIN_REPEAT, MAX_REPEAT])

def _parse(source, state):
    subpattern = SubPattern(state)
    subpatternappend = subpattern.append
    sourceget = source.get
    sourcematch = source.match
    _len = len
    PATTERNENDERS = _PATTERNENDERS
    ASSERTCHARS = _ASSERTCHARS
    LOOKBEHINDASSERTCHARS = _LOOKBEHINDASSERTCHARS
    REPEATCODES = _REPEATCODES
    while 1:
        if source.next in PATTERNENDERS:
            break
        this = sourceget()
        if this is None:
            break
        if state.flags & SRE_FLAG_VERBOSE:
            if this in WHITESPACE:
                continue
            if this == '#':
                while 1:
                    this = sourceget()
                    if this in (None, '\n'):
                        break

                continue
        if this and this[0] not in SPECIAL_CHARS:
            subpatternappend((LITERAL, ord(this)))
        elif this == '[':
            set = []
            setappend = set.append
            if sourcematch('^'):
                setappend((NEGATE, None))
            start = set[:]
            while 1:
                this = sourceget()
                if this == ']' and set != start:
                    break
                elif this and this[0] == '\\':
                    code1 = _class_escape(source, this)
                elif this:
                    code1 = (LITERAL, ord(this))
                else:
                    raise error, 'unexpected end of regular expression'
                if sourcematch('-'):
                    this = sourceget()
                    if this == ']':
                        if code1[0] is IN:
                            code1 = code1[1][0]
                        setappend(code1)
                        setappend((LITERAL, ord('-')))
                        break
                    elif this:
                        if this[0] == '\\':
                            code2 = _class_escape(source, this)
                        else:
                            code2 = (LITERAL, ord(this))
                        if code1[0] != LITERAL or code2[0] != LITERAL:
                            raise error, 'bad character range'
                        lo = code1[1]
                        hi = code2[1]
                        if hi < lo:
                            raise error, 'bad character range'
                        setappend((RANGE, (lo, hi)))
                    else:
                        raise error, 'unexpected end of regular expression'
                else:
                    if code1[0] is IN:
                        code1 = code1[1][0]
                    setappend(code1)

            if _len(set) == 1 and set[0][0] is LITERAL:
                subpatternappend(set[0])
            elif _len(set) == 2 and set[0][0] is NEGATE and set[1][0] is LITERAL:
                subpatternappend((NOT_LITERAL, set[1][1]))
            else:
                subpatternappend((IN, set))
        elif this and this[0] in REPEAT_CHARS:
            if this == '?':
                min, max = (0, 1)
            elif this == '*':
                min, max = 0, MAXREPEAT
            elif this == '+':
                min, max = 1, MAXREPEAT
            elif this == '{':
                if source.next == '}':
                    subpatternappend((LITERAL, ord(this)))
                    continue
                here = source.tell()
                min, max = 0, MAXREPEAT
                lo = hi = ''
                while source.next in DIGITS:
                    lo = lo + source.get()

                if sourcematch(','):
                    while source.next in DIGITS:
                        hi = hi + sourceget()

                else:
                    hi = lo
                if not sourcematch('}'):
                    subpatternappend((LITERAL, ord(this)))
                    source.seek(here)
                    continue
                if lo:
                    min = int(lo)
                if hi:
                    max = int(hi)
                if max < min:
                    raise error, 'bad repeat interval'
            else:
                raise error, 'not supported'
            if subpattern:
                item = subpattern[-1:]
            else:
                item = None
            if not item or _len(item) == 1 and item[0][0] == AT:
                raise error, 'nothing to repeat'
            if item[0][0] in REPEATCODES:
                raise error, 'multiple repeat'
            if sourcematch('?'):
                subpattern[-1] = (MIN_REPEAT, (min, max, item))
            else:
                subpattern[-1] = (MAX_REPEAT, (min, max, item))
        elif this == '.':
            subpatternappend((ANY, None))
        elif this == '(':
            group = 1
            name = None
            condgroup = None
            if sourcematch('?'):
                group = 0
                if sourcematch('P'):
                    if sourcematch('<'):
                        name = ''
                        while 1:
                            char = sourceget()
                            if char is None:
                                raise error, 'unterminated name'
                            if char == '>':
                                break
                            name = name + char

                        group = 1
                        if not isname(name):
                            raise error, 'bad character in group name'
                    elif sourcematch('='):
                        name = ''
                        while 1:
                            char = sourceget()
                            if char is None:
                                raise error, 'unterminated name'
                            if char == ')':
                                break
                            name = name + char

                        if not isname(name):
                            raise error, 'bad character in group name'
                        gid = state.groupdict.get(name)
                        if gid is None:
                            raise error, 'unknown group name'
                        subpatternappend((GROUPREF, gid))
                        continue
                    else:
                        char = sourceget()
                        if char is None:
                            raise error, 'unexpected end of pattern'
                        raise error, 'unknown specifier: ?P%s' % char
                elif sourcematch(':'):
                    group = 2
                elif sourcematch('#'):
                    while 1:
                        if source.next is None or source.next == ')':
                            break
                        sourceget()

                    if not sourcematch(')'):
                        raise error, 'unbalanced parenthesis'
                    continue
                elif source.next in ASSERTCHARS:
                    char = sourceget()
                    dir = 1
                    if char == '<':
                        if source.next not in LOOKBEHINDASSERTCHARS:
                            raise error, 'syntax error'
                        dir = -1
                        char = sourceget()
                    p = _parse_sub(source, state)
                    if not sourcematch(')'):
                        raise error, 'unbalanced parenthesis'
                    if char == '=':
                        subpatternappend((ASSERT, (dir, p)))
                    else:
                        subpatternappend((ASSERT_NOT, (dir, p)))
                    continue
                elif sourcematch('('):
                    condname = ''
                    while 1:
                        char = sourceget()
                        if char is None:
                            raise error, 'unterminated name'
                        if char == ')':
                            break
                        condname = condname + char

                    group = 2
                    if isname(condname):
                        condgroup = state.groupdict.get(condname)
                        if condgroup is None:
                            raise error, 'unknown group name'
                    else:
                        try:
                            condgroup = int(condname)
                        except ValueError:
                            raise error, 'bad character in group name'

                else:
                    if source.next not in FLAGS:
                        raise error, 'unexpected end of pattern'
                    while source.next in FLAGS:
                        state.flags = state.flags | FLAGS[sourceget()]

            if group:
                if group == 2:
                    group = None
                else:
                    group = state.opengroup(name)
                if condgroup:
                    p = _parse_sub_cond(source, state, condgroup)
                else:
                    p = _parse_sub(source, state)
                if not sourcematch(')'):
                    raise error, 'unbalanced parenthesis'
                if group is not None:
                    state.closegroup(group)
                subpatternappend((SUBPATTERN, (group, p)))
            else:
                while 1:
                    char = sourceget()
                    if char is None:
                        raise error, 'unexpected end of pattern'
                    if char == ')':
                        break
                    raise error, 'unknown extension'

        elif this == '^':
            subpatternappend((AT, AT_BEGINNING))
        elif this == '$':
            subpattern.append((AT, AT_END))
        elif this and this[0] == '\\':
            code = _escape(source, this, state)
            subpatternappend(code)
        else:
            raise error, 'parser error'

    return subpattern


def parse(str, flags = 0, pattern = None):
    source = Tokenizer(str)
    if pattern is None:
        pattern = Pattern()
    pattern.flags = flags
    pattern.str = str
    p = _parse_sub(source, pattern, 0)
    tail = source.get()
    if tail == ')':
        raise error, 'unbalanced parenthesis'
    elif tail:
        raise error, 'bogus characters at end of regular expression'
    if flags & SRE_FLAG_DEBUG:
        p.dump()
    if not flags & SRE_FLAG_VERBOSE and p.pattern.flags & SRE_FLAG_VERBOSE:
        return parse(str, p.pattern.flags)
    return p


def parse_template(source, pattern):
    s = Tokenizer(source)
    sget = s.get
    p = []
    a = p.append

    def literal(literal, p = p, pappend = a):
        if p and p[-1][0] is LITERAL:
            p[-1] = (LITERAL, p[-1][1] + literal)
        else:
            pappend((LITERAL, literal))

    sep = source[:0]
    if type(sep) is type(''):
        makechar = chr
    else:
        makechar = unichr
    while 1:
        this = sget()
        if this is None:
            break
        if this and this[0] == '\\':
            c = this[1:2]
            if c == 'g':
                name = ''
                if s.match('<'):
                    while 1:
                        char = sget()
                        if char is None:
                            raise error, 'unterminated group name'
                        if char == '>':
                            break
                        name = name + char

                if not name:
                    raise error, 'bad group name'
                try:
                    index = int(name)
                    if index < 0:
                        raise error, 'negative group number'
                except ValueError:
                    if not isname(name):
                        raise error, 'bad character in group name'
                    try:
                        index = pattern.groupindex[name]
                    except KeyError:
                        raise IndexError, 'unknown group name'

                a((MARK, index))
            elif c == '0':
                if s.next in OCTDIGITS:
                    this = this + sget()
                    if s.next in OCTDIGITS:
                        this = this + sget()
                literal(makechar(int(this[1:], 8) & 255))
            elif c in DIGITS:
                isoctal = False
                if s.next in DIGITS:
                    this = this + sget()
                    if c in OCTDIGITS and this[2] in OCTDIGITS and s.next in OCTDIGITS:
                        this = this + sget()
                        isoctal = True
                        literal(makechar(int(this[1:], 8) & 255))
                if not isoctal:
                    a((MARK, int(this[1:])))
            else:
                try:
                    this = makechar(ESCAPES[this][1])
                except KeyError:
                    pass

                literal(this)
        else:
            literal(this)

    i = 0
    groups = []
    groupsappend = groups.append
    literals = [None] * len(p)
    for c, s in p:
        if c is MARK:
            groupsappend((i, s))
        else:
            literals[i] = s
        i = i + 1

    return (groups, literals)


def expand_template(template, match):
    g = match.group
    sep = match.string[:0]
    groups, literals = template
    literals = literals[:]
    try:
        for index, group in groups:
            literals[index] = s = g(group)
            if s is None:
                raise error, 'unmatched group'

    except IndexError:
        raise error, 'invalid group reference'

    return sep.join(literals)