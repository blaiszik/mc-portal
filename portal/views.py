import logging

from flask import (flash, Flask, jsonify, redirect, render_template,
                   request, session, url_for)
import globus_sdk
import mdf_connect_client
import json

from portal.decorators import authenticated


app = Flask(__name__)
app.config.from_pyfile("portal.conf")
app.url_map.strict_slashes = False

# Set up root logger
logger = logging.getLogger("mc_portal")
logger.setLevel(app.config["LOG_LEVEL"])
logger.propagate = False
# Set up formatters
logfile_formatter = logging.Formatter("[{asctime}] [{levelname}] {name}: {message}",
                                      style='{',
                                      datefmt="%Y-%m-%d %H:%M:%S")
# Set up handlers
logfile_handler = logging.FileHandler(app.config["LOG_FILE"], mode='a')
logfile_handler.setFormatter(logfile_formatter)

logger.addHandler(logfile_handler)

logger.info("\n\n==========Connect Portal started==========\n")


@app.route('/', methods=['GET'])
def home():
    """Home page - play with it if you must!"""
    return render_template('home.jinja2')


@app.route('/add', methods=['GET'])
@authenticated
def add_data():
    """Route for adding data"""
    return render_template('add_data.jinja2')


@app.route('/submissions', methods=['GET'])
@authenticated
def submissions():
     # Make MDFCC
    try:
        logger.debug("Creating MDFCC for status")
        auth_client = globus_sdk.ConfidentialAppAuthClient(
                       app.config['PORTAL_CLIENT_ID'], app.config['PORTAL_CLIENT_SECRET'])
        mdf_authorizer = globus_sdk.RefreshTokenAuthorizer(
                                        session["tokens"]["mdf_dataset_submission"]
                                               ["refresh_token"],
                                        auth_client)
        mdfcc = mdf_connect_client.MDFConnectClient(service_instance=app.config["MDFCC_SERVICE"],
                                                    authorizer=mdf_authorizer)
    except Exception as e:
        logger.error("Status MDFCC init: {}".format(repr(e)))
        json_res = {
            "success": False,
            "error": "Unable to initialize client."
        }
    else:
        try:
            logger.debug("Requesting Submissions")
            json_res = mdfcc.check_all_submissions(raw=True)
        except Exception as e:
            logger.error("Check Submissions request: {}".format(repr(e)))
            json_res = {
                "success": False,
                "error": "Status request failed."
            }

    # return (jsonify(json_res), status_code)
    return render_template("submissions.jinja2", res=json_res)
    pass

@app.route('/status/<source_name>', methods=['GET'])
@authenticated
def status(source_name):
    # Make MDFCC
    try:
        logger.debug("Creating MDFCC for status")
        auth_client = globus_sdk.ConfidentialAppAuthClient(
                       app.config['PORTAL_CLIENT_ID'], app.config['PORTAL_CLIENT_SECRET'])
        mdf_authorizer = globus_sdk.RefreshTokenAuthorizer(
                                        session["tokens"]["mdf_dataset_submission"]
                                               ["refresh_token"],
                                        auth_client)
        mdfcc = mdf_connect_client.MDFConnectClient(service_instance=app.config["MDFCC_SERVICE"],
                                                    authorizer=mdf_authorizer)
    except Exception as e:
        logger.error("Status MDFCC init: {}".format(repr(e)))
        json_res = {
            "success": False,
            "error": "Unable to initialize client."
        }
    else:
        try:
            logger.debug("Requesting status")
            json_res = mdfcc.check_status(source_name, raw=True)
        except Exception as e:
            logger.error("Status request: {}".format(repr(e)))
            json_res = {
                "success": False,
                "error": "Status request failed."
            }

    # return (jsonify(json_res), status_code)
    return render_template("status.jinja2", status_res=json_res)


@app.route('/curate/', methods=['GET'])
@authenticated
def curate():
    return render_template('curate.jinja2')

    # # Make MDFCC
    # try:
    #     logger.debug("Creating MDFCC for status")
    #     auth_client = globus_sdk.ConfidentialAppAuthClient(
    #                    app.config['PORTAL_CLIENT_ID'], app.config['PORTAL_CLIENT_SECRET'])
    #     mdf_authorizer = globus_sdk.RefreshTokenAuthorizer(
    #                                     session["tokens"]["mdf_dataset_submission"]
    #                                            ["refresh_token"],
    #                                     auth_client)
    #     mdfcc = mdf_connect_client.MDFConnectClient(service_instance=app.config["MDFCC_SERVICE"],
    #                                                 authorizer=mdf_authorizer)
    # except Exception as e:
    #     logger.error("Status MDFCC init: {}".format(repr(e)))
    #     json_res = {
    #         "success": False,
    #         "error": "Unable to initialize client."
    #     }
    # else:
    #     try:
    #         logger.debug("Requesting status")
    #         json_res = mdfcc.check_status(source_name, raw=True)
    #     except Exception as e:
    #         logger.error("Status request: {}".format(repr(e)))
    #         json_res = {
    #             "success": False,
    #             "error": "Status request failed."
    #         }

    # # return (jsonify(json_res), status_code)
    # return render_template("status.jinja2", status_res=json_res)

