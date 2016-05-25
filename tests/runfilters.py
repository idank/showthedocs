#!/usr/bin/env python

import sys, argparse

from showdocs import repos, filters
import showdocs.repos.manager
import showdocs.filters.common

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--lang', required=True)
    args = parser.parse_args()

    text = sys.stdin.read()
    repocls = repos.manager.get(args.lang)
    filterscls = repocls.filters()

    s = filters.common.pipeline(filterscls, text)
    if not s.endswith('\n'):
        s += '\n'
    sys.stdout.write(s)
