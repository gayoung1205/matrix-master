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


def kvm_command_handle(input_port):
    """KVM 명령어 생성"""
    input_port = int(input_port)

    data = input_port - 1
    checksum = (data + 0x0D) & 0xFF

    command = f'55 AA 04 09 {data:02X} {checksum:02X} EE'
    return bytes.fromhex(command.replace(' ', ''))


def matrix_command_handle(input_port, target_port):
    """Matrix 명령어 생성 (16포트)"""
    input_port = int(input_port)
    target_port = int(target_port)

    data1 = (input_port - 1) + (target_port - 1) * 16
    data2 = (data1 + 0x0D) & 0xFF

    command = f'55 AA 05 08 00 {data1:02X} {data2:02X} EE'
    return bytes.fromhex(command.replace(' ', ''))


def matrix_all_command_handle(input_port):
    """Matrix ALL 명령어 생성"""
    input_port = int(input_port)

    data1 = 0xF0 + (input_port - 1)
    data2 = (0xFD + (input_port - 1)) & 0xFF

    command = f'55 AA 05 08 {data1:02X} 00 {data2:02X} EE'
    return bytes.fromhex(command.replace(' ', ''))


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

        time.sleep(delay_time)

        list = ['input_a','input_b','input_c','input_d','input_e','input_f','input_g','input_h',
                'input_i','input_j','input_k','input_l','input_m','input_n','input_o','input_p']

        field_index = int(target) - 1
        field_name = list[field_index]

        setattr(mat, field_name, input)
        mat.save()

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
    import socket
    import time
    import subprocess

    try:
        body = json.loads(request.body)
        current_ip = body.get('current_ip')
        new_ip = body.get('new_ip')

        if not current_ip or not new_ip:
            return JsonResponse({'success': False, 'error': 'IP 주소가 올바르지 않습니다.'})

        # ARP 캐시 클리어
        try:
            subprocess.run(['sudo', 'ip', '-s', '-s', 'neigh', 'flush', 'all'],
                           capture_output=True, timeout=5)
        except:
            pass

        # IP 변경 실행
        change_ip(current_ip, new_ip)

        # 10초 대기 후 네트워크 전체 스캔
        time.sleep(10)

        from .hardware_ip_changer import scan_devices
        from .rpi_ip_changer import get_current_ip

        rpi_ip = get_current_ip()
        found_devices = scan_devices(rpi_ip, timeout=0.2)

        if new_ip in found_devices:
            # ✅ DB 업데이트 추가 - 이전 IP를 가진 모든 Matrix 찾아서 업데이트
            updated_matrices = []

            # matrix_ip_address 업데이트
            matrices_by_matrix_ip = Mat.objects.filter(matrix_ip_address=current_ip)
            for mat in matrices_by_matrix_ip:
                mat.matrix_ip_address = new_ip
                mat.save()
                updated_matrices.append(f"{mat.name}(matrix_ip)")

            # kvm_ip_address 업데이트
            matrices_by_kvm_ip = Mat.objects.filter(kvm_ip_address=current_ip)
            for mat in matrices_by_kvm_ip:
                mat.kvm_ip_address = new_ip
                mat.save()
                if f"{mat.name}(kvm_ip)" not in updated_matrices:
                    updated_matrices.append(f"{mat.name}(kvm_ip)")

            # kvm_ip_address2 업데이트
            matrices_by_kvm_ip2 = Mat.objects.filter(kvm_ip_address2=current_ip)
            for mat in matrices_by_kvm_ip2:
                mat.kvm_ip_address2 = new_ip
                mat.save()
                if f"{mat.name}(kvm_ip2)" not in updated_matrices:
                    updated_matrices.append(f"{mat.name}(kvm_ip2)")

            print(f"✅ DB 업데이트 완료: {updated_matrices}")

            return JsonResponse({
                'success': True,
                'message': f'IP가 {new_ip}로 변경되었습니다. DB 업데이트: {len(updated_matrices)}건',
                'found_devices': found_devices,
                'updated_matrices': updated_matrices
            })
        elif current_ip in found_devices:
            return JsonResponse({
                'success': False,
                'error': f'IP 변경이 적용되지 않았습니다. 발견된 장비: {found_devices}'
            })
        elif len(found_devices) > 0:
            return JsonResponse({
                'success': False,
                'error': f'예상치 못한 상황: {found_devices}가 발견되었습니다. 이 중 하나가 하드웨어일 수 있습니다.'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': '하드웨어를 찾을 수 없습니다. 물리적으로 전원을 확인하거나 15초 더 기다려주세요.'
            })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

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
    return ok and ts and (time.time() - ts) < 600

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
    SYSTEM_PASSWORD = "admin123"

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

    if not check_system_access(req):

        return render(req, 'system_template/system_password.html', {
            'user': req.user,
            'current_time': time.strftime('%Y-%m-%d %H:%M:%S')
        })

    matrix = Mat.objects.all().order_by("created_date")
    main_connect_list = [1, 2, 3, 4]
    for i in matrix:
        if i.main_connect in main_connect_list:
            main_connect_list.remove(i.main_connect)

    remaining_time = 600 - (time.time() - req.session.get('system_access_time', time.time()))

    return render(req, 'system_template/system_template.html', {
        'matrix': matrix,
        'main_connect_list': main_connect_list,
        'system_access_user': req.session.get('system_access_user'),
        'access_time_remaining': max(0, int(remaining_time))
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
    if not _has_system_access(req):
        return redirect(f"/api/system_password/?next=/api/system_template/on_device/")

    req.session['system_access_time'] = time.time()
    req.session.modified = True

    device_names = {}
    try:
        from .models import DeviceNameConfig
        config = DeviceNameConfig.objects.filter(user=req.user)
        for item in config:
            device_names[item.device_type] = item.device_name
    except:
        pass

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

        subprocess.run(['sudo', '-K'])
        result = subprocess.run(
            f'echo "{password}" | sudo -S bash /tmp/safe_setup.sh',
            shell=True, capture_output=True, text=True
        )
        if "Sorry, try again" in result.stderr or "incorrect password" in result.stderr.lower():
            messages.error(request, '❌ 비밀번호가 틀렸습니다. 다시 확인해주세요.')
            return redirect('setup_ip_permission')
        elif "SUCCESS" in result.stdout:
            messages.success(request, '✅ 권한 설정 완료!')
            return redirect('on_device')
        elif "SYNTAX_ERROR" in result.stdout:
            messages.error(request, '❌ Sudoers 문법 오류 - 설정 실패')
        elif result.returncode != 0:
            if "is not in the sudoers file" in result.stderr:
                messages.error(request, f'❌ 사용자 {current_user}는 sudo 권한이 없습니다.')
            else:
                messages.error(request, f'❌ 설정 실패: {result.stderr}')
    except Exception as e:
        messages.error(request, f'❌ 오류 발생: {str(e)}')

    return redirect('setup_ip_permission')


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

        time.sleep(0.5)
        check_result = subprocess.run(
            ['sudo', 'test', '-f', '/etc/sudoers.d/matrix_ip_change'],
            capture_output=True
        )

        if check_result.returncode != 0:
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

# ============================================
# 비디오월 관련 Views - 수정된 버전
# ============================================
#
# 중요! 프로토콜 문서와 실제 장비 동작이 반대입니다:
#   - 명령 0x00 → 실제로 Splicer 모드
#   - 명령 0x01 → 실제로 Matrix 모드
#   - DeviceMode 응답 0 → Splicer
#   - DeviceMode 응답 1 → Matrix
#
# 이 파일의 함수들로 views.py의 해당 함수들을 교체하세요.
# ============================================

import socket
import time
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


# ============================================
# 모드 전환 명령어 상수 (실제 장비 동작 기준!)
# ============================================
CMD_TO_MATRIX = bytes([0x55, 0xAA, 0x04, 0x0B, 0x01, 0x10, 0xEE])   # 실제 Matrix 전환
CMD_TO_SPLICER = bytes([0x55, 0xAA, 0x04, 0x0B, 0x00, 0x0F, 0xEE])  # 실제 Splicer 전환
CMD_QUERY = bytes([0x55, 0xAA, 0x05, 0x08, 0x11, 0x00, 0x1E, 0xEE]) # 상태 조회


def parse_device_mode(response):
    """
    Device Info 응답에서 모드 파싱
    실제 장비: DeviceMode 1=Matrix, 0=Splicer
    """
    if not response or len(response) < 5:
        return None, None

    raw_value = response[4]
    # 실제 장비 동작: 1=Matrix, 0=Splicer
    if raw_value == 1:
        return 0, "Matrix"   # mode=0은 UI에서 Matrix를 의미
    else:
        return 1, "Splicer"  # mode=1은 UI에서 Splicer를 의미


def send_command(ip, port, command, timeout=5):
    """
    장비에 명령 전송 및 응답 수신
    """
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(timeout)
        client_socket.connect((ip, port))

        client_socket.sendall(command)
        time.sleep(0.3)

        response = b''
        try:
            response = client_socket.recv(1024)
        except socket.timeout:
            pass

        client_socket.close()
        return response
    except Exception as e:
        print(f"[ERROR] send_command 실패: {e}")
        return None


# ============================================
# 비디오월 페이지
# ============================================
@login_required
def video_wall(request):
    """비디오월 페이지"""
    from .models import Matrix as Mat, VideoWall
    from django.shortcuts import render

    mat = Mat.objects.first()
    video_walls = VideoWall.objects.filter(matrix=mat) if mat else []

    context = {
        'matrix': mat,
        'video_walls': video_walls,
    }
    return render(request, 'video_wall.html', context)


# ============================================
# 장비 모드 조회 (수정됨)
# ============================================
@login_required
def get_device_mode(request):
    """
    현재 장비 모드 조회

    실제 장비 응답:
      - DeviceMode = 1 → Matrix
      - DeviceMode = 0 → Splicer

    UI 반환값:
      - mode = 0 → Matrix
      - mode = 1 → Splicer
    """
    from .models import Matrix as Mat

    mat = Mat.objects.first()
    if not mat:
        return JsonResponse({'success': False, 'error': '장비가 없습니다.'}, status=404)

    try:
        response = send_command(mat.matrix_ip_address, mat.port, CMD_QUERY, timeout=3)

        if response and len(response) >= 5:
            mode, mode_name = parse_device_mode(response)

            if mode is not None:
                print(f"[DEBUG] 모드 조회: raw={response[4]}, mode={mode}, name={mode_name}")
                return JsonResponse({
                    'success': True,
                    'mode': mode,
                    'mode_name': mode_name
                })

        # 응답이 없거나 파싱 실패 시 기본값
        return JsonResponse({
            'success': True,
            'mode': 0,
            'mode_name': 'Matrix'
        })

    except Exception as e:
        print(f"[WARN] 모드 조회 실패: {e}")
        return JsonResponse({
            'success': True,
            'mode': 0,
            'mode_name': 'Matrix'
        })


# ============================================
# 장비 모드 전환 (수정됨)
# ============================================
# @login_required
# def toggle_device_mode(request):
#     """
#     장비 모드 전환 (Matrix ↔ Splicer)
#
#     UI 요청:
#       - target_mode = 0 → Matrix로 전환
#       - target_mode = 1 → Splicer로 전환
#
#     실제 명령:
#       - Matrix 전환: 0x01 (문서와 반대!)
#       - Splicer 전환: 0x00 (문서와 반대!)
#     """
#     from .models import Matrix as Mat
#
#     if request.method != 'POST':
#         return JsonResponse({'success': False, 'error': 'POST 요청만 허용'}, status=405)
#
#     mat = Mat.objects.first()
#     if not mat:
#         return JsonResponse({'success': False, 'error': '장비가 없습니다.'}, status=404)
#
#     try:
#         data = json.loads(request.body)
#         target_mode = data.get('mode', 0)  # 0: Matrix, 1: Splicer
#
#         # 실제 장비 동작 기준 명령어 선택!
#         if target_mode == 0:
#             # Matrix로 전환 → 실제로는 0x01 전송
#             command = CMD_TO_MATRIX
#             mode_name = "Matrix"
#         else:
#             # Splicer로 전환 → 실제로는 0x00 전송
#             command = CMD_TO_SPLICER
#             mode_name = "Splicer"
#
#         print(f"[DEBUG] 모드 전환: target={target_mode}({mode_name}), cmd={command.hex().upper()}")
#
#         # 명령 전송 (2회 전송으로 안정성 확보)
#         response = send_command(mat.matrix_ip_address, mat.port, command)
#         time.sleep(0.2)
#         response = send_command(mat.matrix_ip_address, mat.port, command)
#
#         # 응답 확인
#         if response and len(response) >= 5:
#             actual_mode, actual_name = parse_device_mode(response)
#             print(f"[DEBUG] 전환 결과: raw={response[4]}, mode={actual_mode}, name={actual_name}")
#
#             return JsonResponse({
#                 'success': True,
#                 'mode': actual_mode if actual_mode is not None else target_mode,
#                 'mode_name': actual_name if actual_name else mode_name,
#                 'message': f'{actual_name if actual_name else mode_name} 모드로 전환되었습니다!'
#             })
#
#         return JsonResponse({
#             'success': True,
#             'mode': target_mode,
#             'mode_name': mode_name,
#             'message': f'{mode_name} 모드로 전환되었습니다!'
#         })
#
#     except Exception as e:
#         import traceback
#         print(f"[ERROR] {traceback.format_exc()}")
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def toggle_device_mode(request):
    """
    장비 모드 전환 (Matrix ↔ Splicer ↔ Splitter)

    UI 요청:
      - target_mode = 0 → Matrix로 전환
      - target_mode = 1 → Splicer로 전환
      - target_mode = 2 → Splitter로 전환 (테스트)
    """

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST 요청만 허용'}, status=405)

    mat = Mat.objects.first()
    if not mat:
        return JsonResponse({'success': False, 'error': '장비가 없습니다.'}, status=404)

    try:
        data = json.loads(request.body)
        target_mode = data.get('mode', 0)  # 0: Matrix, 1: Splicer, 2: Splitter

        # 모드별 명령어 선택
        if target_mode == 0:
            # Matrix로 전환 → 실제로는 0x01 전송
            command = CMD_TO_MATRIX
            mode_name = "Matrix"
        elif target_mode == 1:
            # Splicer로 전환 → 실제로는 0x00 전송
            command = CMD_TO_SPLICER
            mode_name = "Splicer"
        elif target_mode == 2:
            # Splitter로 전환 → 0x02 테스트
            # CRC: 0x55 + 0xAA + 0x04 + 0x0B + 0x02 = 0x110 → 0x10
            command = bytes([0x55, 0xAA, 0x04, 0x0B, 0x02, 0x10, 0xEE])
            mode_name = "Splitter"
        else:
            return JsonResponse({'success': False, 'error': f'알 수 없는 모드: {target_mode}'}, status=400)

        print(f"[DEBUG] 모드 전환: target={target_mode}({mode_name}), cmd={command.hex().upper()}")

        # 명령 전송 (2회 전송으로 안정성 확보)
        response = send_command(mat.matrix_ip_address, mat.port, command)
        time.sleep(0.2)
        response = send_command(mat.matrix_ip_address, mat.port, command)

        # 응답 로그
        if response:
            response_hex = ' '.join(f'{b:02X}' for b in response)
            print(f"[DEBUG] 응답: {response_hex} ({len(response)} bytes)")
            if len(response) >= 5:
                print(f"[DEBUG] DeviceMode raw: {response[4]}")

        return JsonResponse({
            'success': True,
            'mode': target_mode,
            'mode_name': mode_name,
            'message': f'{mode_name} 모드로 전환되었습니다!'
        })

    except Exception as e:
        import traceback
        print(f"[ERROR] {traceback.format_exc()}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================
# 비디오월 적용 (수정됨)
# ============================================
@login_required
def video_wall_apply(request, video_wall_id):
    """
    비디오월 하드웨어에 적용

    1. Splicer 모드로 전환 (0x00 전송)
    2. Splicer 좌표 명령 전송
    """
    from .models import Matrix as Mat, VideoWall

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST 요청만 허용'}, status=405)

    try:
        video_wall = VideoWall.objects.get(id=video_wall_id)
        mat = video_wall.matrix

        print(f"[DEBUG] ===== 비디오월 적용 시작 =====")
        print(f"[DEBUG] 비디오월: {video_wall.name}")
        print(f"[DEBUG] 영역: ({video_wall.start_x},{video_wall.start_y}) ~ ({video_wall.end_x},{video_wall.end_y})")
        print(f"[DEBUG] 입력 소스: {video_wall.input_source}")

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)
        client_socket.connect((mat.matrix_ip_address, mat.port))

        # 1. Splicer 모드로 전환 (실제로는 0x00 전송!)
        mode_command = CMD_TO_SPLICER
        print(f"[DEBUG] 1. Splicer 모드 전환 명령: {mode_command.hex().upper()}")
        client_socket.sendall(mode_command)
        time.sleep(0.3)

        # 응답 읽기
        try:
            resp = client_socket.recv(1024)
            print(f"[DEBUG] 모드 전환 응답: {len(resp)} bytes")
        except:
            pass

        time.sleep(0.3)

        # 2. Splicer 명령 전송 (좌표 설정)
        splicer_command = video_wall.get_splicer_command()
        print(f"[DEBUG] 2. Splicer 명령: {splicer_command.hex().upper()}")
        client_socket.sendall(splicer_command)
        time.sleep(0.3)

        # 응답 읽기
        try:
            resp = client_socket.recv(1024)
            print(f"[DEBUG] Splicer 응답: {len(resp)} bytes")
        except:
            pass

        client_socket.close()

        print(f"[DEBUG] ===== 비디오월 적용 완료 =====")

        return JsonResponse({
            'success': True,
            'message': f'"{video_wall.name}" 비디오월이 적용되었습니다.',
            'command_hex': splicer_command.hex().upper()
        })

    except VideoWall.DoesNotExist:
        return JsonResponse({'success': False, 'error': '비디오월을 찾을 수 없습니다.'}, status=404)
    except Exception as e:
        import traceback
        print(f"[ERROR] {traceback.format_exc()}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================
# 비디오월 해제 (수정됨)
# ============================================
@login_required
def video_wall_release(request):
    """
    비디오월 해제 (Matrix 모드로 복귀)

    실제 장비: Matrix 전환은 0x01 전송!
    """
    from .models import Matrix as Mat

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST 요청만 허용'}, status=405)

    mat = Mat.objects.first()
    if not mat:
        return JsonResponse({'success': False, 'error': '장비가 없습니다.'}, status=404)

    try:
        print(f"[DEBUG] ===== Matrix 모드 복귀 시작 =====")

        # Matrix 모드로 전환 (실제로는 0x01 전송!)
        command = CMD_TO_MATRIX
        print(f"[DEBUG] Matrix 모드 전환 명령: {command.hex().upper()}")

        # 2회 전송으로 안정성 확보
        response = send_command(mat.matrix_ip_address, mat.port, command)
        time.sleep(0.2)
        response = send_command(mat.matrix_ip_address, mat.port, command)

        if response and len(response) >= 5:
            mode, mode_name = parse_device_mode(response)
            print(f"[DEBUG] 전환 결과: mode={mode}, name={mode_name}")

        print(f"[DEBUG] ===== Matrix 모드 복귀 완료 =====")

        return JsonResponse({
            'success': True,
            'message': '비디오월이 해제되고 Matrix 모드로 복귀했습니다.'
        })

    except Exception as e:
        import traceback
        print(f"[ERROR] {traceback.format_exc()}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================
# 비디오월 목록 조회 (변경 없음)
# ============================================
@login_required
def video_wall_list(request):
    """저장된 비디오월 목록 조회"""
    from .models import Matrix as Mat, VideoWall

    mat = Mat.objects.first()
    if not mat:
        return JsonResponse({'success': False, 'error': '장비가 없습니다.'}, status=404)

    video_walls = VideoWall.objects.filter(matrix=mat)
    data = []
    for vw in video_walls:
        data.append({
            'id': vw.id,
            'name': vw.name,
            'start_x': vw.start_x,
            'start_y': vw.start_y,
            'end_x': vw.end_x,
            'end_y': vw.end_y,
            'input_source': vw.input_source,
            'size': vw.get_size_display(),
            'monitors': vw.get_monitor_list(),
            'created_date': vw.created_date.strftime('%Y-%m-%d %H:%M'),
        })

    return JsonResponse({'success': True, 'video_walls': data})


# ============================================
# 비디오월 생성 (변경 없음)
# ============================================
@login_required
def video_wall_create(request):
    """비디오월 생성"""
    from .models import Matrix as Mat, VideoWall

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST 요청만 허용'}, status=405)

    mat = Mat.objects.first()
    if not mat:
        return JsonResponse({'success': False, 'error': '장비가 없습니다.'}, status=404)

    try:
        data = json.loads(request.body)

        name = data.get('name', '').strip()
        if not name:
            return JsonResponse({'success': False, 'error': '이름을 입력해주세요.'}, status=400)

        video_wall = VideoWall.objects.create(
            name=name,
            matrix=mat,
            start_x=int(data.get('start_x', 0)),
            start_y=int(data.get('start_y', 0)),
            end_x=int(data.get('end_x', 0)),
            end_y=int(data.get('end_y', 0)),
            input_source=int(data.get('input_source', 1)),
        )

        return JsonResponse({
            'success': True,
            'message': f'"{name}" 비디오월이 생성되었습니다.',
            'id': video_wall.id
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================
# 비디오월 삭제 (변경 없음)
# ============================================
@login_required
def video_wall_delete(request, video_wall_id):
    """비디오월 삭제"""
    from .models import VideoWall

    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'error': 'DELETE 요청만 허용'}, status=405)

    try:
        video_wall = VideoWall.objects.get(id=video_wall_id)
        name = video_wall.name
        video_wall.delete()

        return JsonResponse({
            'success': True,
            'message': f'"{name}" 비디오월이 삭제되었습니다.'
        })

    except VideoWall.DoesNotExist:
        return JsonResponse({'success': False, 'error': '비디오월을 찾을 수 없습니다.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# ============================================
# Splitter 테스트 API
# ============================================
@login_required
def splitter(request):
    """Splitter 페이지"""
    from .models import Matrix as Mat
    from django.shortcuts import render

    mat = Mat.objects.first()

    context = {
        'matrix': mat,
    }
    return render(request, 'splitter.html', context)

@login_required
def splitter_test(request):
    """
    Splitter 테스트 명령 전송 (길이 5 버전)
    """
    from .models import Matrix as Mat
    import socket
    import time

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST 요청만 허용'}, status=405)

    mat = Mat.objects.first()
    if not mat:
        return JsonResponse({'success': False, 'error': '장비가 없습니다.'}, status=404)

    try:
        data = json.loads(request.body)
        mode = int(data.get('mode', 0))          # 0~3
        input_source = int(data.get('input_source', 1))  # 1~16

        # 데이터 바이트 계산
        input_value = input_source - 1  # 0-based
        data_byte = (mode << 4) | input_value

        # ===== 테스트: 길이 5 버전 =====
        bytes_list = [0x55, 0xAA, 0x05, 0x15, 0x00, data_byte]
        crc = sum(bytes_list) & 0xFF
        command = bytes([0x55, 0xAA, 0x05, 0x15, 0x00, data_byte, crc, 0xEE])

        command_hex = ' '.join(f'{b:02X}' for b in command)

        print(f"[DEBUG] ===== Splitter 테스트 (길이 5) =====")
        print(f"[DEBUG] 모드: {mode} (윈도우: {[1,2,4,16][mode]}분할)")
        print(f"[DEBUG] 입력: {input_source} (값: {input_value})")
        print(f"[DEBUG] 데이터 바이트: 0x{data_byte:02X}")
        print(f"[DEBUG] 명령어: {command_hex}")

        # 장비에 전송
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)
        client_socket.connect((mat.matrix_ip_address, mat.port))

        client_socket.sendall(command)
        time.sleep(0.5)

        # 응답 수신
        response = b''
        try:
            response = client_socket.recv(1024)
        except socket.timeout:
            pass

        client_socket.close()

        response_hex = ' '.join(f'{b:02X}' for b in response) if response else 'No response'
        print(f"[DEBUG] 응답: {response_hex} ({len(response)} bytes)")
        print(f"[DEBUG] ===== Splitter 테스트 완료 =====")

        return JsonResponse({
            'success': True,
            'message': 'Splitter 명령 전송 완료',
            'command_hex': command_hex,
            'response_hex': response_hex,
            'response_length': len(response),
        })

    except Exception as e:
        import traceback
        print(f"[ERROR] {traceback.format_exc()}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# ============================================
# Splitter 모드 전환 테스트 API
# ============================================
@login_required
def splitter_switch_mode(request):
    """
    모드 전환 테스트

    명령: 55 AA 04 0B XX CRC EE
    XX: 0x00=Splicer?, 0x01=Matrix?, 0x02=Splitter?
    """
    from .models import Matrix as Mat
    import socket
    import time

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST 요청만 허용'}, status=405)

    mat = Mat.objects.first()
    if not mat:
        return JsonResponse({'success': False, 'error': '장비가 없습니다.'}, status=404)

    try:
        data = json.loads(request.body)
        mode_value = int(data.get('mode_value', 0))
        mode_name = data.get('mode_name', 'Unknown')

        # CRC 계산
        bytes_list = [0x55, 0xAA, 0x04, 0x0B, mode_value]
        crc = sum(bytes_list) & 0xFF
        command = bytes([0x55, 0xAA, 0x04, 0x0B, mode_value, crc, 0xEE])
        command_hex = ' '.join(f'{b:02X}' for b in command)

        print(f"[DEBUG] ===== 모드 전환 테스트 =====")
        print(f"[DEBUG] 모드: {mode_name} (값: 0x{mode_value:02X})")
        print(f"[DEBUG] 명령어: {command_hex}")

        # 장비에 전송
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)
        client_socket.connect((mat.matrix_ip_address, mat.port))

        client_socket.sendall(command)
        time.sleep(0.5)

        # 응답 수신
        response = b''
        try:
            response = client_socket.recv(1024)
        except socket.timeout:
            pass

        client_socket.close()

        response_hex = ' '.join(f'{b:02X}' for b in response) if response else 'No response'
        print(f"[DEBUG] 응답: {response_hex} ({len(response)} bytes)")

        # DeviceMode 파싱 (응답이 있으면)
        device_mode_raw = None
        if response and len(response) >= 5:
            device_mode_raw = response[4]
            print(f"[DEBUG] DeviceMode raw: {device_mode_raw}")

        print(f"[DEBUG] ===== 모드 전환 테스트 완료 =====")

        return JsonResponse({
            'success': True,
            'message': f'{mode_name} 모드 전환 명령 전송 완료',
            'command_hex': command_hex,
            'response_hex': response_hex,
            'response_length': len(response),
            'device_mode_raw': device_mode_raw
        })

    except socket.error as e:
        print(f"[ERROR] 소켓 오류: {e}")
        return JsonResponse({'success': False, 'error': f'통신 오류: {e}'}, status=500)
    except Exception as e:
        import traceback
        print(f"[ERROR] {traceback.format_exc()}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def debug_device_info(request):
    """Device Info 전체 응답 분석"""
    from .models import Matrix as Mat
    import socket
    import time

    mat = Mat.objects.first()
    if not mat:
        return JsonResponse({'success': False, 'error': '장비 없음'})

    try:
        # 상태 조회 명령
        command = bytes([0x55, 0xAA, 0x05, 0x08, 0x11, 0x00, 0x1E, 0xEE])

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)
        client_socket.connect((mat.matrix_ip_address, mat.port))
        client_socket.sendall(command)
        time.sleep(0.5)

        response = b''
        try:
            response = client_socket.recv(1024)
        except:
            pass
        client_socket.close()

        if response and len(response) >= 60:
            # Device Info 파싱
            info = {
                'raw_hex': ' '.join(f'{b:02X}' for b in response),
                'length': len(response),
                'DeviceMode': response[4],           # 바이트 4
                'SplitterFrameIndex': response[56] if len(response) > 56 else None,  # 추정
                'SplitterSwitchState': response[57] if len(response) > 57 else None,  # 추정
                # 주요 바이트들
                'byte_52': response[52] if len(response) > 52 else None,
                'byte_53': response[53] if len(response) > 53 else None,
                'byte_54': response[54] if len(response) > 54 else None,
                'byte_55': response[55] if len(response) > 55 else None,
                'byte_56': response[56] if len(response) > 56 else None,
                'byte_57': response[57] if len(response) > 57 else None,
                'byte_58': response[58] if len(response) > 58 else None,
            }

            print(f"[DEBUG] ===== Device Info 분석 =====")
            print(f"[DEBUG] DeviceMode: {info['DeviceMode']}")
            print(f"[DEBUG] byte_52: {info['byte_52']} (0x{info['byte_52']:02X})" if info['byte_52'] else "")
            print(f"[DEBUG] byte_53: {info['byte_53']} (0x{info['byte_53']:02X})" if info['byte_53'] else "")
            print(f"[DEBUG] byte_54: {info['byte_54']} (0x{info['byte_54']:02X})" if info['byte_54'] else "")
            print(f"[DEBUG] byte_55: {info['byte_55']} (0x{info['byte_55']:02X})" if info['byte_55'] else "")
            print(f"[DEBUG] byte_56: {info['byte_56']} (0x{info['byte_56']:02X})" if info['byte_56'] else "")
            print(f"[DEBUG] byte_57: {info['byte_57']} (0x{info['byte_57']:02X})" if info['byte_57'] else "")
            print(f"[DEBUG] ================================")

            return JsonResponse({'success': True, **info})

        return JsonResponse({'success': False, 'error': 'No response'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})