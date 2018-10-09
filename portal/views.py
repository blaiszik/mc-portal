from boxsdk import OAuth2, Client
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


connect_service = "https://18.233.85.14"

@app.route('/', methods=['GET'])
def home():
    """Home page - play with it if you must!"""
    #print(session['tokens'])
    return render_template('home.jinja2')

@app.route('/add', methods=['GET'])
@authenticated
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
                      headers=headers, 
                      verify=False)
    print(r.json())
    return jsonify(r.json())

@app.route('/api/status/<source_name>', methods=['GET'])
def api_status(source_name):
    headers = {"Authorization":"Bearer {}".format(session['tokens']['mdf_dataset_submission']['access_token'])}
    r = requests.get("{connect_service}/status/{source}".format(connect_service = connect_service, 
                                                                source=source_name),
                        headers=headers, 
                        verify=False)
    return jsonify(r.json())


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


@app.route('/publish/box', methods=['POST', 'GET'])
def publish_box():
    data = request.form
    print(data)

    if not session.get('is_authenticated'):
        return redirect(
            url_for('authcallback', next=request.url, _scheme="https",
                    _external=True,
                    box_integration=True,
                    box_auth = data['auth'],
                    box_file_id = data['file_id'],
                    box_user_id = data['user_id']
                    ))

    oauth = OAuth2(
        client_id='61f7edsvpek2ohzfjw9ft7swde9zim2w',
        client_secret='TcoYuwIZGNEOPDIhI4uqyNophOrqWNJZ'
    )

    box_auth = data.get("auth", request.args.get("box_auth"))
    box_file_id = data.get("file_id", request.args.get("file_id"))
    box_user_id = data.get("user_id", request.args.get("user_id"))

    access_token, refresh_token = oauth.authenticate(box_auth)
    box_client = Client(oauth)
    user = box_client.user(box_user_id).get()
    print(user["name"])
    # file = box_client.file(box_file_id).get()
    file=box_client.folder(box_file_id).get()
    form = BoxSubmitForm()
    form.name.data = user["name"]
    form.titleInput.data = file["name"]
    return render_template('submit_box.jinja2', form=form)

@app.route('/authcallback', methods=['GET'])
def authcallback():
    """Handles the interaction with Globus Auth."""
    # If we're coming back from Globus Auth in an error state, the error
    # will be in the "error" query string parameter.

    in_box_integration = request.args.get("box_integration", False)

    if in_box_integration:
        state = {
            "auth": request.args.get("box_auth"),
            "file_id": request.args.get("box_file_id"),
            "user_id": request.args.get("box_user_id")
        }
    else:
        state = {}



    if 'error' in request.args:
        flash("You could not be logged into the portal: " +
              request.args.get('error_description', request.args['error']))
        return redirect(url_for('home'))

    # Set up our Globus Auth/OAuth2 state
    # redirect_uri = "https://connect.materialsdatafacility.org/authcallback"
    redirect_uri = "https://a4a0ee44.ngrok.io/authcallback?in_box="+str(in_box_integration)

    #url_for('authcallback', _external=True)

    requested_scopes = ["openid", "profile", "email",
                        "https://auth.globus.org/scopes/c17f27bb-f200-486a-b785-2a25e82af505/connect"]

    client = load_portal_client()
    client.oauth2_start_flow(requested_scopes=requested_scopes,
                            redirect_uri=redirect_uri, state=json.dumps(state))

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

        if in_box_integration:
            state = request.args.get("state")
            s = json.loads(state)

            next_stop = url_for('publish/box', _scheme="https",
                                _external=True,
                                box_auth=s['auth'],
                                box_file_id=s['file_id'],
                                box_user_id=s['user_id'])
        else:
            next_stop = url_for('home', _scheme="https", _external=True)

        return redirect(next_stop)


