from flask import Blueprint, redirect, request, url_for, session, render_template, current_app, make_response
from utils.msal_helper import build_msal_app, get_auth_url
from utils.auth_token import create_login_token, create_refresh_token
from utils.auth_check import require_auth, upsert_user_from_payload
import uuid
import os
from dotenv import load_dotenv
from database import user_collection
from utils.validators import fail_response
import jwt

load_dotenv()
def extract_claims(result):
    # 1. If MSAL gave us claims, use them
    claims = result.get("id_token_claims", {})
    if claims and "oid" in claims:
        return claims

    # 2. If raw id_token exists, decode it (works across workers)
    id_token = result.get("id_token")
    if id_token:
        try:
            decoded = jwt.decode(id_token, options={"verify_signature": False})
            return decoded
        except Exception as e:
            print("JWT decode failed:", e)
            return {}

    # 3. If neither exists, return empty
    return {}
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
        render_template(
            "error.html",
            message="Wrong State parameter. Check login status or start a new login",
            home_url=current_app.config["FRONTEND_URL"]
        )
    
    result = build_msal_app().acquire_token_by_authorization_code(
        request.args.get("code"),
        scopes=["User.Read"],
        redirect_uri=url_for("auth.authorized", _external=True)
    )
    claims = extract_claims(result)
    if not claims or "oid" not in claims:
        redirect(os.getenv("STREAMLIT_URL"))
        return fail_response("Authentication failed: no valid claims returned")



    email = claims.get("preferred_username", "")
    domain = email.split('@')[-1]
    domain = domain.strip().lower()
    print("The domain:", domain)

    if not domain.endswith("ntu.edu.sg"):
        return render_template(
            "error.html",
            message="Access denied: NTU emails only",
            home_url=current_app.config["FRONTEND_URL"]
        )

    print("Claims:", claims)
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
