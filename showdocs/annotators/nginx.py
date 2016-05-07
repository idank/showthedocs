import logging

from showdocs import structs
from showdocs.annotators import base, nginxparse

logger = logging.getLogger(__name__)

class NginxAnnotator(base.Annotator):
    alias = ['nginx']

    def __init__(self, lang):
        super(NginxAnnotator, self).__init__(lang)

    def format(self, text, opts):
        return nginxparse.dumps(nginxparse.loads(text))

    def visit(self, node):
        if node.kind == 'directive':
            assert len(node.parts) == 2
            key, value = node.parts
            self._append(key.pos[0], key.pos[1], key.value,
                         [structs.decorate.BACK])
        elif node.kind == 'main':
            for n in node.parts:
                self.visit(n)
        elif node.kind == 'context':
            header = node.header
            headerkey = header.parts[0]
            self._append(node.pos[0], node.pos[1], headerkey.value,
                         [structs.decorate.BLOCK])
            for n in node.body:
                self.visit(n)


    def annotate(self, text, dumptree=False):
        self.docs.add('nginx/ngx_core_module.html')

        parsed = nginxparse.loads(text)
        assert parsed.kind == 'main'

        if dumptree:
            print parsed.dump()

        self.visit(parsed)
        return self.annotations
