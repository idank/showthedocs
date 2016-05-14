import sys, argparse

from showdocs import docs

from bs4 import BeautifulSoup

def validate(path, contents):
    print 'validating %r' % path
    soup = BeautifulSoup(contents, 'html.parser')
    for t in soup.select('[data-showdocs]'):
        errors = []
        g = t['data-showdocs']
        trepr = "tag '%s', group '%s'" % (repr(t)[:20], g)
        classes = t.get('class', [])
        decorations = [c for c in classes if c.startswith('showdocs')]
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
