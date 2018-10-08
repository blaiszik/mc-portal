from flask import (abort, flash, redirect, render_template, request,
                   session, url_for)
import requests
import json
from flask import jsonify

from portal.forms import BoxSubmitForm

try:
    from urllib.parse import urlencode
except:
    from urllib import urlencode

from globus_sdk import RefreshTokenAuthorizer

from portal import app
from portal.decorators import authenticated
from portal.utils import (load_portal_client, get_portal_tokens,
                          get_safe_redirect)

from boxsdk import Client, OAuth2

connect_service = "https://api.materialsdatafacility.org"

@app.route('/', methods=['GET'])
def home():
    """Home page - play with it if you must!"""
    #print(session['tokens'])
    return render_template('home.jinja2')

@app.route('/add', methods=['GET'])
#@authenticated
def add_data():
    """Route for adding data"""
    return render_template('add_data.jinja2')

@app.route('/status/<source_name>', methods=['GET'])
@authenticated
def status(source_name):
    headers = {"Authorization":"Bearer {}".format(session['tokens']['mdf_dataset_submission']['access_token'])}
    r = requests.get("{connect_service}/status/{source}".format(connect_service = connect_service, 
                                                                source=source_name),
                        headers=headers,
                        verify=False)
    return render_template("status.jinja2", status=r.json())

@app.route('/api/convert', methods=['POST'])
def convert():
    data = json.loads(request.data)
    print(data)
    headers = {"Authorization":"Bearer {}".format(session['tokens']['mdf_dataset_submission']['access_token'])}
    print(headers)
    r = requests.post("{connect_service}/convert/".format(connect_service = connect_service),
                      request.data, 
                      headers=headers)
    print(r.json())
    return jsonify(r.json())

@app.route('/api/status/<source_name>', methods=['GET'])
def api_status(source_name):
    headers = {"Authorization":"Bearer {}".format(session['tokens']['mdf_dataset_submission']['access_token'])}
    r = requests.get("{connect_service}/status/{source}".format(connect_service = connect_service, 
                                                                source=source_name),
                        headers=headers)
    return jsonify(r.json())

@app.route('/publish/box', methods=['POST', 'GETcd co'
                                            'sdsddsdsdsdsds'])
def publish_box():
    data = request.form
    print(data)
    oauth = OAuth2(
        client_id='61f7edsvpek2ohzfjw9ft7swde9zim2w',
        client_secret='TcoYuwIZGNEOPDIhI4uqyNophOrqWNJZ'
    )

    access_token, refresh_token = oauth.authenticate(data['auth'])
    box_client = Client(oauth)
    user = box_client.user(data["user_id"]).get()
    print(user["name"])
    file = box_client.file(data["file_id"])
    form = BoxSubmitForm()
    form.name.data = user["name"]

    # return render_template("box_publish.jinja2", form=form)
    return render_template("add_data.jinja2", form=form)

@app.route('/publish/box_prelim', methods=['POST'])
def publish_box_prelim():
    data = request.form
    print(data)
    # return render_template('box_publish.jinja2')
    return """
    <html>
    <script>if (top.location!= self.location) {
   top.location = "/authcallback";
}
    </script>
    <head>
    <h1> Hello world </h1>
    </head>
    </html
    """


@app.route('/signup', methods=['GET'])
def signup():
    """Send the user to Globus Auth with signup=1."""
    return redirect(url_for('authcallback', signup=1))


@app.route('/login', methods=['GET'])
def login():
    """Send the user to Globus Auth."""
    return redirect(url_for('authcallback'))


@app.route('/logout', methods=['GET'])
@authenticated
def logout():
    """
    - Revoke the tokens with Globus Auth.
    - Destroy the session state.
    - Redirect the user to the Globus Auth logout page.
    """
    client = load_portal_client()

    # Revoke the tokens with Globus Auth
    for token, token_type in (
            (token_info[ty], ty)
            # get all of the token info dicts
            for token_info in session['tokens'].values()
            # cross product with the set of token types
            for ty in ('access_token', 'refresh_token')
            # only where the relevant token is actually present
            if token_info[ty] is not None):
        client.oauth2_revoke_token(
            token, additional_params={'token_type_hint': token_type})

    # Destroy the session state
    session.clear()

    redirect_uri = url_for('home', _external=True)

    ga_logout_url = []
    ga_logout_url.append(app.config['GLOBUS_AUTH_LOGOUT_URI'])
    ga_logout_url.append('?client={}'.format(app.config['PORTAL_CLIENT_ID']))
    ga_logout_url.append('&redirect_uri={}'.format(redirect_uri))
    ga_logout_url.append('&redirect_name=Globus Sample Data Portal')

    # Redirect the user to the Globus Auth logout page
    return redirect(''.join(ga_logout_url))


@app.route('/authcallback', methods=['GET', 'POST'])
def authcallback():
    """Handles the interaction with Globus Auth."""
    # If we're coming back from Globus Auth in an error state, the error
    # will be in the "error" query string parameter.
    print("\n\n\n--------------")
    in_box_integration = request.headers['Referer'].endswith("box_prelim")

    print("request.headers "+str(request.headers['Referer']))
    print("So "+str(in_box_integration))

    if 'error' in request.args:
        flash("You could not be logged into the portal: " +
              request.args.get('error_description', request.args['error']))
        return redirect(url_for('home'))

    # Set up our Globus Auth/OAuth2 state
    redirect_uri = "https://f071ee2c.ngrok.io/authcallback"
    #url_for('authcallback', _external=True)

    requested_scopes = ["openid", "profile", "email",
                        "https://auth.globus.org/scopes/c17f27bb-f200-486a-b785-2a25e82af505/connect"]

    client = load_portal_client()
    client.oauth2_start_flow(requested_scopes=requested_scopes,
                            redirect_uri=redirect_uri)

    # If there's no "code" query string parameter, we're in this route
    # starting a Globus Auth login flow.
    if 'code' not in request.args:
        additional_authorize_params = (
            {'signup': 1} if request.args.get('signup') else {})

        auth_uri = client.oauth2_get_authorize_url(
            additional_params=additional_authorize_params)
        return redirect(auth_uri)
    else:
        # If we do have a "code" param, we're coming back from Globus Auth
        # and can start the process of exchanging an auth code for a token.
        code = request.args.get('code')
        tokens = client.oauth2_exchange_code_for_tokens(code)
        print(tokens)

        id_token = tokens.decode_id_token(client)
        session.update(
            tokens=tokens.by_resource_server,
            is_authenticated=True,
            name=id_token.get('name', ''),
            email=id_token.get('email', ''),
            institution=id_token.get('institution', ''),
            primary_username=id_token.get('preferred_username'),
            primary_identity=id_token.get('sub'),
        )

        profile = None
        if in_box_integration:
            next_stop = url_for('home')+"publish/box"
        else:
            next_stop = url_for('home')

        print("Going to "+next_stop)

        if profile:
            name, email, institution = profile

            session['name'] = name
            session['email'] = email
            session['institution'] = institution
        else:
            return redirect(next_stop)

        return redirect(url_for('home'))


