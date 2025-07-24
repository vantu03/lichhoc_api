import pandas as pd, re
from functools import wraps
from flask import request, jsonify, g
from models import Token
from datetime import datetime

def extract_form_fields(form):
    form_data = {}
    for input_tag in form.find_all('input'):
        name = input_tag.get('name')
        if not name: continue
        input_type = input_tag.get('type', 'text')
        value = input_tag.get('value', '')
        if input_type in ['checkbox', 'radio']:
            if input_tag.has_attr('checked'):
                form_data[name] = value
        else:
            form_data[name] = value
    for select in form.find_all('select'):
        name = select.get('name')
        if not name: continue
        selected_option = select.find('option', selected=True)
        form_data[name] = selected_option.get('value', '') if selected_option else \
            (select.find('option').get('value', '') if select.find('option') else '')
    for textarea in form.find_all('textarea'):
        name = textarea.get('name')
        if name:
            form_data[name] = textarea.text or ''
    return form_data

def find_text_positions(df: pd.DataFrame, search_text: str, case_sensitive=False):
    matches = []
    for row_idx, row in df.iterrows():
        for col_idx, cell in enumerate(row):
            if pd.notna(cell):
                cell_str = str(cell)
                if (search_text in cell_str) if case_sensitive else (search_text.lower() in cell_str.lower()):
                    matches.append({"row": row_idx, "col": col_idx, "value": cell})
    return matches

def get_study_time(tiet_start, tiet_end):
    tiet_map = {
        1: ("6:45", "7:35"), 2: ("7:40", "8:30"), 3: ("8:40", "9:30"),
        4: ("9:40", "10:30"), 5: ("10:35", "11:25"), 6: ("13:00", "13:50"),
        7: ("13:55", "14:45"), 8: ("14:55", "15:45"), 9: ("15:55", "16:45"),
        10: ("16:50", "17:40"), 11: ("18:15", "19:05"), 12: ("19:10", "20:00"),
        13: ("20:10", "21:00"), 14: ("21:10", "22:00"), 15: ("20:30", "21:30")
    }
    start = tiet_map.get(tiet_start, ("", ""))[0]
    end = tiet_map.get(tiet_end, ("", ""))[1]
    return f"{start} - {end}"

def convert_time_to_minutes(time_range):
    if not time_range or not isinstance(time_range, str): return -1
    match = re.match(r'(\d{2}):(\d{2})', time_range)
    return int(match.group(1)) * 60 + int(match.group(2)) if match else -1


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or not auth.startswith("Bearer "):
            return jsonify({'status': 'error', 'message': 'Token không hợp lệ'}), 401

        token_str = auth.split(" ")[1]
        token = Token.query.filter_by(token=token_str).first()

        if not token:
            return jsonify({'status': 'error', 'message': 'Token không tồn tại hoặc đã hết hạn'}), 401
        if token.expires_at and token.expires_at < datetime.now():
            return jsonify({'status': 'error', 'message': 'Token đã hết hạn'}), 401

        g.current_user = token.user
        return f(*args, **kwargs)
    return decorated