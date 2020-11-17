"""
    Crop Frequency API
    ~~~~~

    REST API to analyze crop frequencies

    :copyright: n/a
    :license: n/a
    :author: James Raines (jraines521@gmail.com)
    :contributors: n/a

"""
__version__ = '0.0.1'
__all__ = ['app', 'blueprints']

from flask import Flask, render_template
from . import blueprints


app = Flask(__name__, template_folder='templates')
app.register_blueprint(blueprints.cropfrequency_blueprint)

# intialize index
@app.route('/')
def index():
    return {'index': 'Crop Frequency API'}

# error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
