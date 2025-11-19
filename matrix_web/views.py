from django.http.response import HttpResponseServerError, JsonResponse
from rest_framework.views import APIView, Response
from .models import Matrix as Mat, MonitorLayout, Profile, MatrixSetting, License
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .serializers import MatrixSettingSerializer, MatrixSerializer, ProfileSerializer
import socket, time, csv
from utils.views import license_auth
from collections import Counter
import binascii

delay_time = 0.5

@login_required(login_url='login_auth')
def home(req):
    """
    Home 페이지 (레이아웃 정보 포함)
    """
    permission = req.user.userpermission.permission

    # 학생 사용자일 경우 해당 Group만 사용하게끔 분리
    if permission > 2:
        matrix = Mat.objects.filter(is_main=False).filter(main_connect=(permission-2))
        context = {'matrix': matrix, 'permission': permission}
        return render(req, 'group_homepage.html', context)
    else:
        matrix = Mat.objects.filter(is_main=False).order_by("main_connect")
        main = Mat.objects.filter(is_main=True)
        profile = Profile.objects.all().order_by('order', 'id')
        connect = ['입력01', '입력02', '입력03', '입력04']

        for i in range(min(len(matrix), len(connect))):
            matrix[i].count = i+1
            connect[i] = matrix[i].name

        # 사용자의 레이아웃 설정 가져오기
        user_layouts = {}
        for m in main:
            layouts = MonitorLayout.objects.filter(
                user=req.user,
                matrix=m
            ).order_by('display_order')

            if layouts.exists():
                user_layouts[m.id] = [
                    {
                        'position': layout.monitor_position,
                        'row': layout.row_position,
                        'col': layout.col_position,
                        'display_order': layout.display_order,
                        'is_visible': layout.is_visible
                    }
                    for layout in layouts
                ]

        context = {
            'matrix': matrix,
            'profile': profile,
            'main': main,
            'connect_list': connect,
            'permission': permission,
            'user_layouts': user_layouts
        }
        return render(req, 'home.html', context)


def slicer_command_handle(input):
    command = ''
    if type(input) is str:
        input = int(input)
    if input == 0:
        command = '55 AA 04 0B 00 0F EE'
    elif input == 1:
        command = '55 AA 04 0B 11 0F EE'
    return bytes.fromhex(command)

def kvm_command_handle(input):
    """
        kvm command 변환
    """
    command = ''

    if type(input) is str:
        input = int(input)

    if input==1:
        command = '55 AA 04 09 00 0D EE'
    elif input==2:
        command = '55 AA 04 09 01 0E EE'
    elif input==3:
        command = '55 AA 04 09 02 0F EE'
    elif input==4:
        command = '55 AA 04 09 03 10 EE'
    elif input==5:
        command = '55 AA 04 09 04 11 EE'
    elif input==6:
        command = '55 AA 04 09 05 12 EE'
    elif input==7:
        command = '55 AA 04 09 06 13 EE'
    elif input==8:
        command = '55 AA 04 09 07 14 EE'
    elif input==9:
        command = '55 AA 04 09 08 15 EE'
    elif input==10:
        command = '55 AA 04 09 09 16 EE'
    elif input==11:
        command = '55 AA 04 09 0A 17 EE'
    elif input==12:
        command = '55 AA 04 09 0B 18 EE'
    elif input==13:
        command = '55 AA 04 09 0C 19 EE'
    elif input==14:
        command = '55 AA 04 09 0D 1A EE'
    elif input==15:
        command = '55 AA 04 09 0E 1B EE'
    elif input==16:
        command = '55 AA 04 09 0F 1C EE'
    elif input==17:
        command = '55 AA 04 09 11 1D EE'
    elif input==18:
        command = '55 AA 04 09 12 1E EE'
    elif input==19:
        command = '55 AA 04 09 13 1F EE'
    elif input==20:
        command = '55 AA 04 09 14 20 EE'
    elif input==21:
        command = '55 AA 04 09 15 21 EE'
    elif input==22:
        command = '55 AA 04 09 16 22 EE'
    elif input==23:
        command = '55 AA 04 09 17 23 EE'
    elif input==24:
        command = '55 AA 04 09 18 24 EE'
    elif input==25:
        command = '55 AA 04 09 19 25 EE'
    elif input==26:
        command = '55 AA 04 09 1A 26 EE'
    elif input==27:
        command = '55 AA 04 09 1B 27 EE'
    elif input==28:
        command = '55 AA 04 09 1C 28 EE'
    elif input==29:
        command = '55 AA 04 09 1D 29 EE'
    elif input==30:
        command = '55 AA 04 09 1E 2A EE'
    elif input==31:
        command = '55 AA 04 09 1F 2B EE'
    elif input==32:
        command = '55 AA 04 09 20 29 EE'
    return bytes.fromhex(command)

