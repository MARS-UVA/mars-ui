from serial import var_len_proto_send, var_len_proto_recv
from random import randint
print(" ")
print(" ")
print(" ")

def gen_var_send_test(data: list):
    count = len(data)
    count = count | 0b11000000

    buffer = [0xff, count]
    buffer.extend(data)
    buffer.append(sum(buffer) % 256)
    return bytes(buffer)

print("Starting Tests...")
print(" ")

# Client Test
assert var_len_proto_send([1, 2, 3]) == bytes([255, 195, 1, 2, 3, 200])
for i in range(50):
    count = randint(1, 16)
    data = [randint(0, 255) for i in range(count)]
    assert var_len_proto_send(data) == gen_var_send_test(data)

print("Client Test Passed ...")

# Server test
assert var_len_proto_recv(bytes([255, 195, 1, 2, 3, 200])) == [[1, 2, 3]]
for i in range(50):
    count = randint(1, 16)
    data = [randint(0, 255) for i in range(count)]
    assert var_len_proto_recv(gen_var_send_test(data)) == [data]

print("Server Test Passed ...")

# --- incomplete data test
assert var_len_proto_recv(bytes([254])) == []
assert var_len_proto_recv(bytes([])) == []
assert var_len_proto_recv(bytes([255, 195, 1, 2, 3, 199])) == [] # checksum mismatch
assert var_len_proto_recv(bytes([255, 195])) == [] # segmented data
assert var_len_proto_recv(bytes([1, 2, 3, 200])) == [[1, 2, 3]]
assert var_len_proto_recv(bytes([255, 195, 2, 2, 3])) == []
assert var_len_proto_recv(bytes([201])) == [[2, 2, 3]]
assert var_len_proto_recv(bytes([255])) == []
assert var_len_proto_recv(bytes([195])) == []
assert var_len_proto_recv(bytes([2])) == []
assert var_len_proto_recv(bytes([2, 3])) == []
assert var_len_proto_recv(bytes([201])) == [[2, 2, 3]]
assert var_len_proto_recv(bytes([255, 64, 1, 2, 3, 200])) == [] # count byte mismatch
assert var_len_proto_recv(bytes([255, 195, 1, 2, 3, 200] * 2)) == [[1, 2, 3]] * 2 # two packages all at once

print("Incomplete Data Test Passed ...")

print(" ")
print("All Tests Passed!")