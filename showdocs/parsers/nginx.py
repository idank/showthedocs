import string, pprint

from pyparsing import (Literal, White, Word, alphanums, CharsNotIn, Forward,
                       Group, SkipTo, LineEnd, Optional, OneOrMore, ZeroOrMore,
                       pythonStyleComment, quotedString, Or)

class Node(object):
    def __init__(self, **kwargs):
        assert 'kind' in kwargs
        self.__dict__.update(kwargs)

    def dump(self, indent='  '):
        return _dump(self, indent)

    def __repr__(self):
        chunks = []
        d = dict(self.__dict__)
        kind = d.pop('kind')
        for k, v in sorted(d.items()):
            chunks.append('%s=%r' % (k, v))
        return '%sNode(%s)' % (kind.title(), ' '.join(chunks))

    def __eq__(self, other):
        if not isinstance(other, node):
            return False
        return self.__dict__ == other.__dict__


def _dump(tree, indent='  '):
    def _format(n, level=0):
        if isinstance(n, Node):
            d = dict(n.__dict__)
            kind = d.pop('kind')
            if kind == 'list' and level > 0:
                level = level + 1
            fields = []
            v = d.pop('pos', None)
            if v:
                fields.append(('pos', repr(v)))
            for k, v in sorted(d.items()):
                if not v or k == 'parts':
                    continue
                llevel = level
                if isinstance(v, Node):
                    llevel += 1
                    fields.append((k, '\n' + (indent * llevel) + _format(v, llevel)))
                else:
                    fields.append((k, _format(v, level)))
            if kind == 'function':
                fields = [f for f in fields if f[0] not in ('name', 'body')]
            v = d.pop('parts', None)
            if v:
                fields.append(('parts', _format(v, level)))
            return ''.join([
                '%sNode' % kind.title(),
                '(',
                ', '.join(('%s=%s' % field for field in fields)),
                ')'])
        elif isinstance(n, (tuple, list)):
            lines = ['[']
            lines.extend((indent * (level + 1) + _format(x, level + 1) + ','
                         for x in n))
            if len(lines) > 1:
                lines.append(indent * (level) + ']')
            else:
                lines[-1] += ']'
            return '\n'.join(lines)
        return repr(n)

    if not isinstance(tree, Node):
        raise TypeError('expected Node, got %r' % tree.__class__.__name__)
    return _format(tree)


def _nodeifyset(s, l, t):
    return Node(pos=(l, t[-1].pos[1]), kind='set', parts=t[:-1])

def _nodeifydirective(s, l, t):
    assert len(t) >= 3
    return Node(pos=(l, t[-1].pos[1]), kind='directive', parts=t[:-1])

def _nodeifyif(s, l, t):
    assert len(t) == 5
    return Node(pos=(l, t[-1].pos[1]),
                kind='if',
                keyword=t[0],
                condition=t[1],
                body=t[3].asList())

def _nodeifycontext(s, l, t):
    assert len(t) == 1
    t = t[0]
    assert len(t) == 4
    header = t[0].asList()
    body = t[2].asList()

    return Node(pos=(l, t[-1].pos[1]),
                kind='context',
                header=Node(kind='contextheader',
                            parts=header),
                body=body)

def _nodeifymain(s, l, t):
    return Node(pos=(l, t[-1].pos[1]), kind='main', parts=t.asList())

def _nodeify(name):
    def f(s, l, t):
        return Node(kind=name, pos=(l, l + len(t[0])), value=t[0])
    return f

class NginxParser(object):
    '''A class for parsing nginx config files.

    Based on https://github.com/fatiherikli/nginxparser'''

    # constants
    left_bracket = Literal("{").setParseAction(_nodeify('punctuation'))
    right_bracket = Literal("}").setParseAction(_nodeify('punctuation'))
    semicolon = Literal(";").setParseAction(_nodeify('punctuation'))
    space = White().suppress()
    key = Word(alphanums + "_/").setParseAction(_nodeify('key'))
    value = CharsNotIn("{};, ").setParseAction(_nodeify('value'))
    value2 = CharsNotIn(";" + string.whitespace).setParseAction(_nodeify('value'))
    quotedstring = quotedString.setParseAction(_nodeify('value'))
    location = CharsNotIn("{};," + string.whitespace).setParseAction(_nodeify('location'))
    ifword = Literal("if").setParseAction(_nodeify('keyword'))
    setword = Literal("set").setParseAction(_nodeify('keyword'))

    # modifier for location uri [ = | ~ | ~* | ^~ ]
    modifier = (Literal("=") | Literal("~*") | Literal("~") |
                Literal("^~")).setParseAction(_nodeify('modifier'))

    # rules
    directive = (key + ZeroOrMore(space + Or([value, quotedstring])) +
                 semicolon).setParseAction(_nodeifydirective)
    setblock = (setword + OneOrMore(space + value2) + semicolon).setParseAction(_nodeifyset)
    block = Forward()
    ifblock = Forward()
    subblock = Group(ZeroOrMore(setblock | directive | block | ifblock))
    # TODO: parse if condition
    ifblock = (ifword + SkipTo('{') + left_bracket + subblock + right_bracket).setParseAction(_nodeifyif)

    block << Group(Group(key + Optional(space + modifier) + Optional(
        space + location)) + left_bracket + Group(ZeroOrMore(
            directive | block | ifblock | setblock)) +
                   right_bracket).setParseAction(_nodeifycontext)

    script = OneOrMore(directive | block).ignore(
        pythonStyleComment).setParseAction(_nodeifymain)

    def __init__(self, source):
        self.source = source

    def parse(self):
        """
        Returns the parsed tree.
        """
        return self.script.parseString(self.source)

    def as_list(self):
        """
        Returns the list of tree.
        """
        return self.parse().asList()


class NginxDumper(object):
    """A class that dumps nginx configuration from the provided node."""
    def __init__(self, root, indentation=4):
        assert root.kind == 'main'

        self.root = root
        self.indentation = indentation

    def dump(self, node, current_indent=0, spacer=' '):
        """
        Iterates the dumped nginx AST.
        """
        indentation = spacer * current_indent
        if node.kind == 'main':
            for n in node.parts:
                for l in self.dump(n, current_indent):
                    yield l
        elif node.kind == 'context':
            yield ''
            yield indentation + spacer.join([n.value for n in node.header.parts]) + ' {'
            for n in node.body:
                for l in self.dump(n, current_indent + self.indentation):
                    yield l
            yield indentation + '}'
        elif node.kind == 'directive':
            yield indentation + spacer.join([n.value for n in node.parts]) + ';'
        elif node.kind == 'if':
            yield ''
            yield indentation + 'if' + spacer + node.condition.strip() + spacer + '{'
            for n in node.body:
                for l in self.dump(n, current_indent + self.indentation):
                    yield l
            yield indentation + '}'
        elif node.kind == 'set':
            yield indentation + spacer.join([n.value for n in node.parts]) + ';'
        else:
            raise ValueError('unknown kind %r' % node.kind)


    def as_string(self):
        return '\n'.join(self.dump(self.root))


def loads(source):
    return NginxParser(source).as_list()[0]

def dumps(root, indentation=4):
    return NginxDumper(root, indentation).as_string()