def matrix_command_handle(input, target):
    """
        matrix command 변환
    """
    command = ''

    input = int(input)
    target = int(target)
    if input==1:
        if target == 1:
            command = '55 AA 05 08 00 00 0D EE'
        elif target == 2:
            command = '55 AA 05 08 00 10 1D EE'
        elif target == 3:
            command = '55 AA 05 08 00 20 2D EE'
        elif target == 4:
            command = '55 AA 05 08 00 30 3D EE'
        elif target == 5:
            command = '55 AA 05 08 00 40 4D EE'
        elif target == 6:
            command = '55 AA 05 08 00 50 5D EE'
        elif target == 7:
            command = '55 AA 05 08 00 60 6D EE'
        elif target == 8:
            command = '55 AA 05 08 00 70 7D EE'
        elif target == 9:
            command = '55 AA 05 08 00 80 8D EE'
        elif target == 10:
            command = '55 AA 05 08 00 90 9D EE'
        elif target == 11:
            command = '55 AA 05 08 00 A0 AD EE'
        elif target == 12:
            command = '55 AA 05 08 00 B0 BD EE'
        elif target == 13:
            command = '55 AA 05 08 00 C0 CD EE'
        elif target == 14:
            command = '55 AA 05 08 00 D0 DD EE'
        elif target == 15:
            command = '55 AA 05 08 00 E0 ED EE'
        elif target == 16:
            command = '55 AA 05 08 00 F0 FD EE'
    if input==2:
        if target == 1:
            command = '55 AA 05 08 00 01 0E EE'
        elif target == 2:
            command = '55 AA 05 08 00 11 1E EE'
        elif target == 3:
            command = '55 AA 05 08 00 21 2E EE'
        elif target == 4:
            command = '55 AA 05 08 00 31 3E EE'
        elif target == 5:
            command = '55 AA 05 08 00 41 4E EE'
        elif target == 6:
            command = '55 AA 05 08 00 51 5E EE'
        elif target == 7:
            command = '55 AA 05 08 00 61 6E EE'
        elif target == 8:
            command = '55 AA 05 08 00 71 7E EE'
        elif target == 9:
            command = '55 AA 05 08 00 81 8E EE'
        elif target == 10:
            command = '55 AA 05 08 00 91 9E EE'
        elif target == 11:
            command = '55 AA 05 08 00 A1 AE EE'
        elif target == 12:
            command = '55 AA 05 08 00 B1 BE EE'
        elif target == 13:
            command = '55 AA 05 08 00 C1 CE EE'
        elif target == 14:
            command = '55 AA 05 08 00 D1 DE EE'
        elif target == 15:
            command = '55 AA 05 08 00 E1 EE EE'
        elif target == 16:
            command = '55 AA 05 08 00 F1 FE EE'
    if input==3:
        if target == 1:
            command = '55 AA 05 08 00 02 0F EE'
        elif target == 2:
            command = '55 AA 05 08 00 12 1F EE'
        elif target == 3:
            command = '55 AA 05 08 00 22 2F EE'
        elif target == 4:
            command = '55 AA 05 08 00 32 3F EE'
        elif target == 5:
            command = '55 AA 05 08 00 42 4F EE'
        elif target == 6:
            command = '55 AA 05 08 00 52 5F EE'
        elif target == 7:
            command = '55 AA 05 08 00 62 6F EE'
        elif target == 8:
            command = '55 AA 05 08 00 72 7F EE'
        elif target == 9:
            command = '55 AA 05 08 00 82 8F EE'
        elif target == 10:
            command = '55 AA 05 08 00 92 9F EE'
        elif target == 11:
            command = '55 AA 05 08 00 A2 AF EE'
        elif target == 12:
            command = '55 AA 05 08 00 B2 BF EE'
        elif target == 13:
            command = '55 AA 05 08 00 C2 CF EE'
        elif target == 14:
            command = '55 AA 05 08 00 D2 DF EE'
        elif target == 15:
            command = '55 AA 05 08 00 E2 EF EE'
        elif target == 16:
            command = '55 AA 05 08 00 F2 FF EE'
    if input==4:
        if target == 1:
            command = '55 AA 05 08 00 03 10 EE'
        elif target == 2:
            command = '55 AA 05 08 00 13 20 EE'
        elif target == 3:
            command = '55 AA 05 08 00 23 30 EE'
        elif target == 4:
            command = '55 AA 05 08 00 33 40 EE'
        elif target == 5:
            command = '55 AA 05 08 00 43 50 EE'
        elif target == 6:
            command = '55 AA 05 08 00 53 60 EE'
        elif target == 7:
            command = '55 AA 05 08 00 63 70 EE'
        elif target == 8:
            command = '55 AA 05 08 00 73 80 EE'
        elif target == 9:
            command = '55 AA 05 08 00 83 90 EE'
        elif target == 10:
            command = '55 AA 05 08 00 93 A0 EE'
        elif target == 11:
            command = '55 AA 05 08 00 A3 B0 EE'
        elif target == 12:
            command = '55 AA 05 08 00 B3 C0 EE'
        elif target == 13:
            command = '55 AA 05 08 00 C3 D0 EE'
        elif target == 14:
            command = '55 AA 05 08 00 D3 E0 EE'
        elif target == 15:
            command = '55 AA 05 08 00 E3 F0 EE'
        elif target == 16:
            command = '55 AA 05 08 00 F3 00 EE'
    if input==5:
        if target == 1:
            command = '55 AA 05 08 00 04 11 EE'
        elif target == 2:
            command = '55 AA 05 08 00 14 21 EE'
        elif target == 3:
            command = '55 AA 05 08 00 24 31 EE'
        elif target == 4:
            command = '55 AA 05 08 00 34 41 EE'
        elif target == 5:
            command = '55 AA 05 08 00 44 51 EE'
        elif target == 6:
            command = '55 AA 05 08 00 54 61 EE'
        elif target == 7:
            command = '55 AA 05 08 00 64 71 EE'
        elif target == 8:
            command = '55 AA 05 08 00 74 81 EE'
        elif target == 9:
            command = '55 AA 05 08 00 84 91 EE'
        elif target == 10:
            command = '55 AA 05 08 00 94 A1 EE'
        elif target == 11:
            command = '55 AA 05 08 00 A4 B1 EE'
        elif target == 12:
            command = '55 AA 05 08 00 B4 C1 EE'
        elif target == 13:
            command = '55 AA 05 08 00 C4 D1 EE'
        elif target == 14:
            command = '55 AA 05 08 00 D4 E1 EE'
        elif target == 15:
            command = '55 AA 05 08 00 E4 F1 EE'
        elif target == 16:
            command = '55 AA 05 08 00 F4 01 EE'
    if input==6:
        if target == 1:
            command = '55 AA 05 08 00 05 12 EE'
        elif target == 2:
            command = '55 AA 05 08 00 15 22 EE'
        elif target == 3:
            command = '55 AA 05 08 00 25 32 EE'
        elif target == 4:
            command = '55 AA 05 08 00 35 42 EE'
        elif target == 5:
            command = '55 AA 05 08 00 45 52 EE'
        elif target == 6:
            command = '55 AA 05 08 00 55 62 EE'
        elif target == 7:
            command = '55 AA 05 08 00 65 72 EE'
        elif target == 8:
            command = '55 AA 05 08 00 75 82 EE'
        elif target == 9:
            command = '55 AA 05 08 00 85 92 EE'
        elif target == 10:
            command = '55 AA 05 08 00 95 A2 EE'
        elif target == 11:
            command = '55 AA 05 08 00 A5 B2 EE'
        elif target == 12:
            command = '55 AA 05 08 00 B5 C2 EE'
        elif target == 13:
            command = '55 AA 05 08 00 C5 D2 EE'
        elif target == 14:
            command = '55 AA 05 08 00 D5 E2 EE'
        elif target == 15:
            command = '55 AA 05 08 00 E5 F2 EE'
        elif target == 16:
            command = '55 AA 05 08 00 F5 02 EE'
    if input==7:
        if target == 1:
            command = '55 AA 05 08 00 06 13 EE'
        elif target == 2:
            command = '55 AA 05 08 00 16 23 EE'
        elif target == 3:
            command = '55 AA 05 08 00 26 33 EE'
        elif target == 4:
            command = '55 AA 05 08 00 36 43 EE'
        elif target == 5:
            command = '55 AA 05 08 00 46 53 EE'
        elif target == 6:
            command = '55 AA 05 08 00 56 63 EE'
        elif target == 7:
            command = '55 AA 05 08 00 66 73 EE'
        elif target == 8:
            command = '55 AA 05 08 00 76 83 EE'
        elif target == 9:
            command = '55 AA 05 08 00 86 93 EE'
        elif target == 10:
            command = '55 AA 05 08 00 96 A3 EE'
        elif target == 11:
            command = '55 AA 05 08 00 A6 B3 EE'
        elif target == 12:
            command = '55 AA 05 08 00 B6 C3 EE'
        elif target == 13:
            command = '55 AA 05 08 00 C6 D3 EE'
        elif target == 14:
            command = '55 AA 05 08 00 D6 E3 EE'
        elif target == 15:
            command = '55 AA 05 08 00 E6 F3 EE'
        elif target == 16:
            command = '55 AA 05 08 00 F6 03 EE'
    if input==8:
        if target == 1:
            command = '55 AA 05 08 00 07 14 EE'
        elif target == 2:
            command = '55 AA 05 08 00 17 24 EE'
        elif target == 3:
            command = '55 AA 05 08 00 27 34 EE'
        elif target == 4:
            command = '55 AA 05 08 00 37 44 EE'
        elif target == 5:
            command = '55 AA 05 08 00 47 54 EE'
        elif target == 6:
            command = '55 AA 05 08 00 57 64 EE'
        elif target == 7:
            command = '55 AA 05 08 00 67 74 EE'
        elif target == 8:
            command = '55 AA 05 08 00 77 84 EE'
        elif target == 9:
            command = '55 AA 05 08 00 87 94 EE'
        elif target == 10:
            command = '55 AA 05 08 00 97 A4 EE'
        elif target == 11:
            command = '55 AA 05 08 00 A7 B4 EE'
        elif target == 12:
            command = '55 AA 05 08 00 B7 C4 EE'
        elif target == 13:
            command = '55 AA 05 08 00 C7 D4 EE'
        elif target == 14:
            command = '55 AA 05 08 00 D7 E4 EE'
        elif target == 15:
            command = '55 AA 05 08 00 E7 F4 EE'
        elif target == 16:
            command = '55 AA 05 08 00 F7 04 EE'
    if input==9:
        if target == 1:
            command = '55 AA 05 08 00 08 15 EE'
        elif target == 2:
            command = '55 AA 05 08 00 18 25 EE'
        elif target == 3:
            command = '55 AA 05 08 00 28 35 EE'
        elif target == 4:
            command = '55 AA 05 08 00 38 45 EE'
        elif target == 5:
            command = '55 AA 05 08 00 48 55 EE'
        elif target == 6:
            command = '55 AA 05 08 00 58 65 EE'
        elif target == 7:
            command = '55 AA 05 08 00 68 75 EE'
        elif target == 8:
            command = '55 AA 05 08 00 78 85 EE'
        elif target == 9:
            command = '55 AA 05 08 00 88 95 EE'
        elif target == 10:
            command = '55 AA 05 08 00 98 A5 EE'
        elif target == 11:
            command = '55 AA 05 08 00 A8 B5 EE'
        elif target == 12:
            command = '55 AA 05 08 00 B8 C5 EE'
        elif target == 13:
            command = '55 AA 05 08 00 C8 D5 EE'
        elif target == 14:
            command = '55 AA 05 08 00 D8 E5 EE'
        elif target == 15:
            command = '55 AA 05 08 00 E8 F5 EE'
        elif target == 16:
            command = '55 AA 05 08 00 F8 05 EE'
    if input==10:
        if target == 1:
            command = '55 AA 05 08 00 09 16 EE'
        elif target == 2:
            command = '55 AA 05 08 00 19 26 EE'
        elif target == 3:
            command = '55 AA 05 08 00 29 36 EE'
        elif target == 4:
            command = '55 AA 05 08 00 39 46 EE'
        elif target == 5:
            command = '55 AA 05 08 00 49 56 EE'
        elif target == 6:
            command = '55 AA 05 08 00 59 66 EE'
        elif target == 7:
            command = '55 AA 05 08 00 69 76 EE'
        elif target == 8:
            command = '55 AA 05 08 00 79 86 EE'
        elif target == 9:
            command = '55 AA 05 08 00 89 96 EE'
        elif target == 10:
            command = '55 AA 05 08 00 99 A6 EE'
        elif target == 11:
            command = '55 AA 05 08 00 A9 B6 EE'
        elif target == 12:
            command = '55 AA 05 08 00 B9 C6 EE'
        elif target == 13:
            command = '55 AA 05 08 00 C9 D6 EE'
        elif target == 14:
            command = '55 AA 05 08 00 D9 E6 EE'
        elif target == 15:
            command = '55 AA 05 08 00 E9 F6 EE'
        elif target == 16:
            command = '55 AA 05 08 00 F9 06 EE'
    if input==11:
        if target == 1:
            command = '55 AA 05 08 00 0A 17 EE'
        elif target == 2:
            command = '55 AA 05 08 00 1A 27 EE'
        elif target == 3:
            command = '55 AA 05 08 00 2A 37 EE'
        elif target == 4:
            command = '55 AA 05 08 00 3A 47 EE'
        elif target == 5:
            command = '55 AA 05 08 00 4A 57 EE'
        elif target == 6:
            command = '55 AA 05 08 00 5A 67 EE'
        elif target == 7:
            command = '55 AA 05 08 00 6A 77 EE'
        elif target == 8:
            command = '55 AA 05 08 00 7A 87 EE'
        elif target == 9:
            command = '55 AA 05 08 00 8A 97 EE'
        elif target == 10:
            command = '55 AA 05 08 00 9A A7 EE'
        elif target == 11:
            command = '55 AA 05 08 00 AA B7 EE'
        elif target == 12:
            command = '55 AA 05 08 00 BA C7 EE'
        elif target == 13:
            command = '55 AA 05 08 00 CA D7 EE'
        elif target == 14:
            command = '55 AA 05 08 00 DA E7 EE'
        elif target == 15:
            command = '55 AA 05 08 00 EA F7 EE'
        elif target == 16:
            command = '55 AA 05 08 00 FA 07 EE'
    if input==12:
        if target == 1:
            command = '55 AA 05 08 00 0B 18 EE'
        elif target == 2:
            command = '55 AA 05 08 00 1B 28 EE'
        elif target == 3:
            command = '55 AA 05 08 00 2B 38 EE'
        elif target == 4:
            command = '55 AA 05 08 00 3B 48 EE'
        elif target == 5:
            command = '55 AA 05 08 00 4B 58 EE'
        elif target == 6:
            command = '55 AA 05 08 00 5B 68 EE'
        elif target == 7:
            command = '55 AA 05 08 00 6B 78 EE'
        elif target == 8:
            command = '55 AA 05 08 00 7B 88 EE'
        elif target == 9:
            command = '55 AA 05 08 00 8B 98 EE'
        elif target == 10:
            command = '55 AA 05 08 00 9B A8 EE'
        elif target == 11:
            command = '55 AA 05 08 00 AB B8 EE'
        elif target == 12:
            command = '55 AA 05 08 00 BB C8 EE'
        elif target == 13:
            command = '55 AA 05 08 00 CB D8 EE'
        elif target == 14:
            command = '55 AA 05 08 00 DB E8 EE'
        elif target == 15:
            command = '55 AA 05 08 00 EB F8 EE'
        elif target == 16:
            command = '55 AA 05 08 00 FB 08 EE'
    if input==13:
        if target == 1:
            command = '55 AA 05 08 00 0C 19 EE'
        elif target == 2:
            command = '55 AA 05 08 00 1C 29 EE'
        elif target == 3:
            command = '55 AA 05 08 00 2C 39 EE'
        elif target == 4:
            command = '55 AA 05 08 00 3C 49 EE'
        elif target == 5:
            command = '55 AA 05 08 00 4C 59 EE'
        elif target == 6:
            command = '55 AA 05 08 00 5C 69 EE'
        elif target == 7:
            command = '55 AA 05 08 00 6C 79 EE'
        elif target == 8:
            command = '55 AA 05 08 00 7C 89 EE'
        elif target == 9:
            command = '55 AA 05 08 00 8C 99 EE'
        elif target == 10:
            command = '55 AA 05 08 00 9C A9 EE'
        elif target == 11:
            command = '55 AA 05 08 00 AC B9 EE'
        elif target == 12:
            command = '55 AA 05 08 00 BC C9 EE'
        elif target == 13:
            command = '55 AA 05 08 00 CC D9 EE'
        elif target == 14:
            command = '55 AA 05 08 00 DC E9 EE'
        elif target == 15:
            command = '55 AA 05 08 00 EC F9 EE'
        elif target == 16:
            command = '55 AA 05 08 00 FC 09 EE'
    if input==14:
        if target == 1:
            command = '55 AA 05 08 00 0D 1A EE'
        elif target == 2:
            command = '55 AA 05 08 00 1D 2A EE'
        elif target == 3:
            command = '55 AA 05 08 00 2D 3A EE'
        elif target == 4:
            command = '55 AA 05 08 00 3D 4A EE'
        elif target == 5:
            command = '55 AA 05 08 00 4D 5A EE'
        elif target == 6:
            command = '55 AA 05 08 00 5D 6A EE'
        elif target == 7:
            command = '55 AA 05 08 00 6D 7A EE'
        elif target == 8:
            command = '55 AA 05 08 00 7D 8A EE'
        elif target == 9:
            command = '55 AA 05 08 00 8D 9A EE'
        elif target == 10:
            command = '55 AA 05 08 00 9D AA EE'
        elif target == 11:
            command = '55 AA 05 08 00 AD BA EE'
        elif target == 12:
            command = '55 AA 05 08 00 BD CA EE'
        elif target == 13:
            command = '55 AA 05 08 00 CD DA EE'
        elif target == 14:
            command = '55 AA 05 08 00 DD EA EE'
        elif target == 15:
            command = '55 AA 05 08 00 ED FA EE'
        elif target == 16:
            command = '55 AA 05 08 00 FD 0A EE'
    if input==15:
        if target == 1:
            command = '55 AA 05 08 00 0E 1B EE'
        elif target == 2:
            command = '55 AA 05 08 00 1E 2B EE'
        elif target == 3:
            command = '55 AA 05 08 00 2E 3B EE'
        elif target == 4:
            command = '55 AA 05 08 00 3E 4B EE'
        elif target == 5:
            command = '55 AA 05 08 00 4E 5B EE'
        elif target == 6:
            command = '55 AA 05 08 00 5E 6B EE'
        elif target == 7:
            command = '55 AA 05 08 00 6E 7B EE'
        elif target == 8:
            command = '55 AA 05 08 00 7E 8B EE'
        elif target == 9:
            command = '55 AA 05 08 00 8E 9B EE'
        elif target == 10:
            command = '55 AA 05 08 00 9E AB EE'
        elif target == 11:
            command = '55 AA 05 08 00 AE BB EE'
        elif target == 12:
            command = '55 AA 05 08 00 BE CB EE'
        elif target == 13:
            command = '55 AA 05 08 00 CE DB EE'
        elif target == 14:
            command = '55 AA 05 08 00 DE EB EE'
        elif target == 15:
            command = '55 AA 05 08 00 EE FB EE'
        elif target == 16:
            command = '55 AA 05 08 00 FE 0B EE'
    if input==16:
        if target == 1:
            command = '55 AA 05 08 00 0F 1C EE'
        elif target == 2:
            command = '55 AA 05 08 00 1F 2C EE'
        elif target == 3:
            command = '55 AA 05 08 00 2F 3C EE'
        elif target == 4:
            command = '55 AA 05 08 00 3F 4C EE'
        elif target == 5:
            command = '55 AA 05 08 00 4F 5C EE'
        elif target == 6:
            command = '55 AA 05 08 00 5F 6C EE'
        elif target == 7:
            command = '55 AA 05 08 00 6F 7C EE'
        elif target == 8:
            command = '55 AA 05 08 00 7F 8C EE'
        elif target == 9:
            command = '55 AA 05 08 00 8F 9C EE'
        elif target == 10:
            command = '55 AA 05 08 00 9F AC EE'
        elif target == 11:
            command = '55 AA 05 08 00 AF BC EE'
        elif target == 12:
            command = '55 AA 05 08 00 BF CC EE'
        elif target == 13:
            command = '55 AA 05 08 00 CF DC EE'
        elif target == 14:
            command = '55 AA 05 08 00 DF EC EE'
        elif target == 15:
            command = '55 AA 05 08 00 EF FC EE'
        elif target == 16:
            command = '55 AA 05 08 00 FF 0C EE'

    print("command:"+command)
    return binascii.unhexlify(command.replace(' ',''))


