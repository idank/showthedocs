import logging

from showdocs import structs
from showdocs.annotators import base

import sqlparse
from sqlparse.sql import *
from sqlparse.tokens import *

logger = logging.getLogger(__name__)

def _calcpositions(root, index=0):
    positions = {}

    if root.is_group():
        startindex = index
        for token in root.tokens:
            nestedpos, index = _calcpositions(token, index)
            positions.update(nestedpos)
        positions[root] = (startindex, index)
    else:
        positions[root] = (index, index+len(root.value))
        index += len(root.value)

    return positions, index

def _issubselect(token):
    if not token.is_group():
        return False
    for item in token.tokens:
        if item.ttype is DML and item.value.upper() == 'SELECT':
            return True
    return False


def _extractfrompart(tokenlist):
    fromseen = False
    for item in tokenlist.tokens:
        if fromseen:
            if _issubselect(item):
                for x in _extractfrompart(item):
                    yield x
            elif item.ttype is Keyword:
                raise StopIteration
            else:
                yield item
        elif item.ttype is Keyword and item.value.upper() == 'FROM':
            fromseen = True


def _extracttableidentifiers(tokens):
    for token in tokens:
        if isinstance(token, IdentifierList):
            for identifier in token.get_identifiers():
                yield identifier
        elif isinstance(token, Identifier):
            yield token
        elif token.ttype is Keyword:
            yield token


class SqlAnnotator(base.Annotator):
    alias = ['sql', 'postgresql', 'mysql']
    knownkeywords = ['select', 'from', 'where']
    groups = base.makegroups('createtable',
                             'table_name',
                             'select',
                             'as',
                             'from',
                             'where', )

    def __init__(self, lang):
        super(SqlAnnotator, self).__init__(lang)
        self.pos = 0

    def format(self, text, opts):
        opts = opts.asobject()
        kwargs = dict(reindent=opts.reindent)
        if opts.keywordcase:
            kwargs['keyword_case'] = 'upper'

        return sqlparse.format(text, **kwargs)

    def _visitcreatetable(self, statement):
        tokens = statement.tokens
        self._append(self.pos[tokens[0]][0],
                     self.pos[tokens[-1]][1], 'createtable',
                     [structs.decorate.BLOCK])

        tablename = statement.token_next_by_instance(0, Identifier)
        if not tablename:
            tablename = statement.token_next_by_instance(0, Function)
            if tablename:
                tablename = tablename.token_next_by_instance(
                    0, Identifier).tokens[0]

        if tablename:
            p = self.pos[tablename]
            self._append(p[0], p[1], 'table_name', [structs.decorate.BACK])

    def _visitselect(self, statement):
        if self.lang == 'postgresql':
            self.docs.add('sql/pg/select.html')
        elif self.lang == 'mysql':
            self.docs.add('sql/mysql/select.html')

        tokens = statement.tokens

        inprogressend = self.pos[tokens[-1]][1]
        inprogress = [self.pos[tokens[0]][0], self.groups.select, [structs.decorate.BLOCK]]

        frompart = statement.token_next_match(0, Keyword, 'FROM')
        if frompart:
            inprogressend = self.pos[frompart][0]
            prev = statement.token_prev(statement.token_index(frompart))
            if prev:
                inprogressend = self.pos[prev][1]

            inprogress.insert(1, inprogressend)
            self._append(*inprogress)

            inprogress = [self.pos[frompart][0], self.groups['from'], [structs.decorate.BLOCK]]
            inprogressend = self.pos[frompart][1]

        inprogress.insert(1, inprogressend)
        self._append(*inprogress)

        wherepart = statement.token_next_by_instance(0, Where)
        if wherepart:
            self._append(self.pos[wherepart][0], self.pos[wherepart][1], 'where', [structs.decorate.BLOCK])


        frompart = list(_extractfrompart(statement))
        for tablename in _extracttableidentifiers(frompart):
            p = self.pos[tablename]
            self._append(p[0], p[1], 'table_name', [structs.decorate.BACK])

    def _visitkeyword(self, token):
        p = self.pos[token]
        self._append(p[0], p[1], token.value.lower(), [structs.decorate.BACK])

    def annotate(self, text, dumptree=False):
        parsed = sqlparse.parse(text)[0]
        if dumptree:
            print parsed._pprint_tree()

        self.pos, _ = _calcpositions(parsed)

        if isinstance(parsed, Statement):
            for token in parsed.flatten():
                if token.is_keyword:
                    self._visitkeyword(token)

            t = parsed.get_type()
            if t == 'CREATE':
                self._visitcreatetable(parsed)
            elif t == 'SELECT':
                self._visitselect(parsed)

        return self.annotations


        #stream = self.lexer.get_tokens_unprocessed(text)

        #for pos, tokentype, value in stream:
        #    if tokentype == Keyword and value.lower() in self.knownkeywords:
        #        annotations.append(structs.Annotation(pos, pos + len(
        #            value), value.lower(), [structs.decorate.BLOCK]))

        #return annotations
