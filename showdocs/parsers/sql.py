import sqlparse
from sqlparse.sql import *
from sqlparse.tokens import *

class TableName(sqlparse.sql.TokenList):
    @property
    def name(self):
        pass
    @property
    def alias(self):
        pass

def _handleinsert(tl):
    fn = tl.token_next_by_instance(0, sqlparse.sql.Function)
    fnidx = tl.token_index(fn)
    if tl.token_prev(fnidx).value.lower() == 'into':
        pass


def parse(text):
    parsed = sqlparse.parse(text)[0]
    if isinstance(parsed, Statement):
        t = parsed.get_type()
        if t == 'INSERT':
            _handleinsert(parsed)

    return parsed

def calcpositions(root, index=0):
    positions = {}

    if root.is_group():
        startindex = index
        for token in root.tokens:
            nestedpos, index = calcpositions(token, index)
            positions.update(nestedpos)
        positions[root] = (startindex, index)
    else:
        positions[root] = (index, index+len(root.value))
        index += len(root.value)

    return positions, index