@app.route('/api/convert', methods=['POST'])
def convert():
    # Make MDFCC
    logger.debug(request.get_json())
    logger.debug(request.get_json().get('test'))
    logger.debug(request.get_json().get('passthrough'))


    try:
        logger.debug("Creating MDFCC for submission")
        auth_client = globus_sdk.ConfidentialAppAuthClient(
                       app.config['PORTAL_CLIENT_ID'], app.config['PORTAL_CLIENT_SECRET'])
        mdf_authorizer = globus_sdk.RefreshTokenAuthorizer(
                                        session["tokens"]["mdf_dataset_submission"]
                                               ["refresh_token"],
                                        auth_client)
        mdfcc = mdf_connect_client.MDFConnectClient(service_instance=app.config["MDFCC_SERVICE"],
                                                    authorizer=mdf_authorizer)
    except Exception as e:
        logger.error("API Convert MDFCC init: {}".format(e))
        return (jsonify({
            "success": False,
            "error": "Unable to initialize dataset submission client."
        }), 500)

    try:
        logger.debug("Assembling submission")
        metadata = request.get_json()
        if metadata.get("dc"):
            mdfcc.create_dc_block(**metadata["dc"])
        if metadata.get("acl"):
            mdfcc.set_acl(metadata["acl"])
        if metadata.get("source_name"):
            mdfcc.set_source_name(metadata["source_name"])
        if metadata.get("repositories"):
            mdfcc.add_repositories(metadata["respositories"])
        if metadata.get("projects") or metadata.get("project"):
            proj = metadata.get("projects", metadata.get("project", {}))
            mdfcc.set_project_block(**proj)
        if metadata.get("mrr"):
            mdfcc.create_mrr_block(metadata["mrr"])
        if metadata.get("custom"):
            mdfcc.set_custom_block(metadata["custom"])
        if metadata.get("custom_descriptions") or metadata.get("custom_desc"):
            mdfcc.set_custom_descriptions(metadata.get("custom_descriptions",
                                                       metadata.get("custom_desc", {})))
        if metadata.get("data"):
            mdfcc.add_data_source(metadata["data"])
        
        if metadata.get("contacts"):
            def format_contacts(contacts):
                formatted_contacts = []
                if type(contacts) is list:
                    formatted_contacts = [{"contributorName":str(c), "contributorType":"ContactPerson"} for c in contacts]
                else:
                    formatted_contacts = []
                return formatted_contacts
            contacts = {"contributors":format_contacts(metadata.get("contacts"))}
            logger.error(contacts)
            logger.error(metadata.get("contacts"))
            mdfcc.dc.update(contacts)

        if metadata.get("index"):
            if not isinstance(metadata["index"], list):
                metadata["index"] = [metadata["index"]]
            for index in metadata["index"]:
                mdfcc.add_index(**index)
        if metadata.get("conversion_config"):
            mdfcc.set_conversion_config(metadata["conversion_config"])
        if metadata.get("service") or metadata.get("services"):
            # services must be either:
            # 1) list of dict, each dict contains args for an add_service() call
            # 2) one dict, each key is a service, each value is bool/dict of service options
            services = metadata.get("services", metadata.get("service", {}))
            if isinstance(services, list):
                for serv in services:
                    mdfcc.add_service(**serv)
            elif isinstance(services, dict):
                for key, val in services.items():
                    mdfcc.add_service(key, val)
            else:
                raise TypeError("Invalid service entry ({}): {}".format(type(services), services))
        mdfcc.set_passthrough(metadata.get("passthrough", False))
        mdfcc.set_test(metadata.get("test", False))
        mdfcc.add_organization(metadata.get("organizations", "MDF Open"))
        mdfcc.set_source_name(metadata.get("source_name", ""))

    except Exception as e:
        logger.error("API Convert assembly: {}".format(repr(e)))
        return (jsonify({
            "success": False,
            "error": "Dataset submission invalid: {}".format(e)
        }), 400)

    try:
        logger.debug(json.dumps(mdfcc.get_submission()))
        res = mdfcc.submit_dataset(metadata.get("update", False))
        logger.debug("== Dataset Submission ==")
        logger.debug(res)
    except Exception as e:
        logger.error("API Convert submission: {}".format(repr(e)))
        return (jsonify({
            "success": False,
            "error": "Submission to MDF Connect failed: {}".format(e)
        }), 500)

    return (jsonify(res), res["status_code"])


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
    logger.debug("Logging user out")

    try:
        auth_client = globus_sdk.ConfidentialAppAuthClient(
                    app.config['PORTAL_CLIENT_ID'], app.config['PORTAL_CLIENT_SECRET'])

        # Revoke the tokens with Globus Auth
        for token, token_type in (
                (token_info[ty], ty)
                # get all of the token info dicts
                for token_info in session['tokens'].values()
                # cross product with the set of token types
                for ty in ('access_token', 'refresh_token')
                # only where the relevant token is actually present
                if token_info[ty] is not None):
            auth_client.oauth2_revoke_token(
                token, additional_params={'token_type_hint': token_type})

        # Destroy the session state
        session.clear()

        redirect_uri = url_for('home', _external=True)
        print(redirect_uri)

        ga_logout_url = []
        ga_logout_url.append(app.config['GLOBUS_AUTH_LOGOUT_URI'])
        ga_logout_url.append('?client={}'.format(app.config['PORTAL_CLIENT_ID']))
        ga_logout_url.append('&redirect_uri={}'.format(redirect_uri))
        ga_logout_url.append('&redirect_name=Globus Sample Data Portal')
    except Exception as e:
        logger.error("Unable to logout user: {}".format(repr(e)))
        flash("Unable to log you out of Globus.")

    # Redirect the user to the Globus Auth logout page
    return redirect(''.join(ga_logout_url))


