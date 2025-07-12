from flask import Flask, request, jsonify
from lichICTU import LichSinhVienICTU
from flask_cors import CORS

app = Flask(__name__)

VAPID_PUBLIC_KEY = "BGv5IqaSOkLg3Iu5zc4mMmJEsDaIqAactL646vsmAHz1bA44WOvweQe4ZLz2RsPyqwOzlaZf4EMVuzha6rezzZ4"
VAPID_PRIVATE_KEY = "ADK-gJnekc4f12jr8uRR7HuLIfzF7hTTJxt4mZYp5sY"
VAPID_CLAIMS = {"sub": "mailto:you@example.com"}

subs_file = "subscriptions.json"

CORS(app, origins=[
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "https://sv.pro.vn"
])

subs_file = "subscriptions.json"

def load_subs():
    if os.path.exists(subs_file):
        with open(subs_file, "r") as f:
            return json.load(f)
    return []

def save_sub(sub):
    subs = load_subs()
    subs.append(sub)
    with open(subs_file, "w") as f:
        json.dump(subs, f)

@app.route("/")
def index():
    return render_template("index.html", vapid_public_key=VAPID_PUBLIC_KEY)

@app.route("/subscribe", methods=["POST"])
def subscribe():
    sub = request.get_json()
    save_sub(sub)
    return jsonify({"status": "subscribed"})

@app.route("/send", methods=["POST"])
def send():
    payload = json.dumps({
        "title": "Thông báo từ Flask!",
        "body": "Xin chào từ server Python Flask!"
    })
    errors = []
    for sub in load_subs():
        try:
            webpush(
                subscription_info=sub,
                data=payload,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims=VAPID_CLAIMS
            )
        except WebPushException as e:
            errors.append(str(e))
    return jsonify({"status": "done", "errors": errors})

@app.route('/api/', methods=['GET'])
def lichhoc_api():
    tk = request.args.get('username')
    mk = request.args.get('password')

    if not tk or not mk:
        return jsonify({'status': 'error', 'message': 'Thiếu tài khoản hoặc mật khẩu'}), 400

    lich = LichSinhVienICTU(tk, mk)
    data = lich.get_schedule()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
