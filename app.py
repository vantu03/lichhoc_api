from flask import Flask
from flask_cors import CORS
from config import Config
from models import db

# Import các blueprint
from routes.auth import auth_bp
from routes.schedule import schedule_bp
from routes.notify import notify_bp
from routes.home import home_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Khởi tạo CORS
    CORS(app)

    # Khởi tạo database
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Đăng ký blueprint
    app.register_blueprint(auth_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(notify_bp)
    app.register_blueprint(home_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
