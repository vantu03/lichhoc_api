from flask import Blueprint, request, jsonify, abort
from models import db, FcmToken, FirebaseCredential
import firebase_admin
from firebase_admin import credentials, messaging
import json

notify_bp = Blueprint('notify', __name__, url_prefix='/notify')

firebase_apps = {}

def init_firebase_if_needed(server_name):
    if server_name in firebase_apps:
        return firebase_apps[server_name]

    cred_obj = FirebaseCredential.query.filter_by(server_name=server_name).first()
    if not cred_obj:
        raise Exception(f"Không tìm thấy cấu hình Firebase cho server '{server_name}'")

    try:
        cred_dict = json.loads(cred_obj.json_data)
        app_instance = firebase_admin.initialize_app(
            credentials.Certificate(cred_dict),
            name=server_name
        )
        firebase_apps[server_name] = app_instance
        return app_instance
    except Exception as e:
        raise Exception(f"Lỗi khi khởi tạo Firebase cho server '{server_name}': {e}")


@notify_bp.route('/send', methods=['POST'])
def send_notification():
    server_name = request.form.get('server', '').strip()
    title = request.form.get('title', '').strip()
    body = request.form.get('body', '').strip()

    if not server_name or not title or not body:
        abort(400, 'Thiếu thông tin server/title/body')

    try:
        app_instance = init_firebase_if_needed(server_name)
    except Exception as e:
        return str(e), 500

    tokens = FcmToken.query.all()
    if not tokens:
        return 'No tokens found!', 404

    success_count = 0
    error_count = 0
    invalid_tokens = []

    for t in tokens:
        fcm_token = t.token
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=fcm_token,
        )
        try:
            response = messaging.send(message, app=app_instance)
            print("✅ Sent to:", fcm_token, "|", response)
            success_count += 1
        except Exception as e:
            print("❌ Unknown error to:", fcm_token, "|", e)
            invalid_tokens.append(t)
            error_count += 1

    if invalid_tokens:
        for bad in invalid_tokens:
            db.session.delete(bad)
        db.session.commit()

    return jsonify({
        'success': True,
        'sent': success_count,
        'failed': error_count,
        'total': len(tokens)
    })


@notify_bp.route('/upload_firebase', methods=['POST'])
def upload_firebase_config():
    file = request.files.get('json_file')
    server_name = request.form.get('server_name', '').strip()

    if not file or not server_name:
        return jsonify({'success': False, 'message': 'Thiếu file hoặc tên server'}), 400

    content = file.read().decode('utf-8')

    existing = FirebaseCredential.query.filter_by(server_name=server_name).first()
    if existing:
        existing.json_data = content
    else:
        db.session.add(FirebaseCredential(server_name=server_name, json_data=content))

    db.session.commit()
    return jsonify({'success': True})


@notify_bp.route('/token', methods=['POST'])
def save_device_token():
    token = request.json.get('token', '').strip()
    if not token:
        return jsonify({'success': False, 'message': 'Thiếu token'}), 400

    if not FcmToken.query.filter_by(token=token).first():
        db.session.add(FcmToken(token=token))
        db.session.commit()

    return jsonify({'success': True})
