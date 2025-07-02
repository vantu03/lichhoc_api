from django.http import JsonResponse
from .lichICTU import LichSinhVienICTU

def home(request):
    pass

def lichhoc_api(request):
    tk = request.GET.get('username')
    mk = request.GET.get('password')

    if not tk or not mk:
        return JsonResponse({'status': 'error', 'message': 'Thiếu tài khoản hoặc mật khẩu'}, status=400)

    lich = LichSinhVienICTU(tk, mk)
    data = lich.get_schedule()
    return JsonResponse(data, json_dumps_params={'ensure_ascii': False}, safe=False)
