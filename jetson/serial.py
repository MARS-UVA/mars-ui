finalList = []
currentList = []
previousList = []
indexOfNewData = 6
dataLength = 0
placeholder = []

def list_to_byte(data: list):
    '''
    @param: a list containing integers
    @returns: a list with the byte format of the integers
    '''
	cs = len(data) | 192       
	seq = [255, cs] + data
	seq += [sum(seq) % 256]
	return bytes(seq)

def byte_to_list(byteInput: list):
    '''
    @param: A list of containing numbers in byte format
    @return: A list with specific values.
    '''
    global finalList        # A global final list
    global currentList      # A global current list
    global previousList     # A global previous list
    global indexOfNewData       # A global variable for index

    data = list(byteInput)      # Changes the byte input to integers
    currentList = []        # Resets the current list. 
    finalList = []      # Resets the final list

    if (len(data) == 0):        # If the length of the data is 0
        previousList = []       # Reset the previous list 
        return finalList        # Return whatever is in final list

    if (len(data) > 6):     # If the length of the data is more than 6
        dataLength = 0      # Reset the data length to 0 initially
        dataLength = int(len(data)/6)       # Set the data length to be the length of the data found as a multiple of 6
        currentList = data[0:6]     # Take the first 6 values in the list
        placeholder = byte_to_list(currentList)     # Run the function specified with that specific list
        return placeholder * dataLength     # Return the list found with the multiple in datalength

    elif (len(data) == 6):      # If the length of the data is 6
        if (data[0] == 255):        # Check the first item, if the first item is 255
            
            total = 0       # Set total to be 0
            checkSum = data[5]      # Find the checksum value in the overall list

            for item in data:       # For every item in the data list
                if item != checkSum:        # If the item is not the checksum value
                    total += item       # Add the value to the total value

            total = total % 256     # Reset total to be the value of the addition modulus 256
            
            if total == checkSum:       # If the total value is equal to checksum
                finalList.append(data[2:5])     # Append the indexes specified to the final list

            previousList = []       # Reset the previous list. 
        else:
            check_for_incomplete_data(data)     # Calls the function specified with an argument of the given data
    else:
        check_for_incomplete_data(data)     # Calls the function with an argument of the data

    if (len(previousList) == 6):        # Checks if the length of the previous list is 6
        byte_to_list(previousList)      # If it is, it calls the function on the previous list
        currentList = []        # Resets the current list 

    return list(finalList)      # Returns the values in the final list

def check_for_incomplete_data(input2: list):
    '''
    @param: A list of containing numbers in byte format
    @return: A list with specific values.
    '''
    global finalList        # A global final list
    global currentList      # A global current list
    global previousList     # A global previous list
    global indexOfNewData       # A global variable for index

    for item in input2:     # Checks each item in the list 
        if (item == 255):       # If the item is the specified value
            indexOfNewData = input2.index(255)      # The index of said value is saved
            break       # The process stops. 
        else:       # If the item is not the specified value
            indexOfNewData = 6      # Set the index to be a random value 6 or above

    for byte in input2:     # Checks each byte in the input
        if indexOfNewData == 0:     # If the index of the new data is 0 (Checks if the value 255 is in the first index)
            previousList.append(byte)       # Append the byte to the previous list
        else:       # If the condition in the if statement fails
            indexOfByte = input2.index(byte)        # Find the index of the byte
            if indexOfByte < indexOfNewData:        # If the index of the byte is less than the index of the 255 value
                previousList.append(byte)       # Append it to the previous list