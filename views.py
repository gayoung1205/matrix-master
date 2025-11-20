from tabnanny import check
from django.http.response import HttpResponseServerError
from django.shortcuts import render,  redirect
from django.http import HttpResponse
from rest_framework.views import APIView, Response
from .models import Matrix as Mat
from .models import Profile, MatrixSetting, License
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .serializers import MatrixSettingSerializer, MatrixSerializer, ProfileSerializer
import socket, time, csv
from utils.views import license_auth
from datetime import datetime
from collections import Counter
import binascii
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
delay_time = 0.5

@login_required(login_url='login_auth')
def home(req):
    """ 
        Home 페이지
    """
    permission = req.user.userpermission.permission
    print('viewhome')
    # 학생 사용자일 경우 해당 Group만 사용하게끔 분리
    if permission > 2:
        matrix = Mat.objects.filter(is_main=False).filter(main_connect=(permission-2))
        context = {'matrix': matrix, 'permission': permission}
        
        return render(req, 'group_homepage.html', context)
    else:        
        matrix = Mat.objects.filter(is_main=False).order_by("main_connect")
        main = Mat.objects.filter(is_main=True)
        profile = Profile.objects.all().order_by("id")
        connect = ['입력01', '입력02', '입력03', '입력04']

        for i in range(len(matrix)):
            matrix[i].count = i+1
            connect[i] = matrix[i].name

        context = {'matrix': matrix, 'profile': profile, 'main': main, 'connect_list': connect, 'permission': permission}
        return render(req, 'home/home.html', context)


def slicer_command_handle(input):
    command = ''
    if type(input) is str:
        input = int(input)
    if input == 1:
        command = '55 AA 04 0B 00 0F EE'
    elif input == 1:
        command = '55 AA 05 0F 05 10 29 EE'
    print(command)
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
    print(command)
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
def test(request):
    data = {'message':'hi this send for viewmassage'}
    return render(request, 'my_template.html', data)

@login_required(login_url='login_auth')
def control(req):
    print("control")
    """
        matrix 1:1 control api
        id : matrix id
        input : 변하는 값
        target : target column
    """
    id = req.GET.get("id", None)
    input = req.GET.get("input", None)
    target = req.GET.get("target", None)
    print("input:" + input)
    print("target:"+target)
    print(id)
    try:
        mat = Mat.objects.get(id=id)
    except Exception as e:
        print(e)
        return HttpResponseServerError('시스템을 찾을 수 없습니다')

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((mat.matrix_ip_address, mat.port))
        command = matrix_command_handle(input, target)
        md = Cs(CS_ARCH_X86, CS_MODE_32)
        for i in md.disasm(command, 0x1000):
            print("0x%x:\t%s\t%s" %(i.address, i.mnemonic, i.op_str))
            print(command)
        client_socket.sendall(command)
        time.sleep(delay_time)
        print("id:"+id)
        print(command)
        list = ['input_a','input_b','input_c','input_d','input_e','input_f','input_g','input_h','input_i','input_j','input_k','input_l','input_m','input_n','input_o','input_p']
        setattr(mat, list[int(target)-1], input)
        
        mat.save()
    except TimeoutError as e:
        print(e)
        return HttpResponseServerError('장치와의 연결이 실패했습니다. 연결을 확인해주세요.')
    except Exception as e:
        print(e)
        return HttpResponseServerError('시스템 수정 오류')
    finally:
        client_socket.close()
    return redirect('home')

@login_required(login_url='login_auth')
def slicer(req):
    print('slicer')
    print('slicer')
    id = req.GET.get("id", None)
    input = req.GET.get("input", None)
    try:
        print("try")
        print("--------------")
        mat = Mat.objects.get(id=id)
        # if not kvm.is_main:
        #     main = Mat.objects.get(is_main=True)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((mat.matrix_ip_address, mat.port))
        command = slicer_command_handle(input)
        print(command)
        md = Cs(CS_ARCH_X86, CS_MODE_32)
        for i in md.disasm(command, 0x1000):
            print("0x%x:\t%s\t%s" %(i.address, i.mnemonic, i.op_str))
            print(command)
        client_socket.sendall(command)
        time.sleep(delay_time)

        print("----------")
        print(command)
        print("----------")
        print("input:"+input)
        client_socket.sendall(command)
        time.sleep(delay_time)
        print(command)
        client_socket.close()

    except TimeoutError:
        return HttpResponseServerError('장치와의 연결이 실패했습니다. 연결을 확인해주세요.')
    except Exception as e:
        print(e)

    return redirect('home')
@login_required(login_url='login_auth')
def kvm(req):
    """
        kvm control
        id : kvm id
        input : 원하는 kvm 값
    """
    print('kvm')
    id = req.GET.get("id", None)
    input = req.GET.get("input", None)
    
    if isinstance(input, str) and len(input) < 2:
        input = "0"+input

    try:
        kvm = Mat.objects.get(id=id)
        # if not kvm.is_main:
        #     main = Mat.objects.get(is_main=True)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((kvm.kvm_ip_address, kvm.port))
        command = kvm_command_handle(input)
        print("----------")
        print(command)
        print("----------")
        print("input:"+input)
        client_socket.sendall(command)
        time.sleep(delay_time)
        print(command)
        client_socket.close()

    except TimeoutError:
        return HttpResponseServerError('장치와의 연결이 실패했습니다. 연결을 확인해주세요.')
    except Exception as e:
        print(e)

    return redirect('home')


