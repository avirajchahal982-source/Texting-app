import socket
import threading

HOST = "0.0.0.0"   # listen on all interfaces
PORT = 8080        # MUST match your client

def handle_client(conn, addr):
    print(f"[CONNECTED] {addr}")

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            message = data.decode()
            print(f"[RECEIVED from {addr}] {message}")

            # Reply to client
            response = f"Server received: {message}"
            conn.sendall(response.encode())

    except Exception as e:
        print(f"[ERROR] {addr} → {e}")

    finally:
        conn.close()
        print(f"[DISCONNECTED] {addr}")


def start_server():
    print(f"[STARTING] Server listening on {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()

        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


if __name__ == "__main__":
    start_server()