def matrix_all_command_handle(input):
    """
        matrix commnad 변환(all)
    """
    command = ''
    print(input)
    input = int(input)
    if input == 1:
        command = '55 AA 05 08 F0 00 FD EE'
    elif input == 2:
        command = '55 AA 05 08 F1 00 FE EE'
    elif input == 3:
        command = '55 AA 05 08 F2 00 FF EE'
    elif input == 4:
        command = '55 AA 05 08 F3 00 00 EE'
    elif input == 5:
        command = '55 AA 05 08 F4 00 01 EE'
    elif input == 6:
        command = '55 AA 05 08 F5 00 02 EE'
    elif input == 7:
        command = '55 AA 05 08 F6 00 03 EE'
    elif input == 8:
        command = '55 AA 05 08 F7 00 04 EE'
    elif input == 9:
        command = '55 AA 05 08 F8 00 05 EE'
    elif input == 10:
        command = '55 AA 05 08 F9 00 06 EE'
    elif input == 11:
        command = '55 AA 05 08 FA 00 07 EE'
    elif input == 12:
        command = '55 AA 05 08 FB 00 08 EE'
    elif input == 13:
        command = '55 AA 05 08 FC 00 09 EE'
    elif input == 14:
        command = '55 AA 05 08 FD 00 0A EE'
    elif input == 15:
        command = '55 AA 05 08 FE 00 0B EE'
    elif input == 16:
        command = '55 AA 05 08 FF 00 0C EE'
    return bytes.fromhex(command)


def matrix_n_to_n_command_handle():
    """
        matrix commnad 변환(n to n)
    """
    command = '55 AA 05 08 11 00 1E EE'

    return bytes.fromhex(command)

from django.http import JsonResponse, HttpResponseServerError
from django.contrib.auth.decorators import login_required

