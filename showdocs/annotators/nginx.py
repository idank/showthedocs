import logging
import pyparsing

from showdocs import structs, errors
from showdocs.parsers import nginx
from showdocs.annotators import base

logger = logging.getLogger(__name__)

def _reraiseparseexception(e, text):
    # pyparsing usually sets the location to the end of the string,
    # which isn't entirely useful for error messages...
    if e.loc == len(text):
        e.loc -= 1
    raise errors.ParsingError(None, text, e.loc)

class NginxAnnotator(base.Annotator):
    alias = ['nginx']

    def __init__(self, lang):
        super(NginxAnnotator, self).__init__(lang)

    def format(self, text, opts):
        try:
            return nginx.dumps(nginx.loads(text))
        except pyparsing.ParseException, e:
            _reraiseparseexception(e, text)

    def visit(self, node):
        if node.kind == 'directive':
            assert len(node.parts) >= 2
            key = node.parts[0]
            self._append(key.pos[0], key.pos[1], key.value,
                         [structs.decorate.BACK])
        elif node.kind == 'main':
            for n in node.parts:
                self.visit(n)
        elif node.kind == 'context':
            header = node.header
            headerkey = header.parts[0]
            if headerkey.value in ('server', 'http'):
                self.docs.add('nginx/http/ngx_http_core_module.html')
            self._append(node.pos[0], node.pos[1], headerkey.value,
                         [structs.decorate.BLOCK])
            for n in node.body:
                self.visit(n)


    def annotate(self, text, dumptree=False):
        self.docs.add('nginx/ngx_core_module.html')

        try:
            parsed = nginx.loads(text)
        except pyparsing.ParseException, e:
            _reraiseparseexception(e, text)

        assert parsed.kind == 'main'

        if dumptree:
            print parsed.dump()

        self.visit(parsed)
        return self.annotations
