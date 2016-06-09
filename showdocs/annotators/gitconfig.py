import logging
import pyparsing

from showdocs import structs, errors
from showdocs.parsers import gitconfig, ast
from showdocs.annotators import base

logger = logging.getLogger(__name__)

def _reraiseparseexception(e, text):
    # pyparsing usually sets the location to the end of the string,
    # which isn't entirely useful for error messages...
    if e.loc == len(text):
        e.loc -= 1
    raise errors.ParsingError(None, text, e.loc)

class GitConfigAnnotator(base.Annotator):
    alias = ['gitconfig']

    def __init__(self, lang):
        super(GitConfigAnnotator, self).__init__(lang)

    def format(self, text, opts):
        # TODO
        return text

    def visit(self, node):
        # The root node, just visit its parts.
        if node.kind == 'config':
            for n in node.parts:
                self.visit(n)
        elif node.kind == 'section':
            # Add an annotation with group 'section.<name>' where name is the
            # sections' name.
            section = node.name[0].lower()
            subsection = None
            if len(node.name) == 2:
                subsection = node.name[1].lower()
            self._append(node.pos[0], node.pos[1], 'section.%s' % section,
                         [structs.decorate.BLOCK])

            # The alias section is made up of user-defined keys that have no
            # docs.
            if section == 'alias':
                return

            # Annotate the actual keys.
            for n in node.parts:
                if n.kind == 'namevalue':
                    name = n.name
                    group = '%s.%s' % (section, name.value.lower())

                    self._append(name.pos[0], name.pos[1], group,
                                 [structs.decorate.BACK])

    def annotate(self, text, dumptree=False):
        self.docs.add('gitconfig/git-config.html')
        try:
            parsed = gitconfig.loads(text)
        except pyparsing.ParseException, e:
            _reraiseparseexception(e, text)
        assert parsed.kind == 'config'

        if dumptree:
            print parsed.dump()

        self.visit(parsed)
        return self.annotations
