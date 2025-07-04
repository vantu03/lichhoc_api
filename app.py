from flask import Flask, request, jsonify
from lichICTU import LichSinhVienICTU
from flask_cors import CORS

app = Flask(__name__)

CORS(app, origins=[
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "https://sv.pro.vn"
])

@app.route('/')
def home():
    return jsonify({'message': 'Chào bạn đến với API lấy lịch học ICTU'})

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
