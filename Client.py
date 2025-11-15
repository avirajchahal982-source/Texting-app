import socket
import keyboard

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server
while true:
  message = input("Type your message")
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'message')
    data = s.recv(1024)
  print('Received', repr(data))
  if keyboard.is_pressed("esc"):
    break
