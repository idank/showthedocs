import logging

from showdocs import structs
from showdocs.filters import common

logger = logging.getLogger(__name__)

class AnnotatingFilter(common.Filter):
    def process(self):
        i = 0
        for e in self.root.cssselect('code[class]'):
            group = e.text_content()
            if len(group) > 15:
                continue
            e.set('data-showdocs', group.lower())
            e.classes.add(structs.decorate.BACK)
            i += 1
        logger.info('annotated %d elements', i)

        for e in self.root.cssselect('div.REFSECT2[id]'):
            id_ = e.get('id')
            if not id_.startswith('SQL-') or not id_[len('SQL-'):]:
                continue

            group = id_[len('SQL-'):]
            e.set('data-showdocs', group.lower())
            e.classes.add(structs.decorate.BLOCK)
