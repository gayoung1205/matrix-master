# from django import template
#
# register = template.Library()
#
# @register.filter(name='range_tag')
# def range_tag(start_val, end_val):
#     return range(start_val, end_val)
#
# @register.filter(name='list_index')
# def list_index(list, num):
#     if num == 0:
#         return "-"
#     elif 0 < num < 10:
#         return "PC"+str(num)
#     elif 10 <= num < 21:
#         return "PC"+str(num)
#     else:
#         return "T"
#
#
# @register.filter
# def kvm_index(list, num):
#     if num == 0:
#         return "-"
#     elif 0 < num < 10:
#         return "PC0"+str(num)
#     elif 10 <= num < 21:
#         return "PC"+str(num)
#     else:
#         return "T"
#
#
# @register.filter(name='option_selected')
# def option_selected(main, num):
#     if num == 1:
#         return int(main.input_a)
#     elif num == 2:
#         return int(main.input_b)
#     elif num == 3:
#         return int(main.input_c)
#     elif num == 4:
#         return int(main.input_d)
#     elif num == 5:
#         return int(main.input_e)
#     elif num == 6:
#         return int(main.input_f)
#     elif num == 7:
#         return int(main.input_g)
#     elif num == 8:
#         return int(main.input_h)
#     elif num == 9:
#         return int(main.input_i)
#     elif num == 10:
#         return int(main.input_j)
#     elif num == 11:
#         return int(main.input_k)
#     elif num == 12:
#         return int(main.input_l)
#     elif num == 13:
#         return int(main.input_m)
#     elif num == 14:
#         return int(main.input_n)
#     elif num == 15:
#         return int(main.input_o)
#     elif num == 16:
#         return int(main.input_p)
#     else:
#         return "X"
#
# @register.filter
# def remainder(target, num):
#     return target%num
#
# @register.filter
# def group_index(connect: int, num: int):
#     if num == 0:
#         return "-"
#     else:
#         if (connect-1)*5+num < 10:
#             return "PC0"+str((connect-1)*5+num)
#         else:
#             return "PC"+str((connect-1)*5+num)

# 가영추가

from django import template
from django.apps import apps

from django import template
from django.apps import apps

register = template.Library()

@register.filter(name='range_tag')
def range_tag(start_val, end_val):
    return range(start_val, end_val)

@register.filter(name='list_index')
def list_index(list, num):
    if num == 0:
        return "-"
    elif 1 <= num <= len(list) if list else 0:
        return list[num-1]  # 실제 리스트 값 사용
    elif num == 17:  # 16포트에서는 17번이 T
        return "T"
    elif num == 18:  # 16포트에서는 18번이 전자칠판
        return "전자칠판"
    else:
        return f"입력{num:02}"

@register.filter(name='option_selected')
def option_selected(main, num):
    """16포트용 option_selected 필터"""
    if num == 1:
        return int(main.input_a)
    elif num == 2:
        return int(main.input_b)
    elif num == 3:
        return int(main.input_c)
    elif num == 4:
        return int(main.input_d)
    elif num == 5:
        return int(main.input_e)
    elif num == 6:
        return int(main.input_f)
    elif num == 7:
        return int(main.input_g)
    elif num == 8:
        return int(main.input_h)
    elif num == 9:
        return int(main.input_i)
    elif num == 10:
        return int(main.input_j)
    elif num == 11:
        return int(main.input_k)
    elif num == 12:
        return int(main.input_l)
    elif num == 13:
        return int(main.input_m)
    elif num == 14:
        return int(main.input_n)
    elif num == 15:
        return int(main.input_o)
    elif num == 16:
        return int(main.input_p)
    else:
        return "X"

@register.filter
def remainder(target, num):
    return target%num

@register.filter
def kvm_index(list, num):
    if num == 0:
        return "-"
    elif 0 < num < 10:
        return "PC0"+str(num)
    elif 10 <= num < 21:
        return "PC"+str(num)
    else:
        return "T"

@register.filter
def group_index(mat, num: int):
    """
    즐겨찾기(프로필) 페이지에서 사용하는 필터 - 16포트용
    mat: Matrix 객체
    num: 모니터 위치 번호 (1~16)
    """
    Matrix = apps.get_model('matrix_web', 'Matrix')

    # Matrix 객체인지 확인
    if isinstance(mat, Matrix):
        # 커스텀 모니터 이름이 있는지 확인
        monitor_names = mat.monitor_names or []
        if num > 0 and num <= len(monitor_names):
            custom_name = monitor_names[num-1]
            if custom_name and custom_name.strip():
                return custom_name.strip()

    # 커스텀 이름이 없거나 Matrix 객체가 아닌 경우 기본 로직 사용
    # connect 값 추출 (Matrix 객체에서 main_connect 속성 사용)
    if isinstance(mat, Matrix):
        connect = mat.main_connect
    else:
        # 숫자로 전달된 경우 (기존 코드와의 호환성)
        connect = int(mat) if mat else 1

    # 기본 이름 반환 (16포트용)
    if num == 0:
        return "-"
    elif num == 17:
        return "T"
    elif num == 18:
        return "전자칠판"
    else:
        return f"모니터{int(num):02d}"

