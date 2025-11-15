import socket
import keyboard

HOST = '676.7.6.7'  # The server's hostname or IP address
PORT = 676767        # The port used by the server
while True:
  message = input("Type your message")
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'message')
    data = s.recv(1024)
  print('Received', repr(data))
  if keyboard.is_pressed("esc"):
    break
