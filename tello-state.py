#
# Tello Python3 Control Demo 
#
# http://www.ryzerobotics.com/
#
# 1/1/2018

import threading 
import socket
import sys
import time
import platform  

tello_address = ('192.168.10.1', 8889)


state_host=''
state_port=8890
state_addr=(state_host,state_port)

sock= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(state_addr)


def recv():
    count = 0
    while True: 
        try:
            data, server = sock.recvfrom(1518)
            print(data.decode(encoding="utf-8"))
        except Exception:
            print ('\nExit . . .\n')
            break



#recvThread create
recvThread = threading.Thread(target=recv)
recvThread.start()

while True: 
    try:
        msg = input("");
        
        if not msg:
            break  

        if 'end' in msg:
            print ('...')
            sock.close()  
            break

        # Send data
        msg = msg.encode(encoding="utf-8") 
        sent = sock.sendto(msg, tello_address)
    except KeyboardInterrupt:
        print ('\n . . .\n')
        sock.close()  
        break



