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
delay_time = 0.7

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


def kvm_command_handle(input):
    """
        kvm command 변환
    """
    command = ''
    
    if type(input) is str:
        input = int(input)

    if input==1:
        command = '55 AA 04 09 01 0E EE'
    elif input==2:
        command = '55 AA 04 09 02 0E EE'
    elif input==3:
        command = '55 AA 04 09 03 0E EE'
    elif input==4:
        command = '55 AA 04 09 04 0E EE'
    elif input==5:
        command = '55 AA 04 09 05 0E EE'
    elif input==6:
        command = '55 AA 04 09 06 0E EE'
    elif input==7:
        command = '55 AA 04 09 07 0E EE'
    elif input==8:
        command = '55 AA 04 09 08 0E EE'
    elif input==9:
        command = '55 AA 04 09 09 0E EE'
    elif input==10:
        command = '55 AA 04 09 10 0E EE'
    elif input==11:
        command = '55 AA 04 09 11 0E EE'
    elif input==12:
        command = '55 AA 04 09 12 0E EE'
    elif input==13:
        command = '55 AA 04 09 13 0E EE'
    elif input==14:
        command = '55 AA 04 09 14 0E EE'
    elif input==15:
        command = '55 AA 04 09 15 0E EE'
    elif input==16:
        command = '55 AA 04 09 16 0E EE'
    elif input==17:
        command = '55 AA 04 09 17 0E EE'
    elif input==18:
        command = '55 AA 04 09 18 0E EE'
    elif input==19:
        command = '55 AA 04 09 19 0E EE'
    elif input==20:
        command = '55 AA 04 09 20 0E EE'
    elif input==21:
        command = '55 AA 04 09 21 0E EE'
    elif input==22:
        command = '55 AA 04 09 22 0E EE'
    elif input==23:
        command = '55 AA 04 09 23 0E EE'
    elif input==24:
        command = '55 AA 04 09 24 0E EE'
    elif input==25:
        command = '55 AA 04 09 25 0E EE'
    elif input==26:
        command = '55 AA 04 09 26 0E EE'
    elif input==27:
        command = '55 AA 04 09 27 0E EE'
    elif input==28:
        command = '55 AA 04 09 28 0E EE'
    elif input==29:
        command = '55 AA 04 09 29 0E EE'
    elif input==30:
        command = '55 AA 04 09 30 27 EE'
    elif input==31:
        command = '55 AA 04 09 31 28 EE'
    elif input==32:
        command = '55 AA 04 09 32 29 EE'
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
            command = '55 AA 04 08 00 0C EE'
        elif target == 2:
            command = '55 AA 04 08 10 2F EE'
        elif target == 3:
            command = '55 AA 04 08 20 2F EE'
        elif target == 4:
            command = '55 AA 04 08 30 2F EE'
        elif target == 5:
            command = '55 AA 04 08 40 2F EE'
        elif target == 6:
            command = '55 AA 04 08 50 2F EE'
        elif target == 7:
            command = '55 AA 04 08 60 2F EE'
        elif target == 8:
            command = '55 AA 04 08 70 2F EE'
    if input==2:
        if target == 1:
            command = '55 AA 04 08 01 2F EE'
        elif target == 2:
            command = '55 AA 04 08 11 2F EE'
        elif target == 3:
            command = '55 AA 04 08 21 2F EE'
        elif target == 4:
            command = '55 AA 04 08 31 2F EE'
        elif target == 5:
            command = '55 AA 04 08 41 2F EE'
        elif target == 6:
            command = '55 AA 04 08 51 2F EE'
        elif target == 7:
            command = '55 AA 04 08 61 2F EE'
        elif target == 8:
            command = '55 AA 04 08 71 2F EE'
    if input==3:
        if target == 1:
            command = '55 AA 04 08 02 2F EE'
        elif target == 2:
            command = '55 AA 04 08 12 2F EE'
        elif target == 3:
            command = '55 AA 04 08 22 2F EE'
        elif target == 4:
            command = '55 AA 04 08 32 2F EE'
        elif target == 5:
            command = '55 AA 04 08 42 2F EE'
        elif target == 6:
            command = '55 AA 04 08 52 2F EE'
        elif target == 7:
            command = '55 AA 04 08 62 2F EE'
        elif target == 8:
            command = '55 AA 04 08 72 2F EE'
    if input==4:
        if target == 1:
            command = '55 AA 04 08 03 2F EE'
        elif target == 2:
            command = '55 AA 04 08 13 2F EE'
        elif target == 3:
            command = '55 AA 04 08 23 2F EE'
        elif target == 4:
            command = '55 AA 04 08 33 2F EE'
        elif target == 5:
            command = '55 AA 04 08 43 2F EE'
        elif target == 6:
            command = '55 AA 04 08 53 2F EE'
        elif target == 7:
            command = '55 AA 04 08 63 2F EE'
        elif target == 8:
            command = '55 AA 04 08 73 2F EE'
    if input==5:
        if target == 1:
            command = '55 AA 04 08 04 2F EE'
        elif target == 2:
            command = '55 AA 04 08 14 2F EE'
        elif target == 3:
            command = '55 AA 04 08 24 2F EE'
        elif target == 4:
            command = '55 AA 04 08 34 2F EE'
        elif target == 5:
            command = '55 AA 04 08 44 2F EE'
        elif target == 6:
            command = '55 AA 04 08 54 2F EE'
        elif target == 7:
            command = '55 AA 04 08 64 2F EE'
        elif target == 8:
            command = '55 AA 04 08 74 2F EE'
    if input==6:
        if target == 1:
            command = '55 AA 04 08 05 2F EE'
        elif target == 2:
            command = '55 AA 04 08 15 2F EE'
        elif target == 3:
            command = '55 AA 04 08 25 2F EE'
        elif target == 4:
            command = '55 AA 04 08 35 2F EE'
        elif target == 5:
            command = '55 AA 04 08 45 2F EE'
        elif target == 6:
            command = '55 AA 04 08 55 2F EE'
        elif target == 7:
            command = '55 AA 04 08 65 2F EE'
        elif target == 8:
            command = '55 AA 04 08 75 2F EE'
    if input==7:
        if target == 1:
            command = '55 AA 04 08 06 2F EE'
        elif target == 2:
            command = '55 AA 04 08 16 2F EE'
        elif target == 3:
            command = '55 AA 04 08 26 2F EE'
        elif target == 4:
            command = '55 AA 04 08 36 2F EE'
        elif target == 5:
            command = '55 AA 04 08 46 2F EE'
        elif target == 6:
            command = '55 AA 04 08 56 2F EE'
        elif target == 7:
            command = '55 AA 04 08 66 2F EE'
        elif target == 8:
            command = '55 AA 04 08 76 2F EE'
    if input==8:
        if target == 1:
            command = '55 AA 04 08 07 2F EE'
        elif target == 2:
            command = '55 AA 04 08 17 2F EE'
        elif target == 3:
            command = '55 AA 04 08 27 2F EE'
        elif target == 4:
            command = '55 AA 04 08 37 2F EE'
        elif target == 5:
            command = '55 AA 04 08 47 2F EE'
        elif target == 6:
            command = '55 AA 04 08 57 2F EE'
        elif target == 7:
            command = '55 AA 04 08 67 2F EE'
        elif target == 8:
            command = '55 AA 04 08 77 2F EE'
    print("command:"+command)
    return binascii.unhexlify(command.replace(' ',''))


