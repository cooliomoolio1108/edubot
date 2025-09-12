import msal
from flask import current_app, url_for
from functools import wraps
from datetime import datetime, timezone

def build_msal_app():
    return msal.ConfidentialClientApplication(
        client_id=current_app.config["CLIENT_ID"],
        client_credential=current_app.config["CLIENT_SECRET"],
        authority=current_app.config["AUTHORITY"]
    )

def get_auth_url(state):
    return build_msal_app().get_authorization_request_url(
        current_app.config["SCOPE"],
        state=state,
        redirect_uri=url_for("auth.authorized", _external=True)
    )

def upsert_user_from_claims(db, claims: dict) -> dict:
    oid   = claims.get("oid")
    email = (claims.get("preferred_username") or claims.get("email") or "").lower()
    name  = claims.get("name") or ""
    tid   = claims.get("tid")
    now   = datetime.now(timezone.utc)

    if not oid:
        raise ValueError("Missing 'oid' in ID token claims")
    if not email:
        raise ValueError("Missing 'email'/'preferred_username' in ID token claims")

    # 1) Try by oid
    u = db.find_one({"oid": oid})
    if u:
        db.update_one(
            {"_id": u["_id"]},
            {"$set": {
                "email": email,
                "name": name,
                "tenant_id": tid,
                "last_login": now,
                "updated_at": now
            }}
        )
        u.update({"email": email, "name": name, "tenant_id": tid, "last_login": now})
        return u

    # 2) Fallback by email (legacy accounts before oid was stored)
    u = db.find_one({"email": email})
    if u:
        # attach oid going forward
        db.update_one(
            {"_id": u["_id"]},
            {"$set": {
                "oid": oid,
                "tenant_id": tid,
                "last_login": now,
                "updated_at": now
            }}
        )
        u.update({"oid": oid, "tenant_id": tid, "last_login": now})
        return u

    # 3) Create new
    doc = {
        "oid": oid,
        "email": email,
        "name": name,
        "tenant_id": tid,
        "role": "student",
        "is_active": True,
        "status": "active",
        "created_at": now,
        "last_login": now
    }
    res = db.insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    return doc
