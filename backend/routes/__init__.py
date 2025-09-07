from .auth import auth_bp
from .main import main_bp
from .user_routes import user_routes
from .feedback_routes import feedback_routes
from .conversation import conversation_routes
from .message import message_routes
from .chat import chat_routes
from .course import course_routes
from .file import file_routes

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(user_routes)
    app.register_blueprint(feedback_routes)
    app.register_blueprint(conversation_routes)
    app.register_blueprint(message_routes)
    app.register_blueprint(chat_routes)
    app.register_blueprint(course_routes)
    app.register_blueprint(file_routes)