@register.filter(name='profile_monitor_name')
def profile_monitor_name(mat, position):
    """
    프로필(즐겨찾기)에서 사용할 모니터 이름 반환 - 16포트용
    커스텀 이름이 있으면 사용, 없으면 기본 이름 사용
    """
    Matrix = apps.get_model('matrix_web', 'Matrix')

    if isinstance(mat, Matrix):
        # 커스텀 모니터 이름 확인
        monitor_names = mat.monitor_names or []
        if position > 0 and position <= len(monitor_names):
            custom_name = monitor_names[position-1]
            if custom_name and custom_name.strip():
                return custom_name.strip()

        # 커스텀 이름이 없으면 group_index 로직 사용
        return group_index(mat, position)

    # Matrix 객체가 아닌 경우
    return f"모니터{position:02d}"

@register.filter(name='monitor_name')
def monitor_name(mat, position):
    """
    메인 매트릭스용 모니터 이름 반환 - 16포트용
    커스텀 이름이 있으면 사용, 없으면 기본값 사용
    """
    Matrix = apps.get_model('matrix_web', 'Matrix')
    if not isinstance(mat, Matrix):
        # 매트릭스 객체가 아닌 경우 위치에 따른 기본값 반환
        if position == 17:
            return "T"
        elif position == 18:
            return "전자칠판"
        else:
            return f"모니터{int(position):02d}"

    # 커스텀 모니터 이름 확인
    names = mat.monitor_names or []
    try:
        if position > 0 and position <= len(names):
            name = names[position-1]
            if name and name.strip():
                return name.strip()
    except Exception:
        pass

    # 커스텀 이름이 없으면 기본값 반환
    # 메인 매트릭스의 경우
    if mat.is_main:
        if position == 17:
            return "T"
        elif position == 18:
            return "전자칠판"
        else:
            return f"모니터{int(position):02d}"
    else:
        # 서브 매트릭스의 경우 group_index 로직 사용
        if position == 0:
            return "-"
        elif position == 17:
            return "T"
        elif position == 18:
            return "전자칠판"
        else:
            return f"모니터{int(position):02d}"

@register.filter(name='device_name')
def device_name(mat, position):
    """
    디바이스 이름 반환 - 16포트용
    - 저장된 커스텀 디바이스명이 있으면 그 값 사용
    - 없으면 'device01' ~ 'device16' 기본값 사용
    """
    Matrix = apps.get_model('matrix_web', 'Matrix')

    try:
        pos = int(position)
    except Exception:
        return ""

    if pos < 1 or pos > 16:  # 16포트로 확장
        return ""

    # 기본 디바이스 라벨
    default_label = f"입력{pos:02d}"

    # Matrix 객체가 아닌 경우에도 기본값 규칙 적용
    if not isinstance(mat, Matrix):
        return default_label

    names = mat.device_names or []
    if pos <= len(names):
        name = (names[pos-1] or "").strip()
        if name:
            return name

    # 커스텀 값이 없으면 기본값
    return default_label

@register.filter(name='device_monitor_label')
def device_monitor_label(mat, position):
    """
    드롭다운 표기용: 'deviceNN (monitorNN)' - 16포트용
    - 커스텀 값이 있으면 사용, 없으면 규칙값(deviceNN/monitorNN)으로 폴백
    - position=0일 때 '-'
    """
    try:
        pos = int(position)
    except Exception:
        return "-"
    if pos == 0:
        return "-"

    # 이미 정의된 필터 재사용
    dn = device_name(mat, pos)
    # 즐겨찾기 화면에선 profile_monitor_name이 사용자 정의를 더 잘 반영함
    mn = profile_monitor_name(mat, pos)

    # 비어있을 일은 거의 없지만 혹시 대비
    dn = dn.strip() if isinstance(dn, str) else f"입력{pos:02d}"
    mn = mn.strip() if isinstance(mn, str) else f"모니터{pos:02d}"

    return f"{dn} ({mn})"

# add 필터 추가 (템플릿에서 i|add:'-8' 같은 용도로 사용)
@register.filter
def add(value, arg):
    """템플릿에서 숫자 더하기"""
    try:
        return int(value) + int(arg)
    except (ValueError, TypeError):
        return value

# 16포트용 추가 필터들
@register.filter(name='input_field_name')
def input_field_name(position):
    """포지션에 따른 input 필드명 반환 (input_a ~ input_p)"""
    input_fields = [
        'input_a', 'input_b', 'input_c', 'input_d',
        'input_e', 'input_f', 'input_g', 'input_h',
        'input_i', 'input_j', 'input_k', 'input_l',
        'input_m', 'input_n', 'input_o', 'input_p'
    ]

    try:
        pos = int(position)
        if 1 <= pos <= 16:
            return input_fields[pos-1]
    except (ValueError, IndexError):
        pass

    return 'input_a'  # 기본값

@register.filter(name='get_input_value')
def get_input_value(matrix, position):
    """16포트 매트릭스에서 특정 포지션의 입력값 반환"""
    field_name = input_field_name(position)
    try:
        value = getattr(matrix, field_name, "01")
        return value if value else "01"
    except AttributeError:
        return "01"

@register.filter(name='range_16')
def range_16(start_val):
    """16포트용 범위 생성 (1~16)"""
    return range(start_val, 17)

@register.filter(name='port_range')
def port_range(start, end):
    """포트 범위 생성"""
    return range(start, end + 1)