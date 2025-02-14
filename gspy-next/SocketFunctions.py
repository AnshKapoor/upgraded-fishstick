def receiveMessage(dataBuffer):
    """receive thread for receiving socket messages from client(core class)"""
    newPacket = True
    startOfPacket = 0
    dataBuffer = b''
    dataBufferLength = 0
    HEADERSIZE = 12

    dataBufferLength = len(dataBuffer)

    print("dataBuffer: " + str(dataBuffer))
    print("dataBuffer length: " + str(dataBufferLength))

    if newPacket:
        if dataBufferLength >= HEADERSIZE:
            while True:
                # Check for sync pattern
                if dataBuffer[startOfPacket:startOfPacket + 5] == b'\xc0\x1d\xc0\xff\xee':
                    print("Packet Sync pattern found!")
                    payloadLength = int.from_bytes(dataBuffer[startOfPacket + 6:startOfPacket + 9], 'big')
                    print(f"{payloadLength=}")
                    protocolVersion = int.from_bytes(dataBuffer[startOfPacket + 5:startOfPacket + 6], 'big')
                    print(f"{protocolVersion=}")
                    payloadType = int.from_bytes(dataBuffer[startOfPacket + 9:startOfPacket + 10], 'big')
                    print(f"{payloadType=}")

                    if dataBufferLength == startOfPacket + HEADERSIZE:
                        dataBuffer = b''
                        dataBufferLength = 0
                    else:
                        dataBuffer = dataBuffer[startOfPacket + HEADERSIZE:]
                        dataBufferLength = len(dataBuffer)
                    startOfPacket = 0

                    if dataBufferLength >= payloadLength:
                        payload = dataBuffer[:payloadLength]

                        print("Full payload received: " + str(payload))
                        dataBuffer = dataBuffer[payloadLength:]
                        dataBufferLength = len(dataBuffer)
                        print("dataBuffer after payload cut: " + str(dataBuffer))
                        print("-----------------------")

                        newPacket = True
                    else:
                        newPacket = False
                    break
                else:
                    print("Packet Sync pattern NOT found!")

                    startOfPacket += 1
                    # Check for dataBufferLength is bigger than HEADERSIZE + startOfPacket
                    if dataBufferLength < HEADERSIZE + startOfPacket:
                        break
        else:
            print("Packet header not completely received, waiting for more data...")
    else:
        if dataBufferLength >= payloadLength:
            payload = dataBuffer[:payloadLength]

            print("Full payload received: " + str(payload))

            dataBuffer = dataBuffer[payloadLength:]
            dataBufferLength = len(dataBuffer)
            print("dataBuffer after payload cut: " + str(dataBuffer))
            print("-----------------------")

            newPacket = True
        else:
            print("Payload not completely received, waiting for more data...")
