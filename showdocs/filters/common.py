import lxml.html

class Filter(object):
    '''Filters are used during postprocessing of docs generation to modify the
    HTML.

    They are constructed in a pipeline, where the output of one is fed as input
    to the next.'''
    def __init__(self, root):
        self.root = root

    def process(self):
        '''process can alter the DOM by mutating self.root, an lxml.Element.'''
        raise NotImplementedError

def pipeline(filters, s):
    # Assume all files are utf8 encoded.
    parser = lxml.html.HTMLParser(encoding='UTF-8')

    # A filter takes a single element, but the input may not have a root
    # element, it might be a list of elements when parsed. Create a 'dummy'
    # parent that wraps the input.
    node = lxml.html.fragment_fromstring(s, create_parent='dummy', parser=parser)
    if not filters:
        return s
    for fcls in filters:
        f = fcls(node)
        modified = f.process()
        node = modified or node

    # Remove the dummy parent created before.
    serialized = lxml.html.tostring(node, encoding='UTF-8')
    return serialized[len('<dummy>'):-len('</dummy>')]
