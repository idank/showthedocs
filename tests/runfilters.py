#!/usr/bin/env python

import sys, argparse

import showdocs.repos.common
import showdocs.filters.common
from showdocs import repos, filters

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--lang', required=True)
    args = parser.parse_args()

    text = sys.stdin.read()
    repocls = repos.common.get(args.lang)
    filterscls = repocls.filters()

    s = filters.common.pipeline(filterscls, text)
    if not s.endswith('\n'):
        s += '\n'
    sys.stdout.write(s)