def send_msg(client_socket, msg):
    msg = msg.encode()
    client_socket.sendall(msg)
    client_socket.recv(1024)


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
            print("profile")
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
                
            # 같은 input값이 4개 이상 있을 경우에 matrix_all_command 함수을 통해 모든 input값을 일괄 변경 후에 입력
            if is_all:
                for j in range(16):
                    print("all")
                    if int(input_list[j]) != 0 and int(input_list[j]) != is_all:
                        command = matrix_command_handle(input_list[j], j+1)
                        client_socket.sendall(command)
                        time.sleep(delay_time)

            # 입력값과 출력이 4개 이상 일치할 경우 n to n command 입력 후에 변경
            elif check_n_to_n >= 4:
                print("nton")
                command = matrix_n_to_n_command_handle()
                client_socket.sendall(command)
                time.sleep(delay_time)
                print(command)
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
                        print("frofilecommand")
                        print(command)
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
    """
        Login 페이지
    """
    return render(req, 'login/login.html', {})

@login_required(login_url='login_auth')
def system_template(req):
    """
        system_template 페이지
    """
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
class MatrixView(APIView):
    def post(self, req):
        """
            Matrix 생성 api
            name = Matrix 명(Char)
            matrix_ip_address = Matrix IP 주소 (GenericIPAddress)
            kvm_ip_address = Kvm IP 주소 (GenericIPAddress)
            port = Port 번호 (Integer)
            input_a, b, c, d, e, f, g, h = input 번호 (Char)
        """
        data = req.data
        matrix = Mat.objects.create()
        list = ['name', 'matrix_ip_address', 'kvm_ip_address', 'kvm_ip_address2', 'port', 'is_main', 'main_connect']
        for i in data:
            if i in list:
                setattr(matrix, i, data[i])
        matrix.save()
        
        return redirect('system_template')


@method_decorator(login_required, name='post')
class MatrixDetailView(APIView):
    def post(self, req):
        """
            Matrix 삭제 api
        """
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

@login_required(login_url='login_auth')
def profile_template(req):
    """
        profile_template 페이지
    """
    if req.user.userpermission.permission == 2:
        return redirect('home')

    sub_mat = Mat.objects.filter(is_main=False)
    sub_mat = sub_mat.order_by("main_connect")
    main_mat = Mat.objects.filter(is_main=True)
    profile = Profile.objects.all().order_by('id')

    connect = ['입력01', '입력02', '입력03', '입력04']
    for i in range(0, len(sub_mat)):
        connect[i] = sub_mat[i].name
   
    context = {'sub_mat': sub_mat, 'profile': profile, 'main_mat': main_mat, 'connect_list': connect}

    return render(req, 'profile_template/profile_template.html', context)

# ex) Input data = <QueryDict: {'mat_id_list': ['153,154,155,156,157'], 'input_a': ['01,01,01,01,01'], 'input_b': ['02,02,02,02,02'], 'input_c': ['03,03,03,03,03'], 'input_d': ['04,04,04,04,04'], 'input_e': ['05,05,05,05,05'], 'input_f': ['06,06,06,06,06'], 'input_g': ['01,07,07,07,07'], 'input_h': ['01,01,01,01,01'], 'input_kvm': ['01,01,01,01,01'], 'name': ['fgfg']}>
@method_decorator(login_required, name='post')
class ProfileView(APIView):
    def post(self, req):
        """
            Profile 생성 api
            name = Profile 명(Char)
            Profile 생성 후 MatrixSetting 생성
        """
        data = req.data
        print(data)
        profile = Profile.objects.create(name=data["name"])
        profile.save()
        mat_id_list = data["mat_id_list"].split(',')
        mat_input_list = ['input_a','input_b','input_c','input_d','input_e','input_f','input_g','input_h','input_i','input_j','input_k','input_l','input_m','input_n','input_o','input_p', 'input_kvm',]
        print(data)
        for i in range(len(mat_id_list)):
            print(1)
            mat = Mat.objects.get(id=mat_id_list[i])
            mat_set = MatrixSetting.objects.create(profile=profile, matrix=mat)
            for j in data:
                if j in mat_input_list:
                    print(data[j])
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
        """
            Profile 수정, 삭제 api
            data["_method"] == 'delete' -> 삭제 api
            data["_method"] == 'put' -> 수정 api
        """
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
        """
            Matrix 내보내기
        """
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
        """
            Matrix 불러오기
        """
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
        """
            Profile 내보내기
        """
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
        # return redirect('profile_template')


@method_decorator(login_required, name='post')
class ProfileImportView(APIView):
    def post(self, req):
        """
            Profile 불러오기
            profile.csv ->
                - column_a에 "profile", "matrix_setting". 
                - column_b에 "profile"일 경우 profile_name, "matrix_setting"일 경우 matrix_name
                - column_c ~ column_k -> input_a ~ input_h 
        """
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

@license_auth
def test(req):
    # os_type = sys.platform.lower()
    
    # if "windows" in os_type or "win" in os_type:
    #     command = "wmic baseboard get product, Manufacturer, version, serialnumber"
    #     text = os.popen(command).read().replace("\n","").replace("	","").replace(" ","").replace("ManufacturerProductSerialNumberVersion","")

    return HttpResponse("")    


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
