import unittest

from lxml.html import builder

from showdocs import filters, repos
import showdocs.filters.common
import showdocs.repos.common

TESTHTML = '''<div>foo</div>'''

class TestFilters(unittest.TestCase):
    def setUp(self):
        self.context = repos.common.Context()

    def test_no_filters(self):
        filtered = filters.common.pipeline(self.context, [], TESTHTML)
        self.assertEquals(TESTHTML, filtered)

    def test_no_changes(self):
        class noopfilter(filters.common.Filter):
            def process(self):
                pass

        filtered = filters.common.pipeline(self.context, [noopfilter], TESTHTML)
        self.assertEquals(TESTHTML, filtered)

    def test_new_root(self):
        class replacesroot(filters.common.Filter):
            def process(self):
                elem = builder.E('hi')
                elem.text = self.root.cssselect('div')[0].text
                return elem

        filtered = filters.common.pipeline(self.context, [replacesroot], TESTHTML)
        self.assertEquals('<hi>foo</hi>', filtered)

    def test_changes(self):
        class firstfilter(filters.common.Filter):
            def process(self):
                r = self.root
                div = r.cssselect('div')[0]
                div.tag = 'span'

        class secondfilter(filters.common.Filter):
            def process(self):
                r = self.root
                span = r.cssselect('span')[0]
                span.set('data-showdocs', 'bar')

        class thirdfilter(filters.common.Filter):
            def process(self):
                span = self.root.cssselect('span')[0]
                text = span.text
                span.text = ''
                span.append(builder.A(text))

        filtered = filters.common.pipeline(self.context,
            [firstfilter, secondfilter, thirdfilter], TESTHTML)
        self.assertEquals(filtered,
                          '<span data-showdocs="bar"><a>foo</a></span>')
