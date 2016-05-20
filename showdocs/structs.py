import markupsafe

class Annotation(object):
    '''An annotation selects a range in the input, assigns it a group and
    a list of arbitrary class names. Annotations translate to HTML by
    wrapping the range in a <span> tag. The group appears as the value of
    a data-showdocs attribute, likewise for the class names.

    A group is an arbitrary string that identifies the selected range. A group
    is visualized in a special manner in the user interface, depending on the
    decoration applied to it. A group exists to connect a piece of the input to
    its documentation, which will somewhere have a tag with the same
    data-showdocs attribute.

    The list of class names is currently only used to apply decorations.
    A decoration controls the display of the annotation in the UI. The most
    common one is a back decoration, which changes the background color and
    supports things like connecting links when hovering the annotation.'''
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
            markupsafe.escape(self.group), ' '.join(self.classes))

    def decoration(self):
        for c in self.classes:
            if c.startswith(decorateprefix):
                return c

    def addclass(self, c):
        classes = list(self.classes)
        classes.append(c)
        return Annotation(self.start, self.end, self.group, classes)

    def __repr__(self):
        return 'Annotation({start}, {end}, {group!r}, {classes}, {lineno})'.format(
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
