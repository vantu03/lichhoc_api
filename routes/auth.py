from flask import Blueprint, request, jsonify
from models import db, User, Token
from ictu import Ictu
import secrets
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').lower()
    password = request.form.get('password')

    if username and password:
        user = None
        if username.startswith("dtc"):
            browser = Ictu()
            res = browser.login(username, password)
            if res == '':
                user = User.query.filter_by(username=username).first()
                if not user:
                    user = User(username=username, password=password)
                    db.session.add(user)
                else:
                    user.password = password
            else:
                return jsonify({'status': 'error', 'message': res})

        if user:
            token_str = secrets.token_hex(32)
            token = Token(token=token_str, user=user, expires_at=datetime.now() + timedelta(days=7))
            db.session.add(token)
            db.session.commit()

            return jsonify({'status': 'success', 'token': token_str})
        else:
            return jsonify({'status': 'error', 'message': 'Tài khoản hoặc mật khẩu không đúng'})

    return jsonify({'status': 'error', 'message': 'Thiếu thông tin'})
