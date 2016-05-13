from flask import Flask
from flask.ext.assets import Environment

app = Flask(__name__)
assets = Environment(app)

from showdocs import views, config

if config.TEST:
    from showdocs import debugviews

app.config.from_object(config)
