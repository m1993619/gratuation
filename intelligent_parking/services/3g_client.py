import socket

#HOST = 'djoin.net'    # The remote host
#HOST = '127.0.0.1'
HOST = '60.160.152.127'
PORT = 1111              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send('$001,00,01,0')
data = s.recv(1024)
s.close()
print 'Received', repr(data)
