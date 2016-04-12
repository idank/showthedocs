import collections, logging, os, codecs

from showdocs import config

ExternalDoc = collections.namedtuple('ExternalDoc', 'contents css'.split())

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
    css = []
    for root, _, files in os.walk(staticextdir):
        for name in files:
            if os.path.splitext(name)[1] != '.css':
                continue
            css.append(os.path.join(root, name)[len(staticextdir)+1:])

    d = {}
    for root, _, files in os.walk(extdir):
        for name in files:
            if os.path.splitext(name)[1] != '.html':
                continue
            fullpath = os.path.join(root, name)
            logger.info('adding %r to docs filecache', fullpath)
            contents = codecs.open(fullpath, encoding='utf-8').read()
            key = fullpath[len(extdir)+1:]

            externalcss = [x for x in css if x.startswith(os.path.dirname(key))]
            d[key] = ExternalDoc(contents, externalcss)

    return d

_init = False
def initfilecache(root=''):
    global _init
    if _init:
        return
    # FIXME
    # _init = True

    logger.info('initializing docs filecache')
    _filecache = loadall(root)
    logger.info('done initializing docs filecache')

    return _filecache


class Collection(collections.MutableSet):
    def __init__(self):
        self._paths = []

        self._filecache = initfilecache()

    def add(self, path):
        if path not in self._filecache:
            raise ValueError('unknown doc %r' % path)
        if path in self._paths:
            return
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