@app.route('/authcallback', methods=['GET'])
def authcallback():
    """Handles the interaction with Globus Auth."""
    try:
        # If we're coming back from Globus Auth in an error state, the error
        # will be in the "error" query string parameter.
        if 'error' in request.args:
            err_text = request.args.get('error_description', request.args['error'])
            logger.debug("Authcallback error: {}".format(err_text))
            flash("You could not be logged into the portal: {}".format(err_text))
            return redirect(url_for('home'))

        # Set up our Globus Auth/OAuth2 state
        requested_scopes = ["openid", "profile", "email",
                            ("https://auth.globus.org/scopes/"
                             "c17f27bb-f200-486a-b785-2a25e82af505/connect")]

        auth_client = globus_sdk.ConfidentialAppAuthClient(
                       app.config['PORTAL_CLIENT_ID'], app.config['PORTAL_CLIENT_SECRET'])
        auth_client.oauth2_start_flow(requested_scopes=requested_scopes,
                                      redirect_uri=app.config["REDIRECT_URI"], refresh_tokens=True)
    except Exception as e:
        flash("Sorry, we've run into an error logging you in.")
        logger.error("Authcallback init: {}".format(repr(e)))
        return redirect(url_for('home'))

    # If there's no "code" query string parameter, we're in this route
    # starting a Globus Auth login flow.
    if 'code' not in request.args:
        try:
            logger.debug("Starting Auth login flow")
            additional_authorize_params = (
                {'signup': 1} if request.args.get('signup') else {})

            auth_uri = auth_client.oauth2_get_authorize_url(
                            additional_params=additional_authorize_params)
            return redirect(auth_uri)
        except Exception as e:
            flash("Sorry, we've run into an error logging you in with Globus Auth.")
            logger.error("Authcallback no code: {}".format(repr(e)))
            return redirect(url_for('home'))
    else:
        try:
            # If we do have a "code" param, we're coming back from Globus Auth
            # and can start the process of exchanging an auth code for a token.
            logger.debug("Returning from Auth, fetching tokens")
            code = request.args.get('code')
            token_response = auth_client.oauth2_exchange_code_for_tokens(code)
            id_token = token_response.decode_id_token(auth_client)
            tokens = token_response.by_resource_server

            session.update(
                tokens=tokens,
                is_authenticated=True,
                name=id_token.get('name', ''),
                email=id_token.get('email', ''),
                institution=id_token.get('institution', ''),
                primary_username=id_token.get('preferred_username'),
                primary_identity=id_token.get('sub'),
            )
        except Exception as e:
            flash("Sorry, we were unable to authenticate you with Globus Auth.")
            logger.error("Authcallback return tokens: {}".format(repr(e)))
            return redirect(url_for('home'))

        logger.debug("Authcallback success")
        return redirect(url_for('home'))
