import unittest

from lxml.html import builder

import showdocs.filters.common
from showdocs import filters

TESTHTML = '''<div>foo</div>'''

class TestFilters(unittest.TestCase):
    def test_no_filters(self):
        filtered = filters.common.pipeline([], TESTHTML)
        self.assertEquals(TESTHTML, filtered)

    def test_no_changes(self):
        class noopfilter(filters.common.Filter):
            def process(self):
                pass

        filtered = filters.common.pipeline([noopfilter], TESTHTML)
        self.assertEquals(TESTHTML, filtered)

    def test_new_root(self):
        class replacesroot(filters.common.Filter):
            def process(self):
                elem = builder.E('hi')
                elem.text = self.root.cssselect('div')[0].text
                return elem

        filtered = filters.common.pipeline([replacesroot], TESTHTML)
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

        filtered = filters.common.pipeline(
            [firstfilter, secondfilter, thirdfilter], TESTHTML)
        self.assertEquals(filtered,
                          '<span data-showdocs="bar"><a>foo</a></span>')
