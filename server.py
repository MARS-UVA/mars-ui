import socket
import threading


def handle_connection(conn: socket.socket, addr):
    while True:
        data = conn.recv(1024)
        if not data:
            print(str(addr), "closed the connection")
        resp = str(addr) + " sends (reversed): " + data.decode().strip()[::-1] + "\n"
        print(resp, end="")
        conn.sendall(bytes(resp, "utf-8"))


HOST = ''                # Symbolic name meaning all available interfaces
PORT = 6666              # Arbitrary non-privileged port
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    threads = []
    while True:
        try:
            conn, addr = s.accept()
        except KeyboardInterrupt:
            print("Shutting down the socket")
            s.close()  # cleanup socket
            break

        print("Connected by", addr)
        t = threading.Thread(target=handle_connection, args=(conn, addr))
        t.start()