@login_required(login_url='login_auth')
def control(req):

    id = req.GET.get("id", None)
    input = req.GET.get("input", None)
    target = req.GET.get("target", None)

    if not id or not input or not target:
        return HttpResponseServerError('필수 파라미터가 누락되었습니다')

    try:
        mat = Mat.objects.get(id=id)
    except Exception as e:
        return HttpResponseServerError('시스템을 찾을 수 없습니다')

    client_socket = None
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)
        client_socket.connect((mat.matrix_ip_address, mat.port))

        command = matrix_command_handle(input, target)

        client_socket.sendall(command)
        print("Command sent successfully")

        time.sleep(delay_time)

        list = ['input_a','input_b','input_c','input_d','input_e','input_f','input_g','input_h',
                'input_i','input_j','input_k','input_l','input_m','input_n','input_o','input_p']

        field_index = int(target) - 1
        field_name = list[field_index]
        print(f"Updating field: {field_name} = {input}")

        setattr(mat, field_name, input)
        mat.save()
        print("Database updated successfully")

    except socket.timeout:
        print("ERROR: Socket timeout")
        return HttpResponseServerError('장치 연결 시간 초과. IP 주소와 포트를 확인해주세요.')
    except ConnectionRefusedError:
        print("ERROR: Connection refused")
        return HttpResponseServerError('장치가 연결을 거부했습니다. 장치가 켜져있는지 확인해주세요.')
    except Exception as e:
        print(f"ERROR in control function: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return HttpResponseServerError(f'시스템 오류: {str(e)}')
    finally:
        if client_socket:
            try:
                client_socket.close()
                print("Socket closed")
            except:
                pass

    return redirect('home')

@login_required(login_url='login_auth')
def control_all(req):

    id = req.GET.get("id", None)
    input = req.GET.get("input", None)

    if not id or not input:
        return HttpResponseServerError('필수 파라미터가 누락되었습니다')

    try:
        mat = Mat.objects.get(id=id)
    except Exception as e:
        print(f"Matrix not found: {e}")
        return HttpResponseServerError('시스템을 찾을 수 없습니다')

    client_socket = None
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(10)
        client_socket.connect((mat.matrix_ip_address, mat.port))

        # ALL 명령 사용
        command = matrix_all_command_handle(input)
        print(f"ALL command: {command.hex()}")

        client_socket.sendall(command)
        time.sleep(delay_time)

        # DB에 모든 포트 업데이트
        field_list = ['input_a','input_b','input_c','input_d','input_e','input_f','input_g','input_h',
                      'input_i','input_j','input_k','input_l','input_m','input_n','input_o','input_p']

        for field_name in field_list:
            setattr(mat, field_name, input)

        mat.save()
        print(f"✓ ALL command success: all ports set to input {input}")

    except socket.timeout:
        print("Socket timeout error")
        return HttpResponseServerError('장치 연결 시간 초과')
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        return HttpResponseServerError(f'시스템 오류: {str(e)}')
    finally:
        if client_socket:
            try:
                client_socket.close()
            except:
                pass

    return redirect('home')


@login_required(login_url='login_auth')
def slicer(req):
    id = req.GET.get("id", None)
    input = req.GET.get("input", None)

    try:
        mat = Mat.objects.get(id=id)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((mat.matrix_ip_address, mat.port))
        command = slicer_command_handle(input)

        client_socket.sendall(command)
        time.sleep(delay_time)

        client_socket.sendall(command)
        time.sleep(delay_time)
        client_socket.close()

    except TimeoutError:
        return HttpResponseServerError('장치와의 연결이 실패했습니다. 연결을 확인해주세요.')
    except Exception as e:
        pass

    return redirect('home')


@login_required(login_url='login_auth')
def kvm(req):

    id = req.GET.get("id", None)
    input = req.GET.get("input", None)

    if isinstance(input, str) and len(input) < 2:
        input = "0"+input

    try:
        kvm = Mat.objects.get(id=id)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)
        client_socket.connect((kvm.kvm_ip_address, kvm.port))

        command = kvm_command_handle(input)
        client_socket.sendall(command)

        time.sleep(0.3)
        response = client_socket.recv(1024)

        if len(response) >= 4:
            if response[0:2] == b'\x55\xaa':
                length = response[2]

                if length == 0x3B and len(response) >= 62:
                    kvm.kvm_input = input
                    kvm.save()

        client_socket.close()

    except socket.timeout:
        return HttpResponseServerError('KVM 장치 응답 시간 초과')
    except TimeoutError:
        return HttpResponseServerError('장치와의 연결이 실패했습니다. 연결을 확인해주세요.')
    except Exception as e:
        import traceback
        traceback.print_exc()

    return redirect('home')

import threading

connection_pool = {}
connection_lock = threading.Lock()

def get_connection(ip, port):
    """재사용 가능한 연결 가져오기"""
    key = f"{ip}:{port}"

    with connection_lock:
        if key in connection_pool:
            try:
                conn = connection_pool[key]
                keepalive = bytes.fromhex("55 AA 04 04 5A 62 EE")
                conn.sendall(keepalive)
                return conn
            except:
                del connection_pool[key]

        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.settimeout(3)
        conn.connect((ip, port))
        connection_pool[key] = conn
        return conn

@login_required(login_url='login_auth')
def profile_control(req):
    profile_id = req.GET.get("id", None)
    try:
        profile = Profile.objects.get(id=profile_id)
        mat_set = MatrixSetting.objects.filter(profile=profile)
        mat_set_serializers = MatrixSettingSerializer(mat_set, many=True).data
    except Exception as e:
        print(e)

    try:
        for i in mat_set:
            is_all = 0
            check_n_to_n = 0

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((i.matrix.matrix_ip_address, i.matrix.port))
            input_list = [i.input_a, i.input_b, i.input_c, i.input_d, i.input_e, i.input_f, i.input_g, i.input_h, i.input_i, i.input_j, i.input_k, i.input_l, i.input_m, i.input_n, i.input_o, i.input_p]
            counter_list = Counter(input_list)
            keys = counter_list.keys()
            for key in keys:
                if key != "00" and int(counter_list[key]) > 4:
                    is_all = int(key)
                    command = matrix_all_command_handle(key)
                    client_socket.sendall(command)
                    time.sleep(delay_time)
                    break

            # n to n 확인
            for j in range(16):
                if int(input_list[j]) == j+1:
                    check_n_to_n += 1

            if is_all:
                for j in range(16):

                    if int(input_list[j]) != 0 and int(input_list[j]) != is_all:
                        command = matrix_command_handle(input_list[j], j+1)
                        client_socket.sendall(command)
                        time.sleep(delay_time)

            elif check_n_to_n >= 4:

                command = matrix_n_to_n_command_handle()
                client_socket.sendall(command)
                time.sleep(delay_time)
                for j in range(16):
                    if int(input_list[j]) != 0 and int(input_list[j]) != j+1:
                        command = matrix_command_handle(input_list[j], j+1)
                        client_socket.sendall(command)
                        time.sleep(delay_time)

            else:
                for j in range(16):
                    if int(input_list[j]) != 0:
                        command = matrix_command_handle(input_list[j], j+1)
                        client_socket.sendall(command)
                        time.sleep(delay_time)

            if int(i.input_kvm) != 0:
                command = kvm_command_handle(i.input_kvm)
                client_socket.sendall(command)
                time.sleep(delay_time)

                client_socket.close()

        for mat_set_serializer in mat_set_serializers:
            matrix = Mat.objects.get(id=mat_set_serializer["matrix"])
            mat_input_list = ['input_a','input_b','input_c','input_d','input_e','input_f','input_g','input_h','input_i','input_j','input_k','input_l','input_m','input_n','input_o','input_p',]
            for mat_input in mat_input_list:
                if int(mat_set_serializer[mat_input]) != 0:
                    setattr(matrix, mat_input, mat_set_serializer[mat_input])
            matrix.save()

    except TimeoutError:
        return HttpResponseServerError('장치와의 연결이 실패했습니다. 연결을 확인해주세요.')
    except Exception as e:
        print(e)

    return redirect('home')

@license_auth
def login(req):

    return render(req, 'login/login.html', {})

@login_required(login_url='login_auth')
def system_template(req):

    if req.user.userpermission.permission != 0:
        return redirect('home')

    matrix = Mat.objects.all().order_by("created_date")
    main_connect_list = [1, 2, 3, 4]
    for i in matrix:
        if i.main_connect in main_connect_list:
            main_connect_list.remove(i.main_connect)
    context = {'matrix': matrix, 'main_connect_list': main_connect_list}
    return render(req, 'system_template/system_template.html', context)

@method_decorator(login_required, name='post')
class MatrixDetailView(APIView):
    def post(self, req):

        data= req.data
        matrix = Mat.objects.get(id=data['id'])
        if data["_method"] == 'delete':
            matrix.delete()
        elif data["_method"] == 'put':
            list = ['name', 'matrix_ip_address', 'kvm_ip_address', 'kvm_ip_address2', 'port', 'is_main', 'main_connect']
            for i in data:
                if i in list:
                    setattr(matrix, i, data[i])
            matrix.save()

        return redirect('system_template')


@method_decorator(login_required, name='post')
class MatrixView(APIView):
    def post(self, req):

        data = req.data
        matrix = Mat.objects.create()
        list = ['name', 'matrix_ip_address', 'kvm_ip_address', 'kvm_ip_address2', 'port', 'is_main', 'main_connect']
        for i in data:
            if i in list:
                setattr(matrix, i, data[i])
        matrix.save()

        return redirect('system_template')


@login_required(login_url='login_auth')
def profile_template(req):

    if req.user.userpermission.permission == 2:
        return redirect('home')

    sub_mat = Mat.objects.filter(is_main=False)
    sub_mat = sub_mat.order_by("main_connect")
    main_mat = Mat.objects.filter(is_main=True)
    profile = Profile.objects.all().order_by('order', 'id')

    connect = ['입력01', '입력02', '입력03', '입력04']
    for i in range(0, len(sub_mat)):
        connect[i] = sub_mat[i].name

    context = {'sub_mat': sub_mat, 'profile': profile, 'main_mat': main_mat, 'connect_list': connect}

    return render(req, 'profile_template/profile_template.html', context)

@method_decorator(login_required, name='post')
class ProfileView(APIView):
    def post(self, req):

        data = req.data

        profile = Profile.objects.create(name=data["name"])
        profile.save()

        mat_id_list = data["mat_id_list"].split(',')
        mat_input_list = ['input_a','input_b','input_c','input_d','input_e','input_f','input_g','input_h','input_i','input_j','input_k','input_l','input_m','input_n','input_o','input_p', 'input_kvm']

        for i in range(len(mat_id_list)):
            mat = Mat.objects.get(id=mat_id_list[i])

            # get_or_create 사용으로 중복 방지
            mat_set, created = MatrixSetting.objects.get_or_create(
                profile=profile,
                matrix=mat,
                defaults={}
            )

            for j in data:
                if j in mat_input_list:
                    setattr(mat_set, j, data[j].split(',')[i])

            mat_set.save()

        return redirect('profile_template')


