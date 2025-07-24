from flask import Blueprint, request, jsonify
from models import db, User, Token
from ictu import Ictu
import secrets
from datetime import datetime, timedelta
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').lower()
    password = request.form.get('password')

    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Thiếu thông tin'}), 400

    # Tài khoản ICTU
    if username.startswith("dtc"):
        md5_pass = hashlib.md5(password.encode('utf-8')).hexdigest()
        browser = Ictu()
        res = browser.login(username, md5_pass)

        if res == '':
            user = User.query.filter_by(username=username).first()
            if not user:
                user = User(username=username, password=md5_pass)
                db.session.add(user)
            else:
                user.password = md5_pass
        else:
            return jsonify({'status': 'error', 'message': res}), 401

    else:
        # Tài khoản thường
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({'status': 'error', 'message': 'Tài khoản hoặc mật khẩu không đúng'}), 401

    # Tạo token
    token_str = secrets.token_hex(32)
    token = Token(token=token_str, user=user, expires_at=datetime.now() + timedelta(days=7))
    db.session.add(token)
    db.session.commit()

    return jsonify({'status': 'success', 'token': token_str})
