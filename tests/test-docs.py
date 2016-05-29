import unittest, os

from showdocs import docs

class TestDocs(unittest.TestCase):
    def test_loadall(self):
        d = docs.loadall()
        self.assertTrue('sql/pg/select.html' in d.keys())

    def test_badroot(self):
        self.assertRaises(RuntimeError, docs.loadall, os.path.dirname(__file__))

    def test_collection(self):
        path = 'sql/pg/select.html'

        c = docs.Collection()
        self.assertEquals(len(c), 0)
        self.assertEquals(list(c), [])
        self.assertEquals(list(c.withcontents()), [])

        c.add(path)
        self.assertEquals(len(c), 1)
        self.assertEquals(list(c), [path])
        gotpath, externaldoc = list(c.withcontents())[0]
        self.assertEquals(path, gotpath)
        self.assertTrue(externaldoc.contents > 0)

        c.add(path)
        self.assertEquals(len(c), 1)

        self.assertRaises(ValueError, c.add, 'what')

        c.discard(path)
        self.assertEquals(len(c), 0)
