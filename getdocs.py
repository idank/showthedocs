#!/usr/bin/env python

"""getdocs

Usage:
  getdocs.py list
  getdocs.py build [--lang=<lang>] [--config=<path>]
  getdocs.py (-h | --help)
  getdocs.py --version

Options:
  -h --help         Show this screen.
  --version         Show version.
  --lang=<lang>     Language to build [default: all].
  --config=<path>   Update default config with the given one.

"""
import sys, os
from docopt import docopt

import showdocs
from showdocs import config, repos, filters, errors
from showdocs.repos import *

import showdocs.repos.common
import showdocs.repos.manager

def build(args):
    reposcls = set(repos.common.registered.values())
    if args['--lang']:
        lang = args['--lang']
        try:
            langrepo = repos.manager.get(lang)
            reposcls &= set([langrepo])
        except ValueError, e:
            print str(e)
            return 1

    if not os.path.exists(config.STAGING_DIR):
        os.mkdir(config.STAGING_DIR)
    if not os.path.exists(config.EXTERNAL_DIR):
        os.mkdir(config.EXTERNAL_DIR)

    manager = repos.manager.RepositoryManager(reposcls, config.STAGING_DIR,
                                              config.EXTERNAL_DIR)
    manager.generate()

def main(args):
    if args['--config']:
        import imp
        imp.load_source('showdocs.testconfig', args['--config'])

    if args['list']:
        for name in repos.manager.listrepos():
            print name
    elif args['build']:
        return build(args)
    else:
        docopt.usage()
        return 1

if __name__ == '__main__':
    arguments = docopt(__doc__, version='getdocs')
    sys.exit(main(arguments))
