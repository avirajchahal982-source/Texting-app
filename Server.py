import socket
import threading

HOST = "0.0.0.0"  # listen on all network interfaces
PORT = 8080

clients = []  # list of connected clients


def broadcast(message, sender_conn):
    """Send message to all clients except sender"""
    for client in clients:
        if client != sender_conn:
            try:
                client.sendall(message.encode())
            except:
                clients.remove(client)


def handle_client(conn, addr):
    print(f"[CONNECTED] {addr}")
    clients.append(conn)
    try:
        while True:
            data = conn.recv(2048)
            if not data:
                break

            message = data.decode()
            print(f"[{addr}] {message}")
            broadcast(f"{addr[0]}: {message}", conn)

    except Exception as e:
        print(f"[ERROR] {addr} → {e}")
    finally:
        conn.close()
        if conn in clients:
            clients.remove(conn)
        print(f"[DISCONNECTED] {addr}")


def start_server():
    print(f"[STARTING] Server on {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    start_server()
