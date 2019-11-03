# Ethan Hanover 11/3/2019

import socket

def var_len_proto_send(data: list):
	cs = len(data) | 192
	seq = [255, cs] + data
	seq += [sum(seq) % 256]
	return bytes(seq)

#prev = []
def var_len_proto_recv(data: bytes):
	#print("starting with data ", list(data))
	#global prev
	
	seq = []
	if len(data) > 3 and data[0] == 255:
		count = data[1] & 0b00111111
		for i in range(count):
			seq.append(data[i+2])
		
		#print(len(seq) | 192)
		if (len(seq) | 192) == data[1]:
			#print(data[-1])
			#print(sum(data[:-1]) % 256)
			if (sum(data[:-1]) % 256) == data[-1]:
				#prev = data
				return [seq]
	
	return []
	# else:
	# 	#print(list(prev)+list(data))
	# 	ret = var_len_proto_recv(list(prev)+list(data))
	# 	prev = data
	#	#return ret
	
	
# BREAKS WITH SEGMENTED DATA: 
#assert var_len_proto_recv(bytes([255, 195])) == [] # segmented data
#assert var_len_proto_recv(bytes([1, 2, 3, 200])) == [[1, 2, 3]]


#print( var_len_proto_recv(bytes([255, 195, 1, 2, 3, 200])) )

#print(list( var_len_proto_send([1,2,3]) ))
#print(var_len_proto_recv( var_len_proto_send([1,2,3]) ))

#print( var_len_proto_recv(bytes([255, 195, 1, 2, 3, 200])) )
#print( var_len_proto_recv(bytes([255, 195, 1, 2, 3, 199])) )