def matrix_all_command_handle(input):
    """
        matrix commnad 변환(all)
    """
    command = ''
    
    input = int(input)
    if input == 1:
        command = '55 AA 07 04 11 11 11 11 4F EE'
    elif input == 2:
        command = '55 AA 07 04 22 22 22 22 93 EE'
    elif input == 3:
        command = '55 AA 07 04 33 33 33 33 D7 EE'
    elif input == 4:
        command = '55 AA 07 04 44 44 44 44 1B EE'
    elif input == 5:
        command = '55 AA 07 04 55 55 55 55 5F EE'
    elif input == 6:
        command = '55 AA 07 04 66 66 66 66 A3 EE'
    elif input == 7:
        command = '55 AA 07 04 77 77 77 77 E7 EE'
    elif input == 8:
        command = '55 AA 07 04 88 88 88 88 2B EE'
    
    return bytes.fromhex(command)


def matrix_n_to_n_command_handle():
    """
        matrix commnad 변환(n to n)
    """
    command = '55 AA 07 04 12 34 56 78 1F EE'

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

            input_list = [i.input_a, i.input_b, i.input_c, i.input_d, i.input_e, i.input_f, i.input_g, i.input_h, i.input_i, i.input_j, i.input_k, i.input_l, i.input_m, i.input_n, i.input_o, i.input_p]
            counter_list = Counter(input_list)
            keys = counter_list.keys()
            for key in keys:
                if key != "00" and int(counter_list[key]) > 3:
                    is_all = int(key)
                    command = matrix_all_command_handle(key)
                    client_socket.sendall(command)
                    time.sleep(delay_time)  
                    break
            
            # n to n 확인
            for j in range(8):
                if int(input_list[j]) == j+1:
                    check_n_to_n += 1                    
                
            # 같은 input값이 4개 이상 있을 경우에 matrix_all_command 함수을 통해 모든 input값을 일괄 변경 후에 입력
            if is_all:
                for j in range(8):
                    if int(input_list[j]) != 0 and int(input_list[j]) != is_all:
                        command = matrix_command_handle(input_list[j], j+1)
                        client_socket.sendall(command)
                        time.sleep(delay_time)

            # 입력값과 출력이 4개 이상 일치할 경우 n to n command 입력 후에 변경
            elif check_n_to_n >= 4: 
                command = matrix_n_to_n_command_handle()
                client_socket.sendall(command)
                time.sleep(delay_time)
                for j in range(8):
                    if int(input_list[j]) != 0 and int(input_list[j]) != j+1:
                        command = matrix_command_handle(input_list[j], j+1)
                        client_socket.sendall(command)
                        time.sleep(delay_time)

            else: 
                for j in range(8):
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
        mat_input_list = ['input_a','input_b','input_c','input_d','input_e','input_f','input_g','input_h','input_i','input_j','input_k','input_l','input_m','input_n','input_o','input_p', 'input_kvm',]
        
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
                mat_input_list = ['input_a','input_b','input_c','input_d','input_e','input_f','input_g','input_h','input_i','input_j','input_k','input_l','input_m','input_n','input_o','input_p', 'input_kvm',]
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