import socket
import concurrent.futures
import time

def scan_single_ip(ip, port=10580, timeout=0.1):
    """단일 IP 스캔 (내부 함수)"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((ip, port))
            return ip
    except:
        return None

def scan_devices(current_pi_ip, port=10580, timeout=0.1):
    ip_parts = current_pi_ip.split('.')[:3]
    base_ip = '.'.join(ip_parts) + '.'
    found_ips = []
    ips_to_scan = [f"{base_ip}{i}" for i in range(1, 255)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_ip = {executor.submit(scan_single_ip, ip, port, timeout): ip
                        for ip in ips_to_scan}

        for future in concurrent.futures.as_completed(future_to_ip):
            result = future.result()
            if result:
                found_ips.append(result)

    found_ips.sort(key=lambda ip: int(ip.split('.')[-1]))
    return found_ips

def calc_crc(data):
    """CRC 계산"""
    return sum(data) % 256

def build_set_ip_packet(ip_address_str):
    """IP 설정 패킷 생성"""
    ip_bytes = list(map(int, ip_address_str.split('.')))
    payload = [0x07, 0x05] + ip_bytes
    crc = calc_crc(payload)
    packet = [0x55, 0xAA] + payload + [crc, 0xEE]
    return bytes(packet)

def verify_packet_structure(packet):
    """패킷 구조 검증"""
    if packet[0] != 0x55 or packet[1] != 0xAA:
        return False
    if packet[-1] != 0xEE:
        return False

    crc_data = list(packet[2:-2])
    expected_crc = sum(crc_data) % 256
    actual_crc = packet[-2]

    if expected_crc != actual_crc:
        return False

    return True

def send_and_wait_response(ip, port, packet, timeout=2):
    """패킷 전송 및 응답 대기"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        s.sendall(packet)

        try:
            response = s.recv(1024)
            if response:
                return response
        except socket.timeout:
            pass

        s.close()
        return None

    except:
        return None

def change_ip(current_ip, new_ip, port=10580, timeout=2):
    """하드웨어 IP 변경"""
    packet = build_set_ip_packet(new_ip)

    if not verify_packet_structure(packet):
        return

    send_and_wait_response(current_ip, port, packet, timeout)