import unittest

from showdocs.parsers import sql

class TestSqlAnnotator(unittest.TestCase):
    def test_calcpositions(self):
        s = 'select * from a where b = c'
        parsed = sql.parse(s)
        positions, _ = sql.calcpositions(parsed)

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

        traverse(parsed)
