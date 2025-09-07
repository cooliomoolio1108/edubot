from flask import Blueprint, session, render_template

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html", user=session.get("user"))

@main_bp.route("/dashboard")
def dashboard():
    if not session.get("user"):
        return "Not logged in", 401
    return f"Welcome {session['user']['name']}"
