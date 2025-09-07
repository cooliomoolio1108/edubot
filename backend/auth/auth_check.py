from flask import current_app, url_for, request, g
from functools import wraps
import jwt, time
from database.user_crud import get_user
from datetime import datetime, timezone
from utils.validators import success_response, fail_response, error_response

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return fail_response("Missing Authorization Token", code=401)
        try:
            payload = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
            user = get_user(payload.get("sub"))
            if not user:
                return fail_response("User not Found", 404)
            g.current_user = {
                "_id": user.get("_id", ""),
                "email": user.get("email", ""),
                "role": user.get("role", ""),
                "oid": user.get("oid", "")
            }
        except jwt.ExpiredSignatureError:
            return fail_response("Token expired.", 401)
        except Exception as e:
            return error_response(e)
        return f(*args, **kwargs)
    return decorated

def upsert_user_from_payload(db, payload: dict) -> dict:
    oid   = payload.get("oid")
    email = (payload.get("preferred_username") or payload.get("email") or "").lower()
    name  = payload.get("name") or ""
    tid   = payload.get("tid")
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
                "last_login": now,
                "updated_at": now
            }}
        )
        return u

    # 2) Fallback by email (legacy accounts before oid was stored)
    u = db.find_one({"email": email})
    if u:
        # attach oid going forward
        db.update_one(
            {"_id": u["_id"]},
            {"$set": {
                "last_login": now,
                "updated_at": now
            }}
        )
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

