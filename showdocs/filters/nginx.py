from lxml.html import builder

from showdocs import structs
from showdocs.filters import common

class DirectiveFilter(common.Filter):
    def process(self):
        for e in self.root.cssselect('div.directive[id]'):
            attr = {'data-showdocs': e.get('id'), 'class': structs.decorate.BLOCK}
            wrapped = builder.E('div', attr)
            eidx = e.getparent().index(e)
            e.getparent()[eidx] = wrapped
            wrapped.append(e)

        for e in self.root.cssselect('div[data-showdocs]'):
            eidx = e.getparent().index(e)
            siblings = []
            for sibling in e.itersiblings():
                if sibling.tag == 'div' and sibling.get('data-showdocs'):
                    break
                # devdocs appends this at the end, stop here.
                if sibling.get('class') == '_attribution':
                    break
                siblings.append(sibling)
            del e.getparent()[eidx + 1:eidx + len(siblings)]
            for s in siblings:
                e.append(s)

        for e in self.root.cssselect('div[data-showdocs] code strong'):
            e.set('data-showdocs', e.text)
            e.classes.add(structs.decorate.BACK)
