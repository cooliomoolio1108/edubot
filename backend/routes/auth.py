from flask import Blueprint, redirect, request, url_for, session, render_template, current_app, make_response
from auth.msal_helper import build_msal_app, get_auth_url
from auth.auth_token import create_login_token, create_refresh_token
from auth.auth_check import require_auth, upsert_user_from_payload
import uuid
import os
from dotenv import load_dotenv
from database import user_collection
import time
from utils.validators import fail_response
load_dotenv()

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/login")
def login():
    state = str(uuid.uuid4())
    session['oauth_state'] = state
    return redirect(get_auth_url(state))

@auth_bp.route("/auth/getAuth")
def authorized():
    returned_state = request.args.get("state")
    expected_state = session.pop("oauth_state", None)
    if not returned_state or returned_state != expected_state:
        return fail_response("Invalid State parameter")
    
    result = build_msal_app().acquire_token_by_authorization_code(
        request.args.get("code"),
        scopes=["User.Read"],
        redirect_uri=url_for("auth.authorized", _external=True)
    )
    expires_in = result["expires_in"]
    expires_at = int(time.time()) + expires_in
    claims = result.get("id_token_claims", {})
    email = claims.get("preferred_username", "")
    domain = email.split('@')[-1]

    if domain not in {"ntu.edu.sg", "e.ntu.edu.sg"}:
        return render_template("error.html", message="Access denied: NTU emails only", home_url=current_app.config["FRONTEND_URL"])
    
    user = upsert_user_from_payload(user_collection, claims)

    login_token = create_login_token(user['email'], user['name'], user['oid'], user['role'])
    refresh_token = create_refresh_token(user['oid'])
    resp = make_response(redirect(os.getenv("STREAMLIT_URL")))
    resp.set_cookie(
        "login_token",
        login_token,
        httponly=False,
        secure=False,
        samesite="Lax"
    )
    resp.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=False,
        secure=False,
        samesite="Lax"
    )
    return resp

@auth_bp.route("/auth/refresh")
def refresh():
    return

@auth_bp.route("/auth/logout")
def logout():
    session.clear()
    return redirect("https://login.microsoftonline.com/common/oauth2/v2.0/logout")
