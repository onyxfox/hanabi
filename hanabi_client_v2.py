#! /Library/Frameworks/Python.framework/Versions/3.7/bin/python3
import socket
import threading
from pickle import dumps, loads

IP = '127.0.0.1'#'24.98.18.225'#
PORT = 19272

class Client:
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def sendMsg(self):
        while True:
            self.c.send(bytes(input(''), 'utf-8'))

    def __init__(self):
        self.c.connect((IP,PORT))

        iThread = threading.Thread(target=self.sendMsg)
        iThread.daemon = True
        iThread.start()

        while True:
            data = self.c.recv(1024)
            if not data:
                self.c.close()
                break
            # print(data.decode('utf-8'), end='')
            print(loads(data))

client = Client()
