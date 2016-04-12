from flask import Flask
from flask.ext.assets import Environment

app = Flask(__name__)
assets = Environment(app)

from showdocs import views

# app.config.from_object(config)
