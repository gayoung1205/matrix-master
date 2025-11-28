import socket
import time

IP = "192.168.1.135"
PORT = 10580

def send_cmd(cmd_bytes, desc=""):
    print(f"\n[{desc}] 전송: {' '.join(f'{b:02X}' for b in cmd_bytes)}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    sock.connect((IP, PORT))
    sock.sendall(cmd_bytes)
    time.sleep(0.5)
    resp = b''
    try:
        resp = sock.recv(1024)
    except:
        pass
    sock.close()
    print(f"[{desc}] 응답: {len(resp)} bytes")
    if len(resp) > 54:
        print(f"[{desc}] byte_54: {resp[54]} (0x{resp[54]:02X})")
    return resp

# 테스트 1: Splitter 명령만 (Splicer 모드 전환 없이)
print("===== 테스트 1: Splitter만 =====")
send_cmd(bytes([0x55, 0xAA, 0x04, 0x15, 0x30, 0x48, 0xEE]), "16분할")

time.sleep(1)

# 테스트 2: 같은 소켓에서 연속 전송
print("\n===== 테스트 2: 같은 소켓에서 연속 =====")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(3)
sock.connect((IP, PORT))

# Splicer 모드
cmd1 = bytes([0x55, 0xAA, 0x04, 0x0B, 0x00, 0x0F, 0xEE])
print(f"전송1: {' '.join(f'{b:02X}' for b in cmd1)}")
sock.sendall(cmd1)
time.sleep(0.5)
try:
    r1 = sock.recv(1024)
    print(f"응답1: {len(r1)} bytes")
except:
    print("응답1: timeout")

# Splitter 16분할
cmd2 = bytes([0x55, 0xAA, 0x04, 0x15, 0x30, 0x48, 0xEE])
print(f"전송2: {' '.join(f'{b:02X}' for b in cmd2)}")
sock.sendall(cmd2)
time.sleep(0.5)
try:
    r2 = sock.recv(1024)
    print(f"응답2: {len(r2)} bytes")
    if len(r2) > 54:
        print(f"byte_54: {r2[54]} (0x{r2[54]:02X})")
except:
    print("응답2: timeout")

sock.close()
