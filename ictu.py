import requests, pandas as pd, re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from io import BytesIO
from utils import convert_time_to_minutes, find_text_positions, extract_form_fields, get_study_time
from browser import Browser

class Ictu(Browser):
    def __init__(self):
        super().__init__()
        self.today = datetime.today()
        self.result = {
            'status': 'success',
            'message': {
                'startDate': self.today.strftime("%d/%m/%Y"),
                'endDate': (self.today + timedelta(days=7)).strftime("%d/%m/%Y"),
                'schedule': []
            }
        }

    def login(self, tk, mk):
        response = self.session.get('https://dangkytinchi.ictu.edu.vn/kcntt/login.aspx')
        soup = BeautifulSoup(response.text, 'html.parser')
        form_data = extract_form_fields(soup.find('form'))
        form_data['txtUserName'] = tk
        form_data['txtPassword'] = mk
        response = self.session.post(url=response.url, data=form_data)

        soup = BeautifulSoup(response.text, 'html.parser')
        lbl_error = soup.find(id="lblErrorInfo")
        if lbl_error and lbl_error.text.strip():
            return lbl_error.text.strip()
        return ''

    def get_schedule(self):
        try:
            self.get_lich_hoc()
            self.get_lich_thi()

            self.result['message']['schedule'].sort(key=lambda x: (
                datetime.strptime(x['date'], '%d/%m/%Y') if x['date'] else datetime.max,
                convert_time_to_minutes(x.get('timeRange', ''))
            ))

            # Cập nhật startDate và endDate theo lịch thực tế
            dates = [x['date'] for x in self.result['message']['schedule'] if x.get('date')]
            if dates:
                self.result['message']['startDate'] = dates[0]
                self.result['message']['endDate'] = dates[-1]

        except requests.RequestException as e:
            self.result['status'] = 'error'
            self.result['message'] = f'Lỗi: {e}'
        return self.result

    def get_lich_hoc(self):
        response = self.session.get('https://dangkytinchi.ictu.edu.vn/kcntt/Reports/Form/StudentTimeTable.aspx')
        soup = BeautifulSoup(response.text, 'html.parser')
        form_data = extract_form_fields(soup.find('form'))
        # Lấy ngày hiện tại trừ đi 4 năm
        tu_ngay = datetime.today() - timedelta(days=365 * 1)
        form_data['txtTuNgay'] = tu_ngay.strftime('%d/%m/%Y')
        response = self.session.post(url=response.url, data=form_data)

        if not response.headers['Content-Type'].startswith('application/vnd.ms-excel') :
            return

        df = pd.read_excel(BytesIO(response.content), engine='xlrd')
        class_pos = find_text_positions(df, 'Lớp học phần')
        col_class = class_pos[0]['col']
        row_start = class_pos[0]['row'] + 1
        current_week_start = None
        session_counter = {}

        col_teacher = find_text_positions(df, 'Giảng viên/ link meet')[0]['col']
        col_day = find_text_positions(df, 'Thứ')[0]['col']
        col_period = find_text_positions(df, 'Tiết học')[0]['col']
        col_room = find_text_positions(df, 'Địa điểm')[0]['col']

        for i in range(row_start, len(df)):
            cell = df.iloc[i, col_class]

            if isinstance(cell, str) and cell.startswith("Tuần"):
                match = re.search(r"\((\d{2}/\d{2}/\d{4}) đến (\d{2}/\d{2}/\d{4})\)", cell)
                if match:
                    current_week_start = datetime.strptime(match.group(1), "%d/%m/%Y")
            elif pd.notna(cell) and current_week_start:
                try:
                    weekday = int(str(df.iloc[i, col_day]).strip())
                    date = current_week_start + timedelta(days=weekday - 2)
                except:
                    date = None

                session_counter.setdefault(cell, 0)
                session_counter[cell] += 1

                lichhoc = {
                    'date': date.strftime("%d/%m/%Y") if date else None,
                    'dayOfWeek': weekday,
                    'className': cell,
                    'scheduleType': 'Lịch học',
                    'timeRange': '00:00',
                    'detail': {
                        'Tiết': [],
                        'Địa điểm': str(df.iloc[i, col_room]).strip(),
                        'Buổi': session_counter[cell],
                    },
                    'hidden': {
                        'Giảng viên': str(df.iloc[i, col_teacher]).strip(),
                    },
                }

                self.result['message']['schedule'].append(lichhoc)

                period_raw = str(df.iloc[i, col_period]).strip()
                try:
                    parts = [int(p.strip()) for p in period_raw.split('-->')]
                    if len(parts) == 2:
                        tiet_start, tiet_end = parts
                        lichhoc['detail']['Tiết'] = list(range(tiet_start, tiet_end + 1))
                        lichhoc['timeRange'] = get_study_time(tiet_start, tiet_end)
                    elif len(parts) == 1:
                        tiet_start = tiet_end = parts[0]
                        lichhoc['detail']['Tiết'] = [tiet_start]
                        lichhoc['timeRange'] = get_study_time(tiet_start, tiet_end)
                except:
                    pass

    def get_lich_thi(self):
        response = self.session.get('https://dangkytinchi.ictu.edu.vn/kcntt/StudentViewExamList.aspx')
        soup = BeautifulSoup(response.text, 'html.parser')
        form_data = extract_form_fields(soup.find('form'))
        # Lấy ngày hiện tại trừ đi 4 năm
        tu_ngay = datetime.today() - timedelta(days=365 * 1)
        form_data['txtTuNgay'] = tu_ngay.strftime('%d/%m/%Y')
        response = self.session.post(url=response.url, data=form_data)

        if not response.headers['Content-Type'].startswith('application/vnd.ms-excel'):
            return

        df = pd.read_excel(BytesIO(response.content), engine='xlrd')
        class_pos = find_text_positions(df, 'Tên học phần')
        col_class = class_pos[0]['col']
        row_start = class_pos[0]['row'] + 1

        col_tc = find_text_positions(df, 'TC')[0]['col']
        col_day = find_text_positions(df, 'Ngày thi')[0]['col']
        col_period = find_text_positions(df, 'Thời gian thi')[0]['col']
        col_form = find_text_positions(df, 'Hình thức thi')[0]['col']
        col_sbd = find_text_positions(df, 'SBD')[0]['col']
        col_room = find_text_positions(df, 'Phòng thi')[0]['col']

        for i in range(row_start, len(df)):
            class_name = str(df.iloc[i, col_class]).strip()
            if not class_name or class_name.lower().startswith("nan"):
                continue

            try:
                date_obj = datetime.strptime(str(df.iloc[i, col_day]).strip(), "%d/%m/%Y")
                date = date_obj.strftime("%d/%m/%Y")
                day_of_week = date_obj.weekday() + 1
            except:
                date = None
                day_of_week = None

            time_range_match = re.search(r'(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})', str(df.iloc[i, col_period]))
            time_range = f"{time_range_match.group(1)} - {time_range_match.group(2)}" if time_range_match else ""

            self.result['message']['schedule'].append({
                'date': date,
                'dayOfWeek': day_of_week,
                'className': class_name,
                'scheduleType': 'Lịch thi',
                'timeRange': time_range,
                'detail': {
                    'Ca thi': str(df.iloc[i, col_period]).strip(),
                    'Địa điểm': str(df.iloc[i, col_room]).strip()
                },
                'hidden': {
                    'Hình thức': str(df.iloc[i, col_form]).strip(),
                    'Số báo danh': str(df.iloc[i, col_sbd]).strip(),
                    'Số tín chỉ': str(df.iloc[i, col_tc]).strip()
                }
            })
