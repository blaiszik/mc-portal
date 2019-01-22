from flask import Flask


__author__ = 'Globus Team <info@globus.org>'

app = Flask(__name__)
app.config.from_pyfile('portal.conf')

import portal.views  # noqa:E402,F401 (import not at top, unused)
