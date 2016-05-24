from flask import Flask
from flask.ext.assets import Environment

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
