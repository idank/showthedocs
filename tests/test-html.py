import unittest

from showdocs import structs, annotate, html, errors

Ann = structs.Annotation

class TestHtml(unittest.TestCase):
    def check(self, got, expected):
        self.assertEquals(got, expected,
                          'got, expected\n%s\n\n%s' % (got, expected))

    def test_wrap(self):
        s = '012345'
        a = Ann(0, len(s), 'g', ['c'])
        self.check(
            html.wrap(s, [a]),
            '{a}012345</span>'.format(a=a.format()))

    def test_formaterror(self):
        self.assertRaises(ValueError, errors.ParsingError, '', 'a', 1)

        a = Ann(0, 1, 'error', [structs.decorate.BACK])
        q = '012345'
        e = errors.ParsingError('foo', q, 0)
        wrappedq, wrappede = html.formaterror(q, e)
        self.assertEquals(wrappedq, '{a}0</span>12345'.format(a=a.format()))
        self.assertEquals(wrappede,
                          'at position {a}0</span>: foo.'.format(a=a.format()))

        e = errors.ParsingError('foo <bar>', q, len(q)-1)
        wrappedq, wrappede = html.formaterror(q, e)
        self.assertEquals(wrappedq, '01234{a}5</span>'.format(a=a.format()))
        self.assertEquals(
            wrappede,
            'at position {a}5</span>: foo &lt;bar&gt;.'.format(a=a.format()))

    def test_wrap_newline(self):
        #    01 2345
        s = '0\n 1 2'
        a1 = Ann(0, 4, 'g1', [structs.decorate.UNDER])
        a2 = Ann(3, 4, 'g2', [structs.decorate.UNDER])

        self.check(
            html.wrap(s, [a1, a2]),
            '{a1}0</span>\n {a1}{a2}1</span></span> 2'.format(a1=a1.format(),
                                                              a2=a2.format()))

    def test_wrap_multi1(self):
        s = '012345'
        a1 = Ann(1, 3, 'g1', ['c'])
        a2 = Ann(3, 5, 'g2', ['c'])

        self.check(
            html.wrap(s, [a1, a2]),
            '0{a1}12</span>{a2}34</span>5'.format(a1=a1.format(),
                                                  a2=a2.format()))
        self.check(
            html.wrap(s, [a2, a1]),
            '0{a1}12</span>{a2}34</span>5'.format(a1=a1.format(),
                                                  a2=a2.format()))

    def test_wrap_multi2(self):
        s = '012345'
        a1 = Ann(0, len(s), 'g1', ['c'])
        a2 = Ann(2, 4, 'g2', ['c'])

        self.assertEquals(
            html.wrap(s, [a1, a2]),
            '{a1}01{a2}23</span>45</span>'.format(a1=a1.format(),
                                                   a2=a2.format()))

    def test_wrap_multi3(self):
        s = '012'
        a1 = Ann(0, 1, 'g1', ['c'])
        a2 = Ann(1, 2, 'g2', ['c'])
        a3 = Ann(1, 2, 'g3', ['c'])

        self.check(
            html.wrap(s, [a1, a2, a3]),
            '{a1}0</span>{a2}{a3}1</span></span>2'.format(a1=a1.format(),
                                                          a2=a2.format(),
                                                          a3=a3.format()))

    def test_wrap_overlap(self):
        s = '012345'
        a1 = Ann(1, 3, 'g1', ['c'])
        a2 = Ann(2, 4, 'g2', ['c'])

        self.check(
            html.wrap(s, [a1, a2]),
            '0{a1}1{a2index}2</span></span>{a2}3</span>45'.format(
                a1=a1.format(),
                a2index=a2.format(), #a2.addclass('showdocs-decorate-index-1').format(),
                a2=a2.format()))

    def test_splitnewline(self):
        def a(start, end, lineno):
            return Ann(start, end, 'g', ['c'], lineno)

        s = '01'
        self.assertEquals(html._splitnewline(s, a(0, 2, 0)), [a(0, 2, 0)])

        s = '  01  '
        self.assertEquals(html._splitnewline(s, a(0, 6, 0)), [a(2, 4, 0)])

        s = '0 \n 1 2\n  3'
        self.assertEquals(
            html._splitnewline(s, a(0, 7, 0)), [a(0, 1, 0), a(4, 7, 1)])

        s = '0\n 1 2'
        self.assertEquals(
            html._splitnewline(s, a(0, 6, 0)), [a(0, 1, 0), a(3, 6, 1)])
