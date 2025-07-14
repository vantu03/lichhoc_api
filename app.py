from flask import Flask, request, jsonify
from flask_cors import CORS
from lichICTU import LichSinhVienICTU

app = Flask(__name__)

CORS(app)

@app.route('/')
def home():
    return 'Flask API Lịch học ICTU hoạt động!'

@app.route('/lichhoc/', methods=['GET'])
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
