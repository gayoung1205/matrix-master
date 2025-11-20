# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


from tkinter import *
import socket

#프레임 틀 만들기
# root = Tk()
# root.title("AI Group Learning System")
# root.geometry("640x480+200+100")
# root.resizable(False,False) #틀 고정

#lae1 = label(root,text="11")
#lae1.pack()



#버튼만들기
# photo1 = PhotoImage(file="d:\projects\img\min.png")
# btn1 = Button(root, text="bo1")
# btn1.pack()



HOST1 = '192.168.100.232'
HOST2 = '192.168.100.231'
PORT1 = 5000
PORT2 = 5000
test = 'MT00SW0200NT'
test1 = 'MT00SW0200NT'
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((HOST1, PORT1))

client_socket.sendall(test.encode())

client_socket.close()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((HOST2, PORT2))

client_socket.sendall(test1.encode())

client_socket.close()

# root.mainloop()