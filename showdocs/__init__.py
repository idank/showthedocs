import os, logging

logger = logging.getLogger(__name__)

from flask import Flask
from flask.ext.assets import Environment, Bundle

app = Flask(__name__)
assets = Environment(app)

from showdocs import views, config

if config.TEST:
    from showdocs import debugviews

app.config.from_object(config)

_addedhandlers = False
def setuplogging():
    import logging, sys
    root = logging.getLogger('showdocs')
    root.setLevel(logging.INFO)

    if not config.LOG:
        root.setLevel(logging.CRITICAL)
        return

    global _addedhandlers
    if _addedhandlers:
        return
    _addedhandlers = True

    formatter = logging.Formatter('%(asctime)s %(name)s[%(levelname)s] %(message)s')
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)
    root.setLevel(logging.INFO)
    root.addHandler(sh)

setuplogging()

def configureassets():
    staticextdir = os.path.join(config.STATIC_DIR, 'external')
    scss = []
    for root, _, files in os.walk(staticextdir):
        for name in files:
            path, ext = os.path.splitext(name)
            if ext != '.scss':
                continue
            type_ = os.path.splitext(path)[0]
            fullpath = os.path.join(root, name)
            staticrelative = os.path.relpath(fullpath, config.STATIC_DIR)
            output = os.path.join('external', path)
            bundle = Bundle(staticrelative, filters='scss', output=output)
            assetname = type_ + '_scss'
            assets.register(assetname, bundle)
            logger.info('bundled %s, output path %s, registered as %s',
                        staticrelative, output, assetname)

configureassets()
