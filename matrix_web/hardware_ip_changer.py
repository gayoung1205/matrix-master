import socket
import concurrent.futures

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
    return sum(data) % 256

def build_set_ip_packet(ip_address_str):
    ip_bytes = list(map(int, ip_address_str.split('.')))
    payload = [0x07, 0x03] + ip_bytes
    crc = calc_crc(payload)
    packet = [0x55, 0xAA] + payload + [crc, 0xEE]
    return bytes(packet)

def change_ip(current_ip, new_ip, port=10580, timeout=2):
    packet = build_set_ip_packet(new_ip)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        s.connect((current_ip, port))
        s.send(packet)
        try:
            resp = s.recv(1024)
            # 수정: hex() 에러 해결
            print("[응답]", ' '.join(f'{b:02X}' for b in resp))
        except socket.timeout:
            pass