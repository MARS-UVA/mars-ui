import socket
import traceback

if __name__ == "__main__":
    HOST = ''                # Symbolic name meaning all available interfaces
    PORT = 6666              # Arbitrary non-privileged port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        try:
            conn, addr = s.accept()
            print("Connected by", addr)

            while True:
                data = conn.recv(1024)
                print(data)

        except KeyboardInterrupt:
            print("Shutting down the socket")
            s.close()  # cleanup socket
