from flask import redirect, request, session, url_for
from functools import wraps


def authenticated(fn):
    """Mark a route as requiring authentication."""
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        if not session.get('is_authenticated'):

            #Check if token is still valid

            return redirect(url_for('login', next=request.url))

        if request.path == '/logout':
            return fn(*args, **kwargs)

        # if (not session.get('name') or
        #         not session.get('email') or
        #         not session.get('institution')) and request.path != '/':
        #     return redirect(url_for('home', next=request.url))

        return fn(*args, **kwargs)
    return decorated_function
