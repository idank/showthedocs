import collections, logging, os, codecs

from showdocs import config

ExternalDoc = collections.namedtuple('ExternalDoc', 'contents'.split())

logger = logging.getLogger(__name__)

_filecache = {}

def loadall(root=''):
    if not root:
        root = config.ROOT

    root = os.path.normpath(root)
    extdir = os.path.join(root, 'external')
    if not os.path.exists(extdir):
        raise RuntimeError("can't find directory 'external' under %r" % root)

    staticextdir = os.path.join(config.STATIC_DIR, 'external')

    d = {}
    for root, _, files in os.walk(extdir):
        for name in files:
            if os.path.splitext(name)[1] != '.html':
                continue
            fullpath = os.path.join(root, name)
            logger.info('adding %r to docs filecache', fullpath)
            contents = codecs.open(fullpath, encoding='utf-8').read()
            key = fullpath[len(extdir)+1:]

            d[key] = ExternalDoc(contents)

    return d

_init = False
def initfilecache(root=''):
    global _init
    if _init:
        return
    # Don't cache anything in testing.
    if not config.TEST:
        _init = True

    logger.info('initializing docs filecache')
    _filecache = loadall(root)
    logger.info('done initializing docs filecache')

    return _filecache


class Collection(collections.MutableSet):
    '''A collection represents documentation that was requested by an
    annotator. It is eventually passed to the UI, which returns the HTML in the
    response to a query.'''
    def __init__(self):
        # Use a list so order is preserved.
        self._paths = []

        self._filecache = initfilecache()

    def add(self, path):
        if path not in self._filecache:
            raise ValueError('unknown doc %r' % path)
        if path in self._paths:
            return
        logger.info('adding %r to doc collection', path)
        self._paths.append(path)

    def discard(self, path):
        if path in self._paths:
            self._paths.remove(path)

    def __contains__(self, path):
        return path in self._paths
    def __iter__(self):
        return iter(self._paths)
    def __len__(self):
        return len(self._paths)

    def withcontents(self):
        for path in self._paths:
            yield path, self._filecache[path]
