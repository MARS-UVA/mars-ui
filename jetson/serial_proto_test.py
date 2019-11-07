from serial import list_to_byte, byte_to_list
from random import randint

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
assert list_to_byte([1, 2, 3]) == bytes([255, 195, 1, 2, 3, 200])
for i in range(50):
    count = randint(1, 16)
    data = [randint(0, 255) for i in range(count)]
    assert list_to_byte(data) == gen_var_send_test(data)

print("Client Test Passed ...")
         
# # Server test
# assert byte_to_list(bytes([255, 195, 1, 2, 3, 200])) == [[1, 2, 3]]
# for i in range(50):
#     count = randint(1, 16)
#     data = [randint(0, 255) for i in range(count)]
#     assert byte_to_list(gen_var_send_test(data)) == [data]

# print("Server Test Passed ...")

# --- incomplete data test
assert byte_to_list(bytes([254])) == []
assert byte_to_list(bytes([])) == []
assert byte_to_list(bytes([255, 195, 1, 2, 3, 199])) == [] # checksum mismatch
assert byte_to_list(bytes([255, 195])) == [] # segmented data
assert byte_to_list(bytes([1, 2, 3, 200])) == [[1, 2, 3]]
assert byte_to_list(bytes([255, 195, 2, 2, 3])) == []
assert byte_to_list(bytes([201])) == [[2, 2, 3]]
assert byte_to_list(bytes([255])) == []
assert byte_to_list(bytes([195])) == []
assert byte_to_list(bytes([2])) == []
assert byte_to_list(bytes([2, 3])) == []
assert byte_to_list(bytes([201])) == [[2, 2, 3]]
assert byte_to_list(bytes([255, 64, 1, 2, 3, 200])) == [] # count byte mismatch
assert byte_to_list(bytes([255, 195, 1, 2, 3, 200] * 2)) == [[1, 2, 3]] * 2 # two packages all at once

print("Incomplete Data Test Passed ...")

print(" ")
print("All Tests Passed!")