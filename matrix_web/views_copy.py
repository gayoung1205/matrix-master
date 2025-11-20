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

delay_time = 0.23

@login_required(login_url='login_auth')
def home(req):
    """ 
        Home 페이지
    """
    print("views_home")
    permission = req.user.userpermission.permission

    # 학생 사용자일 경우 해당 Group만 사용하게끔 분리
    if permission > 2:
        matrix = Mat.objects.filter(is_main=False).filter(main_connect=(permission-2))
        context = {'matrix': matrix, 'permission': permission}
        print("views_home")
        return render(req, 'group_homepage.html', context)
    else:
        matrix = Mat.objects.filter(is_main=False).order_by("main_connect")
        main = Mat.objects.filter(is_main=True)
        profile = Profile.objects.all().order_by("id")
        connect = ['입력01', '입력02', '입력03', '입력04']
        print("views_home")
        for i in range(len(matrix)):
            matrix[i].count = i+1
            connect[i] = matrix[i].name
            
        context = {'matrix': matrix, 'profile': profile, 'main': main, 'connect_list': connect, 'permission': permission}
        return render(req, 'home/home.html', context)


def kvm_command_handle(input):
    """
        kvm command 변환
    """
    command = ''
    
    if type(input) is str:
        input = int(input)

    if input==1:
        command = '55 AA 04 05 01 0A EE'
    elif input==2:
        command = '55 AA 04 05 02 0B EE'
    elif input==3:
        command = '55 AA 04 05 03 0C EE'
    elif input==4:
        command = '55 AA 04 05 04 0D EE'
    elif input==5:
        command = '55 AA 04 05 05 0E EE'
    elif input==6:
        command = '55 AA 04 05 06 0F EE'
    elif input==7:
        command = '55 AA 04 05 07 10 EE'
    elif input==8:
        command = '55 AA 04 05 08 11 EE'
    elif input==9:
        command = '55 AA 04 05 09 12 EE'
    elif input==10:
        command = '55 AA 04 05 0A 13 EE'
    elif input==11:
        command = '55 AA 04 05 0B 14 EE'
    elif input==12:
        command = '55 AA 04 05 0C 15 EE'
    elif input==13:
        command = '55 AA 04 05 0D 16 EE'
    elif input==14:
        command = '55 AA 04 05 0E 17 EE'
    elif input==15:
        command = '55 AA 04 05 0F 18 EE'
    elif input==16:
        command = '55 AA 04 05 10 19 EE'
    elif input==17:
        command = '55 AA 04 05 11 1A EE'
    elif input==18:
        command = '55 AA 04 05 12 1B EE'
    elif input==19:
        command = '55 AA 04 05 13 1C EE'
    elif input==20:
        command = '55 AA 04 05 14 1D EE'
    elif input==21:
        command = '55 AA 04 05 15 1E EE'
    elif input==22:
        command = '55 AA 04 05 16 1F EE'
    elif input==23:
        command = '55 AA 04 05 17 20 EE'
    elif input==24:
        command = '55 AA 04 05 18 21 EE'
    elif input==25:
        command = '55 AA 04 05 19 22 EE'
    elif input==26:
        command = '55 AA 04 05 1A 23 EE'
    elif input==27:
        command = '55 AA 04 05 1B 24 EE'
    elif input==28:
        command = '55 AA 04 05 1C 25 EE'
    elif input==29:
        command = '55 AA 04 05 1D 26 EE'
    elif input==30:
        command = '55 AA 04 05 1E 27 EE'
    elif input==31:
        command = '55 AA 04 05 1F 28 EE'
    elif input==32:
        command = '55 AA 04 05 20 29 EE'
    
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
            command = '55 AA 07 04 10 00 00 00 1B EE'
        elif target == 2:
            command = '55 AA 07 04 01 00 00 00 0C EE'
        elif target == 3:
            command = '55 AA 07 04 00 10 00 00 1B EE'
        elif target == 4:
            command = '55 AA 07 04 00 01 00 00 0C EE'
        elif target == 5:
            command = '55 AA 07 04 00 00 10 00 1B EE'
        elif target == 6:
            command = '55 AA 07 04 00 00 01 00 0C EE'
        elif target == 7:
            command = '55 AA 07 04 00 00 00 10 1B EE'
        elif target == 8:
            command = '55 AA 07 04 00 00 00 01 0C EE'
    if input==2:
        if target == 1:
            command = '55 AA 07 04 20 00 00 00 2B EE'
        elif target == 2:
            command = '55 AA 07 04 02 00 00 00 0D EE'
        elif target == 3:
            command = '55 AA 07 04 00 20 00 00 2B EE'
        elif target == 4:
            command = '55 AA 07 04 00 02 00 00 0D EE'
        elif target == 5:
            command = '55 AA 07 04 00 00 20 00 2B EE'
        elif target == 6:
            command = '55 AA 07 04 00 00 02 00 0D EE'
        elif target == 7:
            command = '55 AA 07 04 00 00 00 20 2B EE'
        elif target == 8:
            command = '55 AA 07 04 00 00 00 02 0D EE'
    if input==3:
        if target == 1:
            command = '55 AA 07 04 30 00 00 00 3B EE'
        elif target == 2:
            command = '55 AA 07 04 03 00 00 00 0E EE'
        elif target == 3:
            command = '55 AA 07 04 00 30 00 00 3B EE'
        elif target == 4:
            command = '55 AA 07 04 00 03 00 00 0E EE'
        elif target == 5:
            command = '55 AA 07 04 00 00 30 00 3B EE'
        elif target == 6:
            command = '55 AA 07 04 00 00 03 00 0E EE'
        elif target == 7:
            command = '55 AA 07 04 00 00 00 30 3B EE'
        elif target == 8:
            command = '55 AA 07 04 00 00 00 03 0E EE'
    if input==4:
        if target == 1:
            command = '55 AA 07 04 40 00 00 00 4B EE'
        elif target == 2:
            command = '55 AA 07 04 04 00 00 00 0F EE'
        elif target == 3:
            command = '55 AA 07 04 00 40 00 00 4B EE'
        elif target == 4:
            command = '55 AA 07 04 00 04 00 00 0F EE'
        elif target == 5:
            command = '55 AA 07 04 00 00 40 00 4B EE'
        elif target == 6:
            command = '55 AA 07 04 00 00 04 00 0F EE'
        elif target == 7:
            command = '55 AA 07 04 00 00 00 40 4B EE'
        elif target == 8:
            command = '55 AA 07 04 00 00 00 04 0F EE'
    if input==5:
        if target == 1:
            command = '55 AA 07 04 50 00 00 00 5B EE'
        elif target == 2:
            command = '55 AA 07 04 05 00 00 00 10 EE'
        elif target == 3:
            command = '55 AA 07 04 00 50 00 00 5B EE'
        elif target == 4:
            command = '55 AA 07 04 00 05 00 00 10 EE'
        elif target == 5:
            command = '55 AA 07 04 00 00 50 00 5B EE'
        elif target == 6:
            command = '55 AA 07 04 00 00 05 00 10 EE'
        elif target == 7:
            command = '55 AA 07 04 00 00 00 50 5B EE'
        elif target == 8:
            command = '55 AA 07 04 00 00 00 05 10 EE'
    if input==6:
        if target == 1:
            command = '55 AA 07 04 60 00 00 00 6B EE'
        elif target == 2:
            command = '55 AA 07 04 06 00 00 00 11 EE'
        elif target == 3:
            command = '55 AA 07 04 00 60 00 00 6B EE'
        elif target == 4:
            command = '55 AA 07 04 00 06 00 00 11 EE'
        elif target == 5:
            command = '55 AA 07 04 00 00 60 00 6B EE'
        elif target == 6:
            command = '55 AA 07 04 00 00 06 00 11 EE'
        elif target == 7:
            command = '55 AA 07 04 00 00 00 60 6B EE'
        elif target == 8:
            command = '55 AA 07 04 00 00 00 06 11 EE'
    if input==7:
        if target == 1:
            command = '55 AA 07 04 70 00 00 00 7B EE'
        elif target == 2:
            command = '55 AA 07 04 07 00 00 00 12 EE'
        elif target == 3:
            command = '55 AA 07 04 00 70 00 00 7B EE'
        elif target == 4:
            command = '55 AA 07 04 00 07 00 00 12 EE'
        elif target == 5:
            command = '55 AA 07 04 00 00 70 00 7B EE'
        elif target == 6:
            command = '55 AA 07 04 00 00 07 00 12 EE'
        elif target == 7:
            command = '55 AA 07 04 00 00 00 70 7B EE'
        elif target == 8:
            command = '55 AA 07 04 00 00 00 07 12 EE'
    if input==8:
        if target == 1:
            command = '55 AA 07 04 80 00 00 00 8B EE'
        elif target == 2:
            command = '55 AA 07 04 08 00 00 00 13 EE'
        elif target == 3:
            command = '55 AA 07 04 00 80 00 00 8B EE'
        elif target == 4:
            command = '55 AA 07 04 00 08 00 00 13 EE'
        elif target == 5:
            command = '55 AA 07 04 00 00 80 00 8B EE'
        elif target == 6:
            command = '55 AA 07 04 00 00 08 00 13 EE'
        elif target == 7:
            command = '55 AA 07 04 00 00 00 80 8B EE'
        elif target == 8:
            command = '55 AA 07 04 00 00 00 08 13 EE'
    
    return bytes.fromhex(command)


