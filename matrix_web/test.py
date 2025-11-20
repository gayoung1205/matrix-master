from django.http.response import HttpResponseServerError
import socket, time
import threading

class Worker(threading.Thread):
    def __init__(self, client_socket, msg):
        super().__init__()
        self.socket = client_socket           # thread 이름 지정
        self.msg = msg
    
    def run(self):
        msg = self.msg.encode()
        self.client_socket.sendall(msg)
    
def profile_control(req):
    try:
        input_list = ["01", "02", "03", "04", "05", "06", "07", "08"]
        ip = "192.168.50.234"
        port = 5000
        for input in input_list:
            
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((ip, port))                

            print("main thread start")

            threads = []

            for j in range(8):
                if int(input) != "00":
                    thread = Worker(client_socket, f'MT00SW{input}0{j+1}NT')
                    thread.start()
                    threads.append(thread)
                    time.sleep(0.3)

            for thread in threads:
                thread.join()  

            print("main thread end")    
            client_socket.close()
            
    except TimeoutError:
        return HttpResponseServerError('장치와의 연결이 실패했습니다. 연결을 확인해주세요.')
    except Exception as e:
        print(e)