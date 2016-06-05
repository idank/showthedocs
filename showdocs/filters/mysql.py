import logging
from lxml.html import builder

from showdocs import structs
from showdocs.filters import common

logger = logging.getLogger(__name__)

class CleanHtmlFilter(common.Filter):
    def process(self):
        newroot = self.root.cssselect('#docs-body')
        if len(newroot) != 1:
            raise ValueError('need #docs-body in html')

        self.root = newroot[0]
        return self.root

class AnnotatingFilter(common.Filter):
    def process(self):
        for e in self.root.cssselect('code[class]'):
            # Handle whitespace and newlines in the text.
            group = ' '.join(e.text_content().split())
            group = group.replace('\n', '')
            if len(group) > 15:
                continue
            e.set('data-showdocs', group.lower())
            e.classes.add(structs.decorate.BACK)

        for e in self.root.cssselect('code'):
            text = e.text_content()
            group = None
            if text == 'table_references':
                group = 'table_name'
            if group:
                e.set('data-showdocs', group.lower())
                e.classes.add(structs.decorate.BACK)
