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
import threading

@login_required(login_url='login_auth')
def home(req):
    """ 
        Home 페이지
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
        profile = Profile.objects.all().order_by("id")
        connect = ['입력01', '입력02', '입력03', '입력04']

        for i in range(len(matrix)):
            matrix[i].count = i+1
            connect[i] = matrix[i].name
            
        context = {'matrix': matrix, 'profile': profile, 'main': main, 'connect_list': connect, 'permission': permission}
        return render(req, 'home.html', context)


class Worker(threading.Thread):
    def __init__(self, socket, msg):
        super().__init__()
        self.socket = socket           # thread 이름 지정
        self.msg = msg
    
    def run(self):
        send_msg(self.socket, self.msg)


def send_msg(client_socket, msg):
    print(msg)
    msg = msg.encode()
    client_socket.sendall(msg)
    print(client_socket.recv(2048))
    # while total_sent < msg_len:
    #     sent = client_socket.sendall(msg[total_sent:])
    #     print(sent)
    #     client_socket.recv(1024)
    #     # print(client_socket.recv(1024))
    #     if sent == 0:
    #         raise RuntimeError("socket connection broken")
    #     total_sent = total_sent + sent


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
        client_socket.sendall(f'MT00SW{input}{target}NT'.encode())
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


def kvm_command_handle(input):
    """
        kvm command 변환
    """
    command = b''
    
    if type(input) is str:
        input = int(input)

    if input==1:
        command= b'\xAA\xBB\x03\x01\x01\xEE'
    elif input==2:
        command = b'\xAA\xBB\x03\x01\x02\xEE'
    elif input==3:
        command = b'\xAA\xBB\x03\x01\x03\xEE'
    elif input==4:
        command = b'\xAA\xBB\x03\x01\x04\xEE'
    elif input==5:
        command = b'\xAA\xBB\x03\x01\x05\xEE'
    elif input==6:
        command = b'\xAA\xBB\x03\x01\x06\xEE'
    elif input==7:
        command = b'\xAA\xBB\x03\x01\x07\xEE'
    elif input==8:
        command = b'\xAA\xBB\x03\x01\x08\xEE'
    elif input==9:
        command = b'\xAA\xBB\x03\x01\x09\xEE'
    elif input==10:
        command = b'\xAA\xBB\x03\x01\x0A\xEE'
    elif input==11:
        command = b'\xAA\xBB\x03\x01\x0B\xEE'
    elif input==12:
        command = b'\xAA\xBB\x03\x01\x0C\xEE'
    elif input==13:
        command = b'\xAA\xBB\x03\x01\x0D\xEE'
    elif input==14:
        command = b'\xAA\xBB\x03\x01\x0E\xEE'
    elif input==15:
        command = b'\xAA\xBB\x03\x01\x0F\xEE'
    elif input==16:
        command = b'\xAA\xBB\x03\x01\x10\xEE'
    
    return command


def kvm_socket(ip, port, input):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    command = kvm_command_handle(input)
    client_socket.sendall(command)
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
        if kvm.is_main:
            if int(input)<16:
                kvm_socket(kvm.kvm_ip_address, kvm.port, input)
                time.sleep(0.01)
                kvm_socket(kvm.kvm_ip_address2, kvm.port, "08")
            else:
                kvm_socket(kvm.kvm_ip_address2, kvm.port, int(input)-15)
                time.sleep(0.01)
                kvm_socket(kvm.kvm_ip_address, kvm.port, "16")
        else:
            if int(input) < 6:
                kvm_socket(kvm.kvm_ip_address, kvm.port, input)
                time.sleep(0.01)
                if kvm.main_connect < 4:
                    kvm_socket(main.kvm_ip_address, main.port, int(input)+(kvm.main_connect-1)*5)
                    time.sleep(0.01)
                    kvm_socket(main.kvm_ip_address2, main.port, "08")
                else:
                    kvm_socket(main.kvm_ip_address2, main.port, input)
                    time.sleep(0.01)
                    kvm_socket(main.kvm_ip_address, main.port, "16")
            else:
                kvm_socket(kvm.kvm_ip_address, kvm.port, input)
                time.sleep(0.01)
    except TimeoutError:
        return HttpResponseServerError('KVM과의 연결이 실패했습니다. 연결을 확인해주세요.')
    except Exception as e:
        print(e)

    return redirect('home')


@login_required(login_url='login_auth')
def profile_control(req):
    profile_id = req.GET.get("id", None)
    try:
        profile = Profile.objects.get(id=profile_id)
        mat_set = MatrixSetting.objects.filter(profile=profile)
        mat_set_serializer = MatrixSettingSerializer(mat_set, many=True).data
    except Exception as e:
        print(e)
    
    try:
        # for test in range(5):
        for i in mat_set:
            input_list = [i.input_a, i.input_b, i.input_c, i.input_d, i.input_e, i.input_f, i.input_g, i.input_h]
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((i.matrix.matrix_ip_address, i.matrix.port))                

            print("main thread start")

            threads = []

            for j in range(8):
                if int(input_list[j]) != 0:
                    # send_msg(client_socket, f'MT00RD0000NT')
                    # thread = Worker(client_socket, f'MT00SW{input_list[j]}0{j+1}NT')
                    thread = Worker(client_socket, f'MT00RD0000NT')
                    thread.start()
                    threads.append(thread)
                    # send_msg(client_socket, f'MT00SW{input_list[j]}0{j+1}NT')
                    # time.sleep(0.3)
                    time.sleep(3)

            for thread in threads:
                thread.join()  

            print("main thread end")    
            client_socket.close()
            
            # if int(i.input_kvm) != 0:
            #     if i.matrix.is_main:
            #         if int(i.input_kvm)<16:
            #             kvm_socket(i.matrix.kvm_ip_address, i.matrix.port, i.input_kvm)
            #             # time.sleep(0.3)
            #             kvm_socket(i.matrix.kvm_ip_address2, i.matrix.port, "08")
            #             # time.sleep(0.3)
            #         else:
            #             kvm_socket(i.matrix.kvm_ip_address2, i.matrix.port, int(i.input_kvm)-15)
            #             # time.sleep(0.3)
            #             kvm_socket(i.matrix.kvm_ip_address, i.matrix.port, "16")
            #             # time.sleep(0.3)
            #     else:
            #         kvm_socket(i.matrix.kvm_ip_address, i.matrix.port, i.input_kvm)
            #         # time.sleep(0.3)
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
            Profile 삭제 api
        """
        data= req.data
        profile = Profile.objects.get(id=data['id'])
        if data["_method"] == 'delete':
            profile.delete()
        elif data["_method"] == 'put':
            print(data)
            setattr(profile, 'name', data["name"])
            profile.save()

            mat_id_list = data["mat_id_list"].split(',')
            mat_input_list = ['input_a','input_b','input_c','input_d','input_e','input_f','input_g','input_h', 'input_kvm',]
            
            for i in range(len(mat_id_list)):
                mat = Mat.objects.get(id=mat_id_list[i])
                print(mat)
                mat_set = MatrixSetting.objects.filter(profile=profile).filter(matrix=mat)
                print(mat_set)
                for mat_input in mat_input_list:
                    print(mat_set[0], mat_input, data[mat_input].split(',')[i])
                    setattr(mat_set[0], mat_input, data[mat_input].split(',')[i])
                
                mat_set_serializer = MatrixSettingSerializer(mat_set[0]).data
                print(mat_set_serializer)
                mat_set[0].save()   

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