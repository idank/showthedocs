import logging
import re, copy
import lxml

from lxml.html import builder

from showdocs import structs
from showdocs.filters import common

logger = logging.getLogger(__name__)

class CleanHtmlFilter(common.Filter):
    def process(self):
        for e in self.root.cssselect('.sect1 > h2'):
            if e.text.lower() == 'configuration file':
                return e.getparent()

        raise ValueError("couldn't find 'configuration file' section")

class AnnotatingFilter(common.Filter):
    patterns = {'alias.*': 'section.alias', ' (deprecated)': ''}

    def _addoptionsforsection(self, root, section):
        for e in root.cssselect('dt.hdlist1'):
            self.handled.add(e)
            name = e.text_content().lower()
            self._spanify(e, '%s.%s' % (section, name), structs.decorate.BACK)

    def _spanify(self, e, group, decoration):
        assert e.tag == 'dt', 'expected tag dt, got %r' % e.tag

        # Wrap the inner html of e in a <span> because the <dt> stretches to
        # 100% width which messes up the back decoration.
        span = copy.deepcopy(e)
        span.tag = 'span'
        span.set('data-showdocs', group)
        span.classes.add(decoration)

        attrs = e.items()
        e.clear()
        for k, v in attrs:
            e.set(k, v)
        e.append(span)

    def process(self):
        self.handled = set()

        # Go over top level options.
        for e in self.root.cssselect('.sect2 > .dlist > dl > dt.hdlist1'):
            if e in self.handled:
                continue

            name = e.text_content().lower()

            # Replace any patterns found in name.
            for substring, replacewith in self.patterns.iteritems():
                if substring in name:
                    name = name.replace(substring, replacewith)
                    break

            # Most options take this simple form.
            m = re.match(r'(\w+)\.(<\w+>\.)?(\w+)$', name)
            if m:
                self.handled.add(e)

                # Get rid of the subsection and set the group name to be
                # section.option-name.
                section, subsection, key = m.groups()
                self._spanify(e, '%s.%s' % (section, key),
                              structs.decorate.BACK)
            elif name == 'advice.*':
                self.handled.add(e)
                self._addoptionsforsection(e.getnext(), 'advice')
            else:
                logger.warn("didn't annotate %r", e.text_content())
