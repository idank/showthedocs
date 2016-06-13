from pyparsing import *

from showdocs.parsers import ast

def _nodeify(name):
    def f(s, l, t):
        return ast.Node(kind=name, pos=(l, l + len(t[0])), value=t[0])
    return f

def _nodeifynamevalue(s, l, t):
    t = t.asList()
    name = t[0]
    value = t[-1]
    if len(t) == 1:
        value = True
    return ast.Node(pos=(l, t[-1].pos[1]),
                    kind='namevalue',
                    name=name,
                    value=value)

def _nodeifysection(s, l, t):
    t = t.asList()
    name = t[0]
    values = t[1]
    return ast.Node(pos=(l, values[-1].pos[1]),
                    kind='section',
                    name=t[0],
                    parts=t[1])

def _nodeifyall(s, l, t):
    sections = t.asList()
    return ast.Node(pos=(l, sections[-1].pos[1]),
                    kind='config',
                    parts=sections)

comment = Combine((Literal(';') | '#') + Optional(restOfLine))
name = Word(alphas, alphanums + '-')
name.setParseAction(_nodeify('name'))
value = Word(printables) + restOfLine
value.setParseAction(_nodeify('value'))
namevalue = name + Optional(Literal('=').suppress() + Optional(value))
namevalue.setParseAction(_nodeifynamevalue)

section_header = Suppress('[') + Group(Word(alphanums + '._') + Optional(
    dblQuotedString)) + Suppress(']')
section_body = Group(ZeroOrMore(namevalue))
section = section_header + Optional(section_body, [])
section.setParseAction(_nodeifysection)

parser = OneOrMore(section)
parser.ignore(comment)
parser.setParseAction(_nodeifyall)
parser.parseWithTabs()

def loads(s):
    return parser.parseString(s).asList()[0]
