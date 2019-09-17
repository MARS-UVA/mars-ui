import socket
import threading
import traceback


def checksum(bs):
    s = sum(bs[0:6])
    return s % 255 == bs[6]


def handle_connection(conn: socket.socket, addr):
    temp = bytes()
    while True:
        data = conn.recv(1024)
        if not data:
            print(str(addr), "closed the connection")
            break
        try:
            temp += data
            flag = False
            if len(temp) >= 14:
                for i in range(13):
                    h1 = temp[i]
                    h2 = temp[i + 1]
                    if h1 == 0xff and h2 == 0xff and i <= 7:
                        slc = temp[i:i+7]
                        conn.sendall("You send " + bytes(str(list(slc), "utf-8")))
                        flag = True
                        break
                temp = bytes()
            if not flag:
                resp = "(NP) " + str(addr) + " sends: " + str(data) + "\n"
                print(resp, end="")
                conn.sendall(bytes(resp, "utf-8"))
        except:
            print("Failed to send response")
            traceback.print_exc()


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
            s.shutdown(socket.SHUT_RDWR)
            s.close()  # cleanup socket
            break

        print("Connected by", addr)
        t = threading.Thread(target=handle_connection, args=(conn, addr))
        t.start()
