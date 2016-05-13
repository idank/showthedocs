import os

def _np(p):
    return os.path.normpath(p)

ROOT = _np(os.path.join(os.path.dirname(__file__), '..'))
STATIC_DIR = _np(os.path.join(ROOT, 'showdocs', 'static'))

TEST = True
