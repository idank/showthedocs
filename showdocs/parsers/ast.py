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
        if not isinstance(other, Node):
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
