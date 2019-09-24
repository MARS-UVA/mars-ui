import socket
import threading
import traceback


def checksum(bs, count):
    return sum(bs[:-1]) % 255 == bs[-1]


READ_LEN = 20
TRY_LEN = 10


def handle_connection(conn: socket.socket, addr):
    temp = bytes()
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                print(str(addr), "closed the connection")
                conn.close()
                break
            temp += data
            if len(temp) > 2: # read at least 3 bytes
                for i in range(len(temp) - 2):
                    if temp[i] == 0xff and temp[i + 1] == 0xff:  # check the header
                        count = temp[i + 2] 
                        expected_len = 3 + count + 1 # 2 header + 1 count bytes + ... + 1 checksum
                        if len(temp) >= i + expected_len: # if temp's length is greater than the expected packet length
                            slc = temp[i:i + expected_len]
                            conn.sendall(
                                bytes("You send {}\nThe checksum is {}\n".format(
                                    str(list(slc)), "correct" if checksum(slc, count) else "incorrect"), "utf-8")
                            )

                            # remove bytes already read
                            if len(temp) == i + expected_len:
                                temp = bytes()
                            else:
                                temp = temp[i + expected_len:]

                        else:
                            resp = "Header matched. Expected {} more bytes".format(i + expected_len - len(temp))
                            conn.sendall(bytes(resp, "utf-8"))
                            print(resp)
                            temp = temp[i:] # remove bytes already read
                        break
            
                else: # no header found, not protocol, discard the entire sequence
                    temp = bytes()
                    try:
                        content = data.decode("utf-8")
                    except:
                        content = str(data)
                    
                    resp = "(Not protocol) {} sends {}".format(str(addr), content) # return response as-is
                    print(resp)
                    conn.sendall(bytes(resp, "utf-8"))
        except ConnectionResetError:
            traceback.print_exc()
            break
        except BrokenPipeError:
            traceback.print_exc()
            break
        except:
            print("Failed to send response")
            traceback.print_exc()


if __name__ == "__main__":
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
                break

            print("Connected by", addr)
            t = threading.Thread(target=handle_connection, args=(conn, addr))
            t.start()
            threads.append(t)
            
        print("Shutting down the socket")
        s.close()  # cleanup socket