@login_required(login_url='login_auth')
def control(req):
    """
        matrix 1:1 control api
        id : matrix id
        input : 변하는 값
        target : target column
    """
    id = req.GET.get("id", None)
    input = req.GET.get("input", None)
    target = req.GET.get("target", None)
    
    try:
        mat = Mat.objects.get(id=id)
    except Exception as e:
        print(e)
        return HttpResponseServerError('시스템을 찾을 수 없습니다')

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((mat.matrix_ip_address, mat.port))
        command = matrix_command_handle(input, target)
        client_socket.sendall(command)
        time.sleep(delay_time)
        
        client_socket.close()
        
        list = ['input_a','input_b','input_c','input_d','input_e','input_f','input_g','input_h']
        setattr(mat, list[int(target)-1], input)
        mat.save()
    except TimeoutError:
        return HttpResponseServerError('시스템과의 연결이 실패했습니다. 연결을 확인해주세요.')
    except Exception as e:
        print(e)
        return HttpResponseServerError('시스템 수정 오류')

    return redirect('home')


def kvm_socket(ip, port, input):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    command = kvm_command_handle(input)
    client_socket.sendall(command)
    time.sleep(delay_time)
    client_socket.close()

@login_required(login_url='login_auth')
def kvm(req):
    """
        kvm control
        id : kvm id
        input : 원하는 kvm 값
    """
    id = req.GET.get("id", None)
    input = req.GET.get("input", None)
    
    if isinstance(input, str) and len(input) < 2:
        input = "0"+input

    try:
        kvm = Mat.objects.get(id=id)
        if not kvm.is_main:
            main = Mat.objects.get(is_main=True)
    except Exception as e:
        print(e)

    try:
        kvm_socket(kvm.kvm_ip_address, kvm.port, input)
        time.sleep(delay_time)
        # if kvm.is_main:
        #     kvm_socket(kvm.kvm_ip_address, kvm.port, input)
        # else:
        #     if int(input) < 6:
        #         kvm_socket(kvm.kvm_ip_address, kvm.port, input)
        #         time.sleep(delay_time)
        #         if kvm.main_connect < 4:
        #             kvm_socket(main.kvm_ip_address, main.port, int(input)+(kvm.main_connect-1)*5)
        #             time.sleep(delay_time)
        #             kvm_socket(main.kvm_ip_address2, main.port, "08")
        #         else:
        #             kvm_socket(main.kvm_ip_address2, main.port, input)
        #             time.sleep(delay_time)
        #             kvm_socket(main.kvm_ip_address, main.port, "16")
        #     else:
        #         kvm_socket(kvm.kvm_ip_address, kvm.port, input)
        #         time.sleep(delay_time)
    except TimeoutError:
        return HttpResponseServerError('시스템과의 연결이 실패했습니다. 연결을 확인해주세요.')
    except Exception as e:
        print(e)

    return redirect('home')


