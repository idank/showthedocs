class Annotation(object):
    def __init__(self, start, end, group, classes, lineno=0):
        if end <= start:
            raise ValueError('end smaller than start')
        if not isinstance(classes, list):
            raise ValueError('classes needs to be a list')

        self.start = start
        self.end = end
        self.group = group
        self.classes = classes
        self.lineno = lineno

    def format(self):
        return '<span data-showdocs="%s" class="%s">' % (
            self.group, ' '.join(self.classes))

    def decoration(self):
        for c in self.classes:
            if c.startswith(decorateprefix) and 'index' not in c:
                return c

    def addclass(self, c):
        classes = list(self.classes)
        classes.append(c)
        return Annotation(self.start, self.end, self.group, classes)

    def __repr__(self):
        return 'Annotation({start}, {end}, {group}, {classes}, {lineno})'.format(
            **self.__dict__)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

decorateprefix = 'showdocs-decorate'
class decorate(object):
    BLOCK = '%s-block' % decorateprefix
    UNDER = '%s-under' % decorateprefix
    BACK = '%s-back' % decorateprefix
