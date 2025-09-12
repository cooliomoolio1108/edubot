import time, jwt
from flask import current_app
from services.user_services import get_user_by_oid
from datetime import datetime, timedelta

def create_login_token(user_email, name, oid, role):
    user = get_user_by_oid(oid)
    payload = {
        "sub": user.get("_id", ""),
        "oid": oid,
        "email": user_email,
        "name": name,
        "iat": int(time.time()),
        #"exp": datetime.utcnow() + timedelta(seconds=5),
        "exp": int(time.time()) + 3600,
        "role": user.get("role", "")
    }
    token = jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")
    return token

def create_refresh_token(oid):
    user = get_user_by_oid(oid)
    payload = {
        "sub": user.get("_id", ""),
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    token = jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")
    return token