import logging

from showdocs import structs
from showdocs.annotators import base

from showdocs import parsers
from showdocs.parsers import sql

import sqlparse
from sqlparse.sql import *
from sqlparse.tokens import *

logger = logging.getLogger(__name__)

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
            self.docs.add('postgres/sql-select.html')
        elif self.lang == 'mysql':
            self.docs.add('mysql/select.html')

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

    def _visitkeyword(self, flat, i, token):
        # TODO: move this to the parser
        # We get two tokens for a GROUP BY, merge them to one annotation.
        groupby = flat[i:i+1]
        if token.value.lower() in ('group', 'order'):
            j = i+1
            while j < len(flat) and flat[j].is_whitespace():
                j += 1
            if j < len(flat) and flat[j].value.lower() == 'by':
                p1 = self.pos[token]
                p2 = self.pos[flat[j]]
                self._append(p1[0], p2[1], '%s by' % token.value.lower(),
                             [structs.decorate.BACK])
                return
        elif token.value.lower() == 'by':
            return

        p = self.pos[token]
        self._append(p[0], p[1], token.value.lower(), [structs.decorate.BACK])

    def annotate(self, text, dumptree=False):
        parsed = parsers.sql.parse(text)
        if dumptree:
            print parsed._pprint_tree()

        self.pos, _ = parsers.sql.calcpositions(parsed)

        if isinstance(parsed, Statement):
            flat = list(parsed.flatten())
            for i, token in enumerate(flat):
                if token.is_keyword:
                    self._visitkeyword(flat, i, token)

            t = parsed.get_type()
            if t == 'CREATE':
                self._visitcreatetable(parsed)
            elif t == 'SELECT':
                self._visitselect(parsed)

        return self.annotations
