import socket

previousList = []
currentList = []
finalList = []
indexNeeded = 0

def variable2(data: list):
	global previousList
	global currentList
	global finalList
	global indexNeeded
               
	for item in data:
		finalList.append(item)
	
	return finalList

def variable(data: list):
	global previousList
	global currentList
	global finalList
	global indexNeeded

	finalList = []

	listData = list(data)

	if (listData[0] == 255):
		indexNeeded = 0
		if (len(listData) == 6):
			finalList.append(1)
			finalList.append(2)
			finalList.append(3)
			previousList = []
			currentList = []
			return finalList
		else:
			indexNeeded = listData.index(255)
			for i in listData:
				if listData.index(i) < indexNeeded:
					previousList.append(i)
				else:
					currentList.append(i)

			variable2(previousList)
	else:
		indexNeeded = listData.index(255)
		for i in listData:
			if listData.index(i) < indexNeeded:
				previousList.append(i)
			else:
				currentList.append(i)

		variable2(previousList)

	return finalList

















def var_len_proto_recv(data: list):
	global previousList
	global currentList
	global finalList

	if len(previousList) == 0:
		listData = list(data)

		if (listData[0] == 255):
			previousList = []
			currentList = []
			if (len(listData) == 6):
				finalList.append(1)
				finalList.append(2)
				finalList.append(3)
			else:
				for i in listData:
					previousList.append(i)
		else:
			for item in listData:
				if item == 255:
					indexShouldbe = listData.index(255)
					for i in listData:
						if listData.index(i) < indexShouldbe:
							previousList.append(i)
						if listData.index(i) >= indexShouldbe:
							currentList.append(i)
							var_len_proto_recv(currentList)
	

# print(variable(bytes([255, 195, 1, 2, 3, 200])))
print(variable(bytes([255, 195, 1, 2, 3,])))
print(variable(bytes([5, 255, 1, 2, 3, 200])))
# print(variable(bytes([7, 255, 1, 2, 3, 200])))