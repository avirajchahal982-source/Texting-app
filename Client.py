import socket
import keyboard

HOST = '127.0.0.1'   # Replace with real server IP
PORT = 8080          # Valid port number

while True:
    message = input("Type your message: ")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(message.encode())   # send the actual user input
        data = s.recv(1024)

    print('Received:', data.decode())

    if keyboard.is_pressed("esc"):
        print("Exiting...")
        break
