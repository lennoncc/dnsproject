import time
import random
import binascii
from socket import *

serverName = '169.237.229.88'
serverPort = 53

clientSocket = socket(AF_INET, SOCK_DGRAM)

# payloadbuf = bytearray()
# Header
# payloadbuf += b'1010000100100011' # 16 bit ID (A123)
# 0 QR indicating query
# 0000 OPCODE to specify what kind of query
# 0 AA not applicable, set to 0
# 0 TC to indicate not truncated
# 1 RD to indicate recursion is desired
# 0 RA not applicable, set to 0
# 000 Z reserved for future use
# 0000 RCODE
# payloadbuf += b'0000000000000001' # Number of Questions
# payloadbuf += b'0000000000000000' # Number of Answers
# payloadbuf += b'0000000000000000' # Number of Authority Records
# payloadbuf += b'0000000000000000' # Number of Additional Records
payloadbuf = ''
payloadbuf += 'A123' # 16 bit ID in Hex
payloadbuf += '0100' # Flags as seen above
payloadbuf += '0001' # Number of Questions
payloadbuf += '0000' # Number of Answers
payloadbuf += '0000' # Number of Authority Records
payloadbuf += '0000' # Number of Additional Records

# Question (Formatted in ASCII)
questionbuf = ''
questionbuf += '03' # tmz has length 3
questionbuf += '74' # ascii for t
questionbuf += '6d' # ascii for m
questionbuf += '7a' # ascii for z
questionbuf += '03' # com has length 3
questionbuf += '63' # ascii for c
questionbuf += '6f' # ascii for o
questionbuf += '6d' # ascii for m
questionbuf += '00' # zero byte to end QNAME
questionbuf += '0001' # QTYPE
questionbuf += '0001' # QCLASS
questionLen = len(questionbuf)

payloadbuf += questionbuf

clientSocket.sendto(binascii.unhexlify(payloadbuf), (serverName, serverPort))
try:
  message, serverAddress = clientSocket.recvfrom(4096)
finally:
  clientSocket.close()

print(f'in hex: {binascii.hexlify(message).decode("utf-8")}')
decmessage = binascii.hexlify(message).decode("utf-8")
responseid = decmessage[0:4] # Parse through id
print(f'id is {responseid}')
# Header
flags = decmessage[4:8]
print(f'flags are {flags}')
qdcount = decmessage[8:12]
print(f'qdcount is {qdcount}')
ancount = decmessage[12:16]
print(f'ancount is {ancount}')
nscount = decmessage[16:20]
print(f'nscount is {nscount}')
arcount = decmessage[20:24]
print(f'arcount is {arcount}')
# Question
print(f'question should be: {decmessage[24:24+questionLen]}')
startofRR = 24 + questionLen
# Resource Record
print(f'full RR: {decmessage[startofRR:len(decmessage)]}')
responseName = decmessage[startofRR:startofRR+4]
print(f'responseName: {responseName}')
responseType = decmessage[startofRR+4:startofRR+8]
print(f'responseType: {responseType}')
responseClass = decmessage[startofRR+8:startofRR+12]
print(f'responseClass: {responseClass}')
responseTTL = decmessage[startofRR+12:startofRR+20]
print(f'responseTTL: {responseTTL}')
responseRDLength = decmessage[startofRR+20:startofRR+24]
print(f'responseRDLength: {responseRDLength}')
responseRDData = decmessage[startofRR+24:startofRR+24+(2*int(responseRDLength))]
print(f'responseRDData: {responseRDData}')
ipaddr = ''
for i in range(0, len(responseRDData),2):
  print(responseRDData[i:i+2])
  ipaddr += str(int(responseRDData[i:i+2], 16))
  ipaddr += '.'

print(ipaddr[0:len(ipaddr)-1])