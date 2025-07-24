from flask import Blueprint, jsonify, g
from ictu import Ictu
from utils import token_required

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

@schedule_bp.route('/', methods=['POST'])
@token_required
def get_schedule():

    user = g.current_user

    if user.username.startswith('dtc'):
        browser = Ictu()
        res = browser.login(user.username, user.password)

        if res != '':
            return jsonify({'status': 'error', 'message': res})

        result = browser.get_schedule()
        return jsonify(result)

    else:

        return jsonify({'status': 'error', 'message': 'Không có lịch'})