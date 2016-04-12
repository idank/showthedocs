from showdocs import docs, structs

def makegroups(*args):
    class container(object):
        def __getitem__(self, k):
            return getattr(self, k)
    c = container()
    for a in args:
        setattr(c, a, a)
    return c

class Annotator(object):
    def __init__(self):
        self.docs = docs.Collection()
        self.annotations = []

    def _append(self, *args):
        self.annotations.append(structs.Annotation(*args))

    @property
    def alias(self):
        raise NotImplementedError
    def format(self, text, opts):
        return text
    def annotate(self, text):
        raise NotImplementedError
