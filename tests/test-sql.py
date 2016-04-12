import unittest
import sqlparse

from showdocs import structs

from showdocs.annotators import sql

Ann = structs.Annotation

class TestSqlAnnotator(unittest.TestCase):
    def test_calcpositions(self):
        s = 'select * from a where b = c'
        statement = sqlparse.parse(s)[0]
        positions, _ = sql._calcpositions(statement)

        def traverse(node):
            p = positions[node]

            if not node.is_group():
                self.assertEquals(node.value, s[p[0]:p[1]], repr(node))
                return

            pstart = positions[node.tokens[0]][0]
            pend = positions[node.tokens[-1]][1]
            v = s[pstart:pend]
            self.assertEquals(v, s[p[0]:p[1]], repr(node))
            for token in node.tokens:
                traverse(token)

        traverse(statement)
