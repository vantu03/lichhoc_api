from flask import Blueprint, request, jsonify
from models import db, Token, FirebaseCredential
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
    server_name = request.form.get('server')
    title = request.form.get('title')
    body = request.form.get('body')

    try:
        app_instance = init_firebase_if_needed(server_name)
    except Exception as e:
        return str(e), 500

    tokens = Token.query.all()
    if not tokens:
        return 'No tokens found!', 404

    success_count = 0
    error_count = 0
    for t in tokens:
        token = t.token
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=token,
        )
        try:
            response = messaging.send(message, app=app_instance)
            print("✅ Sent to:", token, "|", response)
            success_count += 1
        except firebase_admin.exceptions.FirebaseError as e:
            print("❌ Firebase error to:", token, "|", e)
            if isinstance(e, messaging.UnregisteredError) or \
               isinstance(e, messaging.InvalidArgumentError):
                print("⚠️ Token invalid. Deleting:", token)
                db.session.delete(t)
                db.session.commit()
            error_count += 1
        except Exception as e:
            print("❌ Unknown error to:", token, "|", e)
            error_count += 1

    return jsonify({
        'success': True,
        'sent': success_count,
        'failed': error_count,
        'total': len(tokens)
    })


@notify_bp.route('/upload_firebase', methods=['POST'])
def upload_firebase_config():
    file = request.files.get('json_file')
    server_name = request.form.get('server_name')

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


@notify_bp.route('/save_token', methods=['POST'])
def save_device_token():
    token = request.json.get('token')
    if not token:
        return jsonify({'success': False, 'message': 'Missing token'}), 400

    if not Token.query.filter_by(token=token).first():
        db.session.add(Token(token=token))
        db.session.commit()
    return jsonify({'success': True})
