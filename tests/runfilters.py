#!/usr/bin/env python

import sys, argparse

from showdocs import repos, filters
import showdocs.repos.manager
import showdocs.filters.common

def testcontext():
    context = repos.common.Context()
    context.current_url = 'http://localhost/a/b/test.html'
    return context

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--lang', required=True)
    args = parser.parse_args()

    text = sys.stdin.read()
    repocls = repos.manager.get(args.lang)
    filterscls = repocls.filters()

    s = filters.common.pipeline(testcontext(), filterscls, text)
    if not s.endswith('\n'):
        s += '\n'
    sys.stdout.write(s)