def send_msg(client_socket, msg):
    msg = msg.encode()
    client_socket.sendall(msg)
    client_socket.recv(1024)
    # while total_sent < msg_len:
    #     sent = client_socket.sendall(msg[total_sent:])
    #     print(sent)
    #     client_socket.recv(1024)
    #     # print(client_socket.recv(1024))
    #     if sent == 0:
    #         raise RuntimeError("socket connection broken")
    #     total_sent = total_sent + sent


@login_required(login_url='login_auth')
def profile_control(req):
    profile_id = req.GET.get("id", None)
    try:
        profile = Profile.objects.get(id=profile_id)
        mat_set = MatrixSetting.objects.filter(profile=profile)
        mat_set_serializer = MatrixSettingSerializer(mat_set, many=True).data
    except Exception as e:
        print(e)
    
    # if profile.name == 'infinity loop':
        # ip = mat_set[0].matrix.matrix_ip_address
        # ip = "192.168.1.4"
        # port = mat_set[0].matrix.port
        # print(ip, port)
        # try:
            # while True:
                # input_list = ["01", "02", "03", "04", "05", "06", "07", "08"]
                # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # client_socket.connect((ip, port))       

                # for j in range(8):
                    # if int(input_list[j]) != 0:
                        # command = matrix_command_handle(input_list[j], j+1)
                        # client_socket.sendall(command)
                        # now = datetime.now()
                        # print(f"time : {now.year}/{now.month}/{now.day} {now.hour}:{now.minute}:{now.second}, input : {input_list[j]}, target : 0{j+1}")
                        # time.sleep(delay_time)
                # client_socket.close()
        
                # kvm_socket(ip, port, "01")
                # now = datetime.now()
                # print(f"time : {now.year}/{now.month}/{now.day} {now.hour}:{now.minute}:{now.second}, kvm : 01")
                
                # input_list = ["05", "06", "07", "08", "01", "02", "03", "04"]
                # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # client_socket.connect((ip, port))       
    
                # for j in range(8):
                    # if int(input_list[j]) != 0:
                        # command = matrix_command_handle(input_list[j], j+1)
                        # client_socket.sendall(command)
                        # now = datetime.now()
                        # print(f"time : {now.year}/{now.month}/{now.day} {now.hour}:{now.minute}:{now.second}, input : {input_list[j]}, target : 0{j+1}")
                        # time.sleep(delay_time)
                # client_socket.close()
        
                # kvm_socket(ip, port, "05")
                # now = datetime.now()
                # print(f"time : {now.year}/{now.month}/{now.day} {now.hour}:{now.minute}:{now.second}, kvm : 06")
        # except Exception as e:
            # print(e)
        # return redirect('home')
    
    try:
        for i in mat_set:
            input_list = [i.input_a, i.input_b, i.input_c, i.input_d, i.input_e, i.input_f, i.input_g, i.input_h]
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((i.matrix.matrix_ip_address, i.matrix.port))          

            for j in range(8):
                if int(input_list[j]) != 0:
                    command = matrix_command_handle(input_list[j], j+1)
                    client_socket.sendall(command)
                    time.sleep(delay_time)
            client_socket.close()
            
            if int(i.input_kvm) != 0:
                kvm_socket(i.matrix.kvm_ip_address, i.matrix.port, i.input_kvm)
                # if i.matrix.is_main:
                #     if int(i.input_kvm)<16:
                #         kvm_socket(i.matrix.kvm_ip_address, i.matrix.port, i.input_kvm)
                #         # time.sleep(0.3)
                #         kvm_socket(i.matrix.kvm_ip_address2, i.matrix.port, "08")
                #         # time.sleep(0.3)
                #     else:
                #         kvm_socket(i.matrix.kvm_ip_address2, i.matrix.port, int(i.input_kvm)-15)
                #         # time.sleep(0.3)
                #         kvm_socket(i.matrix.kvm_ip_address, i.matrix.port, "16")
                #         # time.sleep(0.3)
                # else:
                #     kvm_socket(i.matrix.kvm_ip_address, i.matrix.port, i.input_kvm)
                #     # time.sleep(0.3)
    except TimeoutError:
        return HttpResponseServerError('장치와의 연결이 실패했습니다. 연결을 확인해주세요.')
    except Exception as e:
        print(e)

    try:
        for i in mat_set_serializer:
            matrix = Mat.objects.get(id=i["matrix"])
            mat_input_list = ['input_a','input_b','input_c','input_d','input_e','input_f','input_g','input_h',]
            for mat_input in mat_input_list:
                setattr(matrix, mat_input, i[mat_input])
            matrix.save()
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
        
        profile = Profile.objects.create(name=data["name"])
        profile.save()
        mat_id_list = data["mat_id_list"].split(',')
        mat_input_list = ['input_a','input_b','input_c','input_d','input_e','input_f','input_g','input_h', 'input_kvm',]
        
        for i in range(len(mat_id_list)):
            mat = Mat.objects.get(id=mat_id_list[i])
            mat_set = MatrixSetting.objects.create(profile=profile, matrix=mat)
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
        """
            Profile 수정, 삭제 api
            data["_method"] == 'delete' -> 삭제 api
            data["_method"] == 'put' -> 수정 api
        """
        data = req.data
        try:
            profile = Profile.objects.get(id=data['id'])
            if data["_method"] == 'delete':
                profile.delete()
            elif data["_method"] == 'put':
                setattr(profile, 'name', data["name"])
                profile.save()

                mat_id_list = data["mat_id_list"].split(',')
                mat_input_list = ['input_a','input_b','input_c','input_d','input_e','input_f','input_g','input_h', 'input_kvm',]
                for i in range(len(mat_id_list)):
                    mat = Mat.objects.get(id=mat_id_list[i])
                    mat_set = MatrixSetting.objects.get(profile=profile, matrix=mat)
                    for mat_input in mat_input_list:
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
                writer.writerow(["matrix_setting", set_ser["matrix_name"], set_ser["input_a"], set_ser["input_b"], set_ser["input_c"], set_ser["input_d"], set_ser["input_e"], set_ser["input_f"], set_ser["input_g"], set_ser["input_h"], set_ser["input_kvm"]])

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
                    input_list = ['input_a','input_b','input_c','input_d','input_e','input_f','input_g','input_h', 'input_kvm',]
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