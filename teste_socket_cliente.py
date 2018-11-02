import socket               
 
sock = socket.socket()
 
host = "192.168.42.252" #ESP32 IP in local network
port = 80            #ESP32 Server Port    

sock.connect((host, port))

# tmp = 2
# while 1:
#     tmp += 1
#     hs = host + str(tmp)
#     print(hs)
#     try:
#         sock.connect((hs, port))
#         break
#     except:
#         continue
 
message = "Get"
sock.send((message).encode())
 
data = ""       
 
while len(data) < 17:
    data += (sock.recv(1)).decode()
 
print(data)
 
sock.close()