@method_decorator(login_required, name='post')
class ProfileDetailView(APIView):
    def get(self, req):
        try:
            id = req.GET.get("id", None)
            mat_set = MatrixSetting.objects.filter(profile=id)
            mat_set_serializer = MatrixSettingSerializer(mat_set, many=True).data

            return Response(data=mat_set_serializer)
        except Exception as e:
            return HttpResponseServerError("잘못된 프로필 데이터입니다.")

    def post(self, req):

        data = req.data
        try:
            profile = Profile.objects.get(id=data['id'])
            print(data)
            if data["_method"] == 'delete':
                profile.delete()
            elif data["_method"] == 'put':
                setattr(profile, 'name', data["name"])
                profile.save()
                mat_id_list = data["mat_id_list"].split(',')
                mat_input_list = ['input_a','input_b','input_c','input_d','input_e','input_f','input_g','input_h','input_i','input_j','input_k','input_l','input_m','input_n','input_o','input_p', 'input_kvm',]
                for i in range(len(mat_id_list)):

                    mat = Mat.objects.get(id=mat_id_list[i])
                    mat_set = MatrixSetting.objects.get(profile=profile, matrix=mat)
                    for mat_input in mat_input_list:
                        print(mat_input)
                        setattr(mat_set, mat_input, data[mat_input].split(',')[i])
                    mat_set.save()
        except Exception as e:
            print(e)
            return HttpResponseServerError('수정 오류')

        return redirect('profile_template')


@method_decorator(login_required, name='post')
class MatrixExportView(APIView):
    def post(self, req):

        data = req.data
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="system_export.csv"'},
        )
        writer = csv.writer(response)
        for i in data["export_mat_list"].split(","):
            mat = Mat.objects.get(id=i)
            mat_serializer = MatrixSerializer(mat).data
            writer.writerow([mat_serializer["name"], mat_serializer["matrix_ip_address"], mat_serializer["kvm_ip_address"], mat_serializer["kvm_ip_address2"], mat_serializer["port"], mat_serializer["is_main"], mat_serializer["main_connect"]])

        return response


@method_decorator(login_required, name='post')
class MatrixImportView(APIView):
    def post(self, req):

        data = req.data
        file = data["matrix_file"]

        read = file.read().decode('utf8')
        readLine = read.split('\n')
        for line in readLine:
            if len(line) > 0:
                line_split = line.split(',')
                mat = Mat.objects.create(name=line_split[0], matrix_ip_address=line_split[1], kvm_ip_address=line_split[2], kvm_ip_address2=line_split[3], port=line_split[4], is_main=line_split[5], main_connect=line_split[6])
                mat.save()

        return redirect('system_template')


@method_decorator(login_required, name='post')
class ProfileExportView(APIView):
    def post(self, req):

        data = req.data
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="profile_export.csv"'},
        )
        response.write(u'\ufeff'.encode('utf-8'))
        writer = csv.writer(response)
        for i in data["export_pro_list"].split(","):
            profile = Profile.objects.get(id=i)
            profile_ser = ProfileSerializer(profile).data
            mat_set = MatrixSetting.objects.filter(profile=profile)
            writer.writerow(["profile", profile_ser["name"]])
            for set in mat_set:
                set_ser = MatrixSettingSerializer(set).data
                writer.writerow(["matrix_setting", set_ser["matrix_name"], set_ser["input_a"], set_ser["input_b"], set_ser["input_c"], set_ser["input_d"], set_ser["input_e"], set_ser["input_f"], set_ser["input_g"], set_ser["input_h"], set_ser["input_i"], set_ser["input_j"], set_ser["input_k"], set_ser["input_l"], set_ser["input_m"], set_ser["input_n"], set_ser["input_o"], set_ser["input_p"], set_ser["input_kvm"]])

        return response


@method_decorator(login_required, name='post')
class ProfileImportView(APIView):
    def post(self, req):

        data = req.data
        file = data["profile_file"]
        read = file.read().decode('utf-8-sig')
        readLine = read.split('\n')
        pro = ''
        for line in readLine:
            if len(line) > 0:
                line_split = line.strip().split(',')
                if line_split[0] == "profile":
                    pro = Profile.objects.create(name=line_split[1])
                    pro.save()
                else:
                    mat = Mat.objects.get(name=line_split[1])
                    mat_set = MatrixSetting.objects.create(profile=pro, matrix=mat)
                    input_list = ['input_a','input_b','input_c','input_d','input_e','input_f','input_g','input_h','input_i','input_j','input_k','input_l','input_m','input_n','input_o','input_p', 'input_kvm',]
                    for i in range(9):
                        if len(line_split[i+2])<2 and int(line_split[i+2])<10:
                            line_split[i+2] = "0"+line_split[i+2]
                        setattr(mat_set, input_list[i], line_split[i+2])
                    mat_set.save()

        return redirect('profile_template')


class LicenseAuthView(APIView):
    def post(self, req):
        key = req.data["license"]

        try:
            license = License.objects.all()
        except Exception as e:
            print(e)
        if license:
            setattr(license[0], "key", key)
            license[0].save()
        else:
            license = License.objects.create(key=key)
            license.save()

        return redirect('login_auth')

def slicer(request):
    matrix_id = request.GET.get('id')
    input_val = request.GET.get('input')
    target = request.GET.get('target')

    return JsonResponse({'status': 'success'})

@login_required(login_url='login_auth')
def matrix_update_names(request, matrix_id):

    try:
        matrix = Mat.objects.get(id=matrix_id)
    except Mat.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '매트릭스를 찾을 수 없습니다.'
        }, status=404)

    if request.method == 'POST':
        try:
            position = int(request.POST.get('position', 1))
            monitor_name = request.POST.get('monitor_name', '').strip()
            device_name = request.POST.get('device_name', '').strip()

            # 16포트 지원 (position 1~16)
            if position < 1 or position > 16:
                return JsonResponse({
                    'success': False,
                    'message': '올바르지 않은 포지션입니다. (1-16 범위)'
                }, status=400)

            index = position - 1

            if not isinstance(matrix.monitor_names, list) or len(matrix.monitor_names) < 16:
                matrix.monitor_names = [f"모니터 {i+1:02d}" for i in range(16)]

            if not isinstance(matrix.device_names, list) or len(matrix.device_names) < 16:
                matrix.device_names = [f"입력 {i+1:02d}" for i in range(16)]

            if monitor_name:
                matrix.monitor_names[index] = monitor_name
            if device_name:
                matrix.device_names[index] = device_name

            matrix.save()

            return JsonResponse({
                'success': True,
                'message': '이름이 성공적으로 업데이트되었습니다.',
                'monitor_name': matrix.monitor_names[index],
                'device_name': matrix.device_names[index]
            })

        except (ValueError, IndexError) as e:
            return JsonResponse({
                'success': False,
                'message': f'잘못된 요청입니다: {str(e)}'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'서버 오류가 발생했습니다: {str(e)}'
            }, status=500)

    try:
        if not isinstance(matrix.monitor_names, list) or len(matrix.monitor_names) < 16:
            matrix.monitor_names = [f"모니터 {i+1:02d}" for i in range(16)]

        if not isinstance(matrix.device_names, list) or len(matrix.device_names) < 16:
            matrix.device_names = [f"입력 {i+1:02d}" for i in range(16)]

        matrix.save()

        return JsonResponse({
            'success': True,
            'monitor_names': matrix.monitor_names,
            'device_names': matrix.device_names
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'서버 오류가 발생했습니다: {str(e)}'
        }, status=500)

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required(login_url='login_auth')
@csrf_exempt
def save_monitor_layout(request):

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST 요청만 허용됩니다.'})

    try:
        data = json.loads(request.body)
        matrix_id = data.get('matrix_id')
        layout_data = data.get('layout_data', [])

        if not matrix_id:
            return JsonResponse({'success': False, 'message': 'matrix_id가 필요합니다.'})

        try:
            matrix = Mat.objects.get(id=matrix_id)
        except Mat.DoesNotExist:
            return JsonResponse({'success': False, 'message': '매트릭스를 찾을 수 없습니다.'})

        user = request.user

        MonitorLayout.objects.filter(user=user, matrix=matrix).delete()

        for item in layout_data:
            monitor_position = int(item.get('monitor_position'))
            row_position = int(item.get('row_position', 1))
            col_position = int(item.get('col_position', 1))
            display_order = int(item.get('display_order', 0))
            is_visible = item.get('is_visible', True)

            if monitor_position < 1 or monitor_position > 16:
                continue

            MonitorLayout.objects.create(
                user=user,
                matrix=matrix,
                monitor_position=monitor_position,
                row_position=row_position,
                col_position=col_position,
                display_order=display_order,
                is_visible=is_visible
            )

        return JsonResponse({
            'success': True,
            'message': '레이아웃이 성공적으로 저장되었습니다.',
            'saved_count': len(layout_data)
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '잘못된 JSON 데이터입니다.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})

@login_required(login_url='login_auth')
def get_monitor_layout(request, matrix_id):

    try:
        matrix = Mat.objects.get(id=matrix_id)
    except Mat.DoesNotExist:
        return JsonResponse({'success': False, 'message': '매트릭스를 찾을 수 없습니다.'})

    user = request.user

    layouts = MonitorLayout.objects.filter(user=user, matrix=matrix).order_by('display_order')

    layout_data = []
    for layout in layouts:
        layout_data.append({
            'monitor_position': layout.monitor_position,
            'row_position': layout.row_position,
            'col_position': layout.col_position,
            'display_order': layout.display_order,
            'is_visible': layout.is_visible
        })

    if not layout_data:
        for i in range(1, 17):
            row = 1 if i <= 8 else 2
            col = i if i <= 8 else i - 8
            layout_data.append({
                'monitor_position': i,
                'row_position': row,
                'col_position': col,
                'display_order': i - 1,
                'is_visible': True
            })

    return JsonResponse({
        'success': True,
        'layout_data': layout_data
    })

@login_required(login_url='login_auth')
@csrf_exempt
def reset_monitor_layout(request):

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST 요청만 허용됩니다.'})

    try:
        data = json.loads(request.body)
        matrix_ids = data.get('matrix_ids', [])
        user = request.user

        if not matrix_ids:
            total_deleted = MonitorLayout.objects.filter(user=user).delete()[0]
            return JsonResponse({
                'success': True,
                'message': f'모든 레이아웃이 초기화되었습니다. ({total_deleted}개 항목 삭제)',
                'deleted_count': total_deleted,
                'reset_type': 'all'
            })

        total_deleted = 0
        reset_matrices = []

        for matrix_id in matrix_ids:
            try:
                matrix = Mat.objects.get(id=matrix_id)
                deleted_count = MonitorLayout.objects.filter(user=user, matrix=matrix).delete()[0]
                total_deleted += deleted_count
                reset_matrices.append({
                    'matrix_id': matrix_id,
                    'matrix_name': matrix.name,
                    'deleted_count': deleted_count
                })

                print(f"Reset layout for matrix {matrix_id} ({matrix.name}): {deleted_count} items deleted")

            except Mat.DoesNotExist:
                print(f"Matrix with ID {matrix_id} not found, skipping")
                continue

        if reset_matrices:
            return JsonResponse({
                'success': True,
                'message': f'선택된 매트릭스의 레이아웃이 초기화되었습니다. (총 {total_deleted}개 항목 삭제)',
                'total_deleted': total_deleted,
                'reset_matrices': reset_matrices,
                'reset_type': 'selected'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '유효한 매트릭스를 찾을 수 없습니다.'
            })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '잘못된 JSON 데이터입니다.'})
    except Exception as e:
        print(f"Error in reset_monitor_layout: {str(e)}")
        return JsonResponse({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})

