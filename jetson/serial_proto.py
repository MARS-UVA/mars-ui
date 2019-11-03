import socket

def var_len_proto_send(data: list):
	cs = len(data) | 192
	seq = [255, cs] + data
	seq += [sum(seq) % 256]
	return bytes(seq)

prev = []
def var_len_proto_recv_old(data: bytes):
	global prev
	print("starting with data ", list(data))
	
	seq = []
	if len(data) > 3 and data[0] == 255:
		count = data[1] & 0b00111111
		for i in range(count):
			seq.append(data[i+2])
		
		#print(len(seq) | 192)
		if (len(seq) | 192) == data[1] and (sum(data[:-1]) % 256) == data[-1]:
			prev = [] # got a complete message, so forget old messages
			return [seq]
		else: 
			return []
	
	#return []
	else:
		
		if len(prev) == 0: # previous message is useless
			#print("discarding cache...")
			prev = data
			return []

		else:

			#newdata = list(data) + list(prev)
			newdata = list(prev) + list(data)
			#if not 255 in newdata:
			if newdata[0] != 255:
				return []

			if 255 in list(data):
				print("data has a header")
				prev = []
				return []

			#print("Failed first condition, here's newdata:", newdata)

			#prev = data
			ret = var_len_proto_recv(bytes(newdata))
			prev = []
			#ret = var_len_proto_recv(list(prev)+list(data))
			#return []
			#return var_len_proto_recv(bytes(newdata))
			return ret



def var_len_proto_recv(data: list):
	if 255 in data:
		start = index(data, 255)


def process_data(data: list):
	pass


print( var_len_proto_recv(bytes([255])) )
print("next")
assert var_len_proto_recv(bytes([255, 195])) == [] # segmented data
assert var_len_proto_recv(bytes([1, 2, 3, 200])) == [[1, 2, 3]]


#print( var_len_proto_recv(bytes([255, 195, 1, 2, 3, 200])) )

#print(list( var_len_proto_send([1,2,3]) ))
#print(var_len_proto_recv( var_len_proto_send([1,2,3]) ))

#print( var_len_proto_recv(bytes([255, 195, 1, 2, 3, 200])) )
#print( var_len_proto_recv(bytes([255, 195, 1, 2, 3, 199])) )