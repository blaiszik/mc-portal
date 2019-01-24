#!/usr/bin/env python3

from portal.views import app

if __name__ == '__main__':
    app.run(host='0.0.0.0',
            ssl_context=('./ssl/server.crt', './ssl/server.key'))
