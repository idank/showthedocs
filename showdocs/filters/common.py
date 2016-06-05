import lxml.html
import lxml.html.builder

class Filter(object):
    '''Filters are used during postprocessing of docs generation to modify the
    HTML.

    They are constructed in a pipeline, where the output of one is fed as input
    to the next.'''
    def __init__(self, context, root):
        self.context = context
        self.root = root

    def process(self):
        '''process can alter the DOM by mutating self.root, an lxml.Element.
        Returning a value overrides self.root and passes that value to
        subsequent filters.'''
        raise NotImplementedError

def pipeline(context, filters, s):
    # Assume all files are utf8 encoded.
    parser = lxml.html.HTMLParser(encoding='UTF-8')

    # A filter takes a single element, but the input may not have a root
    # element, it might be a list of elements when parsed. Create a 'dummy'
    # parent that wraps the input.
    node = lxml.html.fragment_fromstring(s, create_parent='dummy', parser=parser)
    if not filters:
        return s
    for fcls in filters:
        f = fcls(context, node)
        modified = f.process()
        if modified is not None:
            dummy = lxml.html.builder.E('dummy')
            dummy.append(modified)
            node = dummy

    # Remove the dummy parent created before.
    assert node.tag == 'dummy', 'expected element with tag dummy, got %s' % node.tag
    serialized = lxml.html.tostring(node, encoding='UTF-8')
    return serialized[len('<dummy>'):-len('</dummy>')]
