import sys, argparse

from showdocs import annotate, annotators, errors

def main(args):
    ann = annotators.get(args.lang)
    text = sys.stdin.read()
    formatted = ann.format(text, annotate.formatoptions())
    if args.format:
        print formatted
        return

    annotations = ann.annotate(formatted, args.dump)
    if not annotations:
        print 'no annotations'
        return 1
    else:
        for a in annotations:
            begin, end = a.start, a.end
            context = repr(formatted[begin:end])
            if end - begin > 10:
                context = '%r..%r' % (formatted[begin:begin + 5],
                                      formatted[end - 5:end])
            print a, context

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--format', action='store_true')
    parser.add_argument('-l', '--lang', required=True)
    parser.add_argument('-d', '--dump', action='store_true')
    args = parser.parse_args()

    rc = main(args)
    sys.exit(rc or 0)