@login_required(login_url='login_auth')
@csrf_exempt
def toggle_monitor_visibility(request):

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST 요청만 허용됩니다.'})

    try:
        data = json.loads(request.body)
        matrix_id = data.get('matrix_id')
        monitor_position = int(data.get('monitor_position'))
        is_visible = data.get('is_visible', True)

        if not matrix_id or not monitor_position:
            return JsonResponse({'success': False, 'message': 'matrix_id와 monitor_position이 필요합니다.'})

        try:
            matrix = Mat.objects.get(id=matrix_id)
        except Mat.DoesNotExist:
            return JsonResponse({'success': False, 'message': '매트릭스를 찾을 수 없습니다.'})

        user = request.user

        layout, created = MonitorLayout.objects.get_or_create(
            user=user,
            matrix=matrix,
            monitor_position=monitor_position,
            defaults={
                'row_position': 1 if monitor_position <= 8 else 2,
                'col_position': monitor_position if monitor_position <= 8 else monitor_position - 8,
                'display_order': monitor_position - 1,
                'is_visible': is_visible
            }
        )

        if not created:
            layout.is_visible = is_visible
            layout.save()

        return JsonResponse({
            'success': True,
            'message': f'모니터 {monitor_position}의 가시성이 {"표시" if is_visible else "숨김"}로 변경되었습니다.',
            'is_visible': is_visible
        })

    except (ValueError, json.JSONDecodeError):
        return JsonResponse({'success': False, 'message': '잘못된 데이터입니다.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})


from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required(login_url='login_auth')
@csrf_exempt
def save_monitor_layout(request):

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST 요청만 허용됩니다.'})

    try:
        data = json.loads(request.body)
        layout_data = data.get('layout_data', [])
        user = request.user

        if not layout_data:
            return JsonResponse({'success': False, 'message': '저장할 레이아웃 데이터가 없습니다.'})

        saved_count = 0

        for matrix_layout in layout_data:
            matrix_id = matrix_layout.get('matrix_id')
            monitors = matrix_layout.get('monitors', [])

            if not matrix_id:
                continue

            try:
                matrix = Mat.objects.get(id=matrix_id)
            except Mat.DoesNotExist:
                continue

            MonitorLayout.objects.filter(user=user, matrix=matrix).delete()

            for monitor_data in monitors:
                position = monitor_data.get('position')
                row = monitor_data.get('row', 1)
                col = monitor_data.get('col', position)
                display_order = monitor_data.get('display_order', 0)
                is_visible = monitor_data.get('is_visible', True)

                if position and 1 <= position <= 16:  # 16포트 지원
                    MonitorLayout.objects.create(
                        user=user,
                        matrix=matrix,
                        monitor_position=position,
                        display_order=display_order,
                        is_visible=is_visible,
                        row_position=row,
                        col_position=col
                    )
                    saved_count += 1

        return JsonResponse({
            'success': True,
            'message': f'레이아웃이 저장되었습니다. ({saved_count}개 모니터)',
            'saved_count': saved_count
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '잘못된 JSON 데이터입니다.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})

@login_required(login_url='login_auth')
def get_monitor_layout(request, matrix_id):

    try:
        try:
            matrix = Mat.objects.get(id=matrix_id)
        except Mat.DoesNotExist:
            return JsonResponse({'success': False, 'message': '매트릭스를 찾을 수 없습니다.'})

        user = request.user

        layouts = MonitorLayout.objects.filter(
            user=user,
            matrix=matrix
        ).order_by('display_order')

        if layouts.exists():
            layout_data = []
            for layout in layouts:
                layout_data.append({
                    'position': layout.monitor_position,
                    'row': layout.row_position,
                    'col': layout.col_position,
                    'display_order': layout.display_order,
                    'is_visible': layout.is_visible
                })

            return JsonResponse({
                'success': True,
                'layout_data': layout_data,
                'total_monitors': len(layout_data),
                'has_saved_layout': True
            })
        else:
            default_layout = []
            for i in range(1, 17):
                row = 1 if i <= 8 else 2
                col = i if i <= 8 else i - 8
                default_layout.append({
                    'position': i,
                    'row': row,
                    'col': col,
                    'display_order': i - 1,
                    'is_visible': True
                })

            return JsonResponse({
                'success': True,
                'layout_data': default_layout,
                'total_monitors': len(default_layout),
                'has_saved_layout': False,
                'message': '기본 레이아웃을 반환합니다.'
            })

    except Exception as e:
        print(f"Error in get_monitor_layout: {str(e)}")
        return JsonResponse({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})

@login_required(login_url='login_auth')
def debug_layout_status(request):

    user = request.user

    all_matrices = Mat.objects.all()

    layout_status = []
    for matrix in all_matrices:
        layouts = MonitorLayout.objects.filter(user=user, matrix=matrix)
        layout_status.append({
            'matrix_id': matrix.id,
            'matrix_name': matrix.name,
            'layout_count': layouts.count(),
            'layouts': [
                {
                    'position': layout.monitor_position,
                    'row': layout.row_position,
                    'col': layout.col_position,
                    'visible': layout.is_visible,
                    'order': layout.display_order
                }
                for layout in layouts.order_by('display_order')
            ]
        })

    return JsonResponse({
        'success': True,
        'user': user.username,
        'total_matrices': len(all_matrices),
        'layout_status': layout_status
    })

@login_required(login_url='login_auth')
@csrf_exempt
def reset_monitor_layout(request):

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST 요청만 허용됩니다.'})

    try:
        data = json.loads(request.body)
        matrix_id = data.get('matrix_id')
        user = request.user

        if matrix_id:
            # 특정 매트릭스의 레이아웃만 초기화
            try:
                matrix = Mat.objects.get(id=matrix_id)
                deleted_count = MonitorLayout.objects.filter(user=user, matrix=matrix).delete()[0]
                return JsonResponse({
                    'success': True,
                    'message': f'레이아웃이 초기화되었습니다. ({deleted_count}개 항목 삭제)',
                    'deleted_count': deleted_count
                })
            except Mat.DoesNotExist:
                return JsonResponse({'success': False, 'message': '매트릭스를 찾을 수 없습니다.'})
        else:
            # 모든 레이아웃 초기화
            deleted_count = MonitorLayout.objects.filter(user=user).delete()[0]
            return JsonResponse({
                'success': True,
                'message': f'모든 레이아웃이 초기화되었습니다. ({deleted_count}개 항목 삭제)',
                'deleted_count': deleted_count
            })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '잘못된 JSON 데이터입니다.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})


@login_required(login_url='login_auth')
@csrf_exempt
def toggle_monitor_visibility(request):
    """
    모니터의 표시/숨김 상태를 토글
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST 요청만 허용됩니다.'})

    try:
        data = json.loads(request.body)
        matrix_id = data.get('matrix_id')
        position = data.get('position')
        user = request.user

        if not matrix_id or not position:
            return JsonResponse({'success': False, 'message': 'matrix_id와 position이 필요합니다.'})

        try:
            matrix = Mat.objects.get(id=matrix_id)
        except Mat.DoesNotExist:
            return JsonResponse({'success': False, 'message': '매트릭스를 찾을 수 없습니다.'})

        # 기존 레이아웃 설정 찾기 또는 생성
        layout, created = MonitorLayout.objects.get_or_create(
            user=user,
            matrix=matrix,
            monitor_position=position,
            defaults={
                'display_order': position,
                'is_visible': True,
                'row_position': 1 if position <= 8 else 2,
                'col_position': position if position <= 8 else position - 8
            }
        )

        # 가시성 토글
        layout.is_visible = not layout.is_visible
        layout.save()

        # 모니터 이름 가져오기 (있는 경우)
        monitor_name = f'모니터 {position:02d}'
        if hasattr(matrix, 'monitor_names') and isinstance(matrix.monitor_names, list):
            if len(matrix.monitor_names) >= position:
                monitor_name = matrix.monitor_names[position - 1]

        return JsonResponse({
            'success': True,
            'visible': layout.is_visible,
            'position': position,
            'matrix_id': matrix_id,
            'monitor_name': monitor_name,
            'message': f'{monitor_name}이(가) {"표시" if layout.is_visible else "숨김"} 상태로 변경되었습니다.'
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '잘못된 JSON 데이터입니다.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})

@login_required(login_url='login_auth')
def get_hidden_monitors(request):
    """
    숨겨진 모니터 목록을 반환
    """
    try:
        matrix_id = request.GET.get('matrix_id')
        if not matrix_id:
            return JsonResponse({'success': False, 'message': 'matrix_id가 필요합니다.'})

        try:
            matrix = Mat.objects.get(id=matrix_id)
        except Mat.DoesNotExist:
            return JsonResponse({'success': False, 'message': '매트릭스를 찾을 수 없습니다.'})

        user = request.user
        hidden_monitors = []

        # 16포트 모니터 확인 (1~16)
        for position in range(1, 17):
            visibility_key = f'visibility_{user.id}_{matrix_id}_{position}'
            is_visible = request.session.get(visibility_key, True)

            if not is_visible:
                hidden_monitors.append({
                    'position': position,
                    'name': f'모니터 {position:02d}',
                    'matrix_id': matrix_id
                })

        return JsonResponse({
            'success': True,
            'hidden_monitors': hidden_monitors
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})

# 기존의 임시 함수들을 실제 구현으로 교체
@csrf_exempt
def toggle_monitor(request):
    """기존 toggle_monitor 함수를 toggle_monitor_visibility로 리다이렉트"""
    return toggle_monitor_visibility(request)

@csrf_exempt
def save_layout(request):
    """기존 save_layout 함수를 save_monitor_layout으로 리다이렉트"""
    return save_monitor_layout(request)

@csrf_exempt
def reset_layout(request):
    """기존 reset_layout 함수를 reset_monitor_layout로 리다이렉트"""
    return reset_monitor_layout(request)

def hidden_monitors(request):
    """기존 hidden_monitors 함수를 get_hidden_monitors로 리다이렉트"""
    return get_hidden_monitors(request)

@csrf_exempt
def restore_monitor(request):
    """숨겨진 모니터 복원 (toggle_monitor_visibility 재사용)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST 요청만 허용됩니다.'})

    try:
        data = json.loads(request.body)
        data['is_visible'] = True  # 복원이므로 항상 True

        # toggle_monitor_visibility 함수 재사용
        request._body = json.dumps(data).encode('utf-8')
        return toggle_monitor_visibility(request)

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})

@login_required(login_url='login_auth')
def get_hardware_status(request):
    """
    하드웨어 상태를 조회하여 UI에 반영
    """
    try:
        # 실제 하드웨어와 통신하는 로직이 필요
        # 여기서는 임시로 더미 데이터 반환
        hardware_data = {}

        matrices = Mat.objects.all()
        for matrix in matrices:
            hardware_data[str(matrix.id)] = {
                'kvm_input': 1,  # 현재 KVM 입력
                'input_a': '01',
                'input_b': '02',
                'input_c': '03',
                'input_d': '04',
                'input_e': '05',
                'input_f': '06',
                'input_g': '07',
                'input_h': '08',
                'input_i': '09',
                'input_j': '10',
                'input_k': '11',
                'input_l': '12',
                'input_m': '13',
                'input_n': '14',
                'input_o': '15',
                'input_p': '16'
            }

        return JsonResponse({
            'status': 'success',
            'data': hardware_data
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'하드웨어 상태 조회 중 오류가 발생했습니다: {str(e)}'
        })

@login_required(login_url='login_auth')
@csrf_exempt
def matrix_order_update(request):

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST 요청만 허용됩니다.'})

    try:
        data = json.loads(request.body)
        order = data.get('order', [])

        user = request.user
        request.session[f'matrix_order_{user.id}'] = order

        return JsonResponse({
            'success': True,
            'message': '순서가 저장되었습니다.'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})

from .hardware_ip_changer import scan_devices, change_ip
from .rpi_ip_changer import get_current_ip, change_rpi_ip
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_protect

@require_http_methods(["GET"])
def scan_kvm_devices(request):
    """하드웨어 IP 스캔"""
    try:
        current_ip = _get_current_ip()
        devices = scan_devices(current_ip)

        return JsonResponse({
            "success": True,
            "devices": devices,
            "count": len(devices)
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        })

@csrf_protect
@require_POST
def change_hardware_ip(request):
    """하드웨어 장비 IP 변경"""
    try:
        body = json.loads(request.body)
        current_ip = body.get('current_ip')
        new_ip = body.get('new_ip')

        if not current_ip or not new_ip:
            return JsonResponse({
                'success': False,
                'error': 'IP 주소가 올바르지 않습니다.'
            })

        change_ip(current_ip, new_ip)
        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required(login_url='login_auth')
@require_http_methods(["GET"])
def get_rpi_ip(request):
    """라즈베리파이의 현재 IP 주소 조회"""
    try:
        current_ip = get_current_ip()

        return JsonResponse({
            "success": True,
            "ip": current_ip
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        })

# ========== 라즈베리파이 IP 변경 (추가) ==========
@require_POST
def change_rpi_ip_view(request):
    """라즈베리파이 IP 변경"""
    try:
        data = json.loads(request.body)
        new_ip = data.get("new_ip")

        if not new_ip:
            return JsonResponse({
                "success": False,
                "error": "IP 정보 누락"
            })

        success, message = change_rpi_ip(new_ip)
        return JsonResponse({
            "success": success,
            "error": None if success else message
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        })

from django.contrib.auth.decorators import login_required

@login_required(login_url='login_auth')
def check_session_time(req):

    if not req.session.get('system_access'):
        return JsonResponse({
            'valid': False,
            'remaining': 0,
            'remaining_formatted': '00:00'
        })

    access_time = req.session.get('system_access_time', 0)
    current_time = time.time()
    remaining = 600 - (current_time - access_time)

    if remaining <= 0:
        req.session.pop('system_access', None)
        req.session.pop('system_access_time', None)
        req.session.pop('system_access_user', None)
        return JsonResponse({
            'valid': False,
            'remaining': 0,
            'remaining_formatted': '00:00'
        })

    minutes = int(remaining // 60)
    seconds = int(remaining % 60)

    return JsonResponse({
        'valid': True,
        'remaining': int(remaining),
        'remaining_formatted': f'{minutes:02d}:{seconds:02d}',
        'user': req.session.get('system_access_user')
    })

@login_required
def system_logout(req):
    """
    시스템 관리 세션 명시적 종료
    """
    req.session.pop('system_access', None)
    req.session.pop('system_access_time', None)
    req.session.pop('system_access_user', None)

    return JsonResponse({'success': True, 'message': '시스템 관리 세션이 종료되었습니다.'})

import os
import subprocess
from urllib.parse import urlparse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, resolve

def _has_system_access(req):

    ok = req.session.get('system_access') is True
    ts = req.session.get('system_access_time')
    return ok and ts and (time.time() - ts) < 600  # 10분

def check_system_access(req):

    if not req.session.get('system_access'):
        return False

    access_time = req.session.get('system_access_time', 0)
    current_time = time.time()

    if current_time - access_time > 600:
        req.session.pop('system_access', None)
        req.session.pop('system_access_time', None)
        req.session.pop('system_access_user', None)
        return False
    req.session['system_access_time'] = current_time

    return True

# get_current_ip 함수 추가
def get_current_ip():
    """현재 서버의 IP 주소"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "192.168.1.1"

def _check_ip_permission():
    """IP 변경 권한 설정 여부 확인 (sudoers 파일 존재 확인)"""
    return os.path.exists('/etc/sudoers.d/matrix_ip_change')

@never_cache
@login_required(login_url='login_auth')
def system_password(req):
    """시스템 비밀번호 입력 페이지"""
    return render(req, 'system_template/system_password.html', {
        'user': req.user,
        'current_time': time.strftime('%Y-%m-%d %H:%M:%S')
    })

@never_cache
@login_required(login_url='login_auth')
@require_POST
def verify_system_password(req):
    """시스템 비밀번호 검증"""
    SYSTEM_PASSWORD = "admin123"  # 8포트와 동일한 비밀번호

    data = json.loads(req.body or "{}")
    input_password = data.get('password', '').strip()

    raw_next = data.get('next') or reverse('on_device')

    path = urlparse(raw_next).path
    if not path.startswith('/'):
        path = '/' + path

    allowed_names = {'on_device', 'system_template'}
    try:
        resolved_name = resolve(path).url_name
    except Exception:
        resolved_name = None

    # 허용 안 되면 on_device로 강제
    if resolved_name not in allowed_names:
        next_url = reverse('on_device')
    else:
        next_url = path

    if not input_password:
        return HttpResponse(
            json.dumps({'success': False, 'message': '비밀번호를 입력해주세요.'}),
            content_type='application/json', status=400
        )

    if input_password == SYSTEM_PASSWORD:
        req.session['system_access'] = True
        req.session['system_access_time'] = time.time()
        req.session['system_access_user'] = req.user.username
        req.session.modified = True
        return HttpResponse(
            json.dumps({'success': True, 'redirect_url': next_url}),
            content_type='application/json'
        )
    else:
        return HttpResponse(
            json.dumps({'success': False, 'message': '비밀번호가 올바르지 않습니다.'}),
            content_type='application/json', status=401
        )

@never_cache
@login_required(login_url='login_auth')
def system_template(req):

    if req.user.userpermission.permission != 0:
        return redirect('home')

    # 시스템 접근 권한 확인
    if not check_system_access(req):
        # 비밀번호 입력 페이지로 리다이렉트
        return render(req, 'system_template/system_password.html', {
            'user': req.user,
            'current_time': time.strftime('%Y-%m-%d %H:%M:%S')
        })

    matrix = Mat.objects.all().order_by("created_date")
    main_connect_list = [1, 2, 3, 4]
    for i in matrix:
        if i.main_connect in main_connect_list:
            main_connect_list.remove(i.main_connect)

    # 남은 시간 계산
    remaining_time = 600 - (time.time() - req.session.get('system_access_time', time.time()))

    return render(req, 'system_template/system_template.html', {
        'matrix': matrix,
        'main_connect_list': main_connect_list,
        'system_access_user': req.session.get('system_access_user'),
        'access_time_remaining': max(0, int(remaining_time))  # 음수 방지
    })

def _get_current_ip():
    """현재 서버 IP 주소 조회"""
    try:
        out = subprocess.run(['hostname', '-I'], capture_output=True, text=True).stdout.strip()
        return out.split()[0] if out else ''
    except Exception:
        return ''

def _check_ip_permission():
    """IP 변경 권한 설정 여부 확인 (sudoers 파일 존재 확인)"""
    return os.path.exists('/etc/sudoers.d/matrix_ip_change')

@never_cache
@login_required(login_url='login_auth')
def on_device(req):
    """온디바이스 관리 메인 페이지 - 비밀번호 인증 추가"""
    # 게이트 통과 확인
    if not _has_system_access(req):
        return redirect(f"/api/system_password/?next=/api/system_template/on_device/")

    # 세션 시간을 리셋(10분 재충전)
    req.session['system_access_time'] = time.time()
    req.session.modified = True

    # 사용자별 장비 이름 가져오기
    device_names = {}
    try:
        from .models import DeviceNameConfig
        config = DeviceNameConfig.objects.filter(user=req.user)
        for item in config:
            device_names[item.device_type] = item.device_name
    except:
        pass

    # 기본값 설정
    if 'hardware' not in device_names:
        device_names['hardware'] = 'Matrix'
    if 'server' not in device_names:
        device_names['server'] = 'Server'

    context = {
        'current_ip': _get_current_ip(),
        'ip_change_configured': _check_ip_permission(),
        'device_names': device_names,
    }
    return render(req, 'system_template/on_device.html', context)

@login_required(login_url='login_auth')
def setup_ip_permission(request):
    """IP 변경 권한 설정 페이지 - 비밀번호 인증 추가"""

    if request.method == 'GET':
        # 시스템 접근 권한 확인
        if not _has_system_access(request):
            return redirect(f"/api/system_password/?next=/api/setup_ip_permission/")

        current_user = subprocess.run(['whoami'], capture_output=True, text=True).stdout.strip() or os.getenv('USER', 'www-data')
        context = {
            'sudo_user': current_user,
            'already_configured': os.path.exists('/etc/sudoers.d/matrix_ip_change'),
        }

        return render(request, 'system_template/setup_permission.html', context)

    # POST 요청 처리 (권한 설정)
    password = request.POST.get('password')
    try:
        current_user = subprocess.run(['whoami'], capture_output=True, text=True).stdout.strip() or os.getenv('USER', 'www-data')
        safe_setup_script = f"""#!/bin/bash
TEMP_FILE=$(mktemp)
cat > $TEMP_FILE << 'EOF'
# Matrix Web IP 변경 권한
{current_user} ALL=(ALL) NOPASSWD: /usr/sbin/ip addr flush dev eth0
{current_user} ALL=(ALL) NOPASSWD: /usr/bin/cp /etc/dhcpcd.conf /etc/dhcpcd.conf.bak
{current_user} ALL=(ALL) NOPASSWD: /bin/mv /tmp/dhcpcd_new.conf /etc/dhcpcd.conf
{current_user} ALL=(ALL) NOPASSWD: /bin/systemctl restart dhcpcd
{current_user} ALL=(ALL) NOPASSWD: /usr/sbin/ip -f inet addr show eth0
{current_user} ALL=(ALL) NOPASSWD: /usr/sbin/ip addr flush dev eth0
{current_user} ALL=(ALL) NOPASSWD: /bin/rm -f /etc/sudoers.d/matrix_ip_change
{current_user} ALL=(ALL) NOPASSWD: /usr/bin/cat /etc/sudoers.d/matrix_ip_change
EOF
if visudo -c -f $TEMP_FILE; then
    cp $TEMP_FILE /etc/sudoers.d/matrix_ip_change
    chmod 440 /etc/sudoers.d/matrix_ip_change
    echo "SUCCESS"
else
    echo "SYNTAX_ERROR"
fi
rm -f $TEMP_FILE
"""
        with open('/tmp/safe_setup.sh', 'w') as f:
            f.write(safe_setup_script)
        os.chmod('/tmp/safe_setup.sh', 0o755)

        subprocess.run(['sudo', '-K'])  # sudo 캐시 초기화
        result = subprocess.run(
            f'echo "{password}" | sudo -S bash /tmp/safe_setup.sh',
            shell=True, capture_output=True, text=True
        )
        if "Sorry, try again" in result.stderr or "incorrect password" in result.stderr.lower():
            messages.error(request, '❌ 비밀번호가 틀렸습니다. 다시 확인해주세요.')
            return redirect('setup_ip_permission')  # 설정 페이지로 다시
        elif "SUCCESS" in result.stdout:
            messages.success(request, '✅ 권한 설정 완료!')
            return redirect('on_device')  # 통합 페이지로
        elif "SYNTAX_ERROR" in result.stdout:
            messages.error(request, '❌ Sudoers 문법 오류 - 설정 실패')
        elif result.returncode != 0:
            if "is not in the sudoers file" in result.stderr:
                messages.error(request, f'❌ 사용자 {current_user}는 sudo 권한이 없습니다.')
            else:
                messages.error(request, f'❌ 설정 실패: {result.stderr}')
    except Exception as e:
        messages.error(request, f'❌ 오류 발생: {str(e)}')

    return redirect('setup_ip_permission')  # 실패 시 설정 페이지로


@login_required(login_url='login_auth')
@require_POST
def remove_ip_permission(request):
    """IP 변경 권한 제거"""
    try:
        result = subprocess.run(
            ['sudo', 'rm', '-f', '/etc/sudoers.d/matrix_ip_change'],
            capture_output=True,
            text=True
        )

        # 0.5초 대기 후 파일 존재 확인
        time.sleep(0.5)
        check_result = subprocess.run(
            ['sudo', 'test', '-f', '/etc/sudoers.d/matrix_ip_change'],
            capture_output=True
        )

        if check_result.returncode != 0:
            # 파일이 존재하지 않으면 삭제 성공
            messages.success(request, '✅ 권한 설정이 제거되었습니다.')
        else:
            messages.error(request, '❌ 권한 제거 실패. SSH에서 확인이 필요합니다.')

        subprocess.run(['sudo', '-K'])

    except Exception as e:
        messages.error(request, f'❌ 제거 실패: {str(e)}')

    return redirect('on_device')

@login_required(login_url='login_auth')
def get_device_names(request):
    """현재 사용자의 장비 이름 설정 조회"""
    try:
        from .models import DeviceNameConfig
        config = DeviceNameConfig.objects.filter(user=request.user)
        names = {}
        for item in config:
            names[item.device_type] = item.device_name

        # 기본값 설정
        if 'hardware' not in names:
            names['hardware'] = 'Matrix'
        if 'server' not in names:
            names['server'] = 'Server'

        return JsonResponse({
            'success': True,
            'names': names
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='login_auth')
@require_POST
def update_device_name(request):
    """장비 이름 업데이트"""
    try:
        data = json.loads(request.body)
        device_type = data.get('device_type')
        device_name = data.get('device_name', '').strip()

        if device_type not in ['hardware', 'server']:
            return JsonResponse({
                'success': False,
                'error': '잘못된 장비 타입입니다.'
            }, status=400)

        if len(device_name) > 200:
            return JsonResponse({
                'success': False,
                'error': '장비 이름은 200자를 초과할 수 없습니다.'
            }, status=400)

        # 기본값 설정
        if not device_name:
            device_name = 'Matrix' if device_type == 'hardware' else 'Server'

        from .models import DeviceNameConfig
        config, created = DeviceNameConfig.objects.get_or_create(
            user=request.user,
            device_type=device_type,
            defaults={'device_name': device_name}
        )

        if not created:
            config.device_name = device_name
            config.save()

        # 세션 시간 연장
        if request.session.get('system_access'):
            request.session['system_access_time'] = time.time()

        return JsonResponse({
            'success': True,
            'message': '장비 이름이 업데이트되었습니다.',
            'device_name': device_name
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '잘못된 JSON 형식입니다.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
@login_required(login_url='login_auth')
def profile_order(request):
    """프로필 순서 저장/조회 API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_list = data.get('order', [])

            # 각 프로필의 순서 업데이트
            for index, profile_id in enumerate(order_list):
                Profile.objects.filter(id=profile_id).update(order=index)

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    elif request.method == 'GET':
        try:
            profiles = Profile.objects.all().order_by('order', 'id')
            order_list = [p.id for p in profiles]
            return JsonResponse({'order': order_list})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required(login_url='login_auth')
def check_hardware_connection(request):
    """
    하드웨어 연결 상태를 확인하는 API
    """
    matrix_id = request.GET.get('id')

    if not matrix_id:
        return JsonResponse({
            'success': False,
            'error': 'Matrix ID가 필요합니다.'
        }, status=400)

    try:
        mat = Mat.objects.get(id=matrix_id)

        # Matrix 연결 테스트
        matrix_status = {
            'connected': False,
            'ip': mat.matrix_ip_address,
            'port': mat.port
        }

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((mat.matrix_ip_address, mat.port))
            sock.close()
            matrix_status['connected'] = (result == 0)
        except:
            matrix_status['connected'] = False

        # KVM 연결 테스트
        kvm_status = {
            'connected': False,
            'ip': mat.kvm_ip_address,
            'port': mat.port
        }

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((mat.kvm_ip_address, mat.port))
            sock.close()
            kvm_status['connected'] = (result == 0)
        except:
            kvm_status['connected'] = False

        return JsonResponse({
            'success': True,
            'matrix': matrix_status,
            'kvm': kvm_status,
            'name': mat.name
        })

    except Mat.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Matrix를 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)