from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
import subprocess, os

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


    # ✅ Route webhook GITHUB
    @app.route('/git-webhook', methods=['POST'])
    def git_webhook():
        try:
            # Lấy đường dẫn thư mục hiện tại của app.py
            project_dir = os.path.dirname(os.path.abspath(__file__))

            subprocess.run(['git', '-C', project_dir, 'pull'], check=True)
            subprocess.run(['systemctl', 'restart', 'svpro'], check=True)
            return 'Updated and restarted.', 200
        except subprocess.CalledProcessError as e:
            return f'Error: {e}', 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
