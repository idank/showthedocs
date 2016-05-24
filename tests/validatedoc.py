import sys, argparse
import lxml.html
import lxml.etree

from showdocs import docs

def validate(path, contents):
    print 'validating %r' % path
    root = lxml.html.fromstring(contents)
    for t in root.cssselect('[data-showdocs]'):
        errors = []
        g = t.get('data-showdocs')
        trepr = "tag '%s', group '%s'" % (lxml.html.tostring(t)[:20], g)
        classes = t.get('class')
        decorations = [c for c in classes.split() if c.startswith('showdocs')]
        if not decorations:
            errors.append("has no showdocs-decorate-* class, found %r" %
                          classes)
        for e in errors:
            print trepr, e

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()

    collection = docs.Collection()
    for name in args.files:
        collection.add(name)

    for path, externaldoc in collection.withcontents():
        validate(path, externaldoc.contents)
