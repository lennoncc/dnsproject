import binascii
import sys
from socket import *
url = sys.argv[1]

serverName = '198.41.0.4'
serverPort = 53

clientSocket = socket(AF_INET, SOCK_DGRAM)

# Header
# 0 QR indicating query
# 0000 OPCODE to specify what kind of query
# 0 AA not applicable, set to 0
# 0 TC to indicate not truncated
# 1 RD to indicate recursion is desired
# 0 RA not applicable, set to 0
# 000 Z reserved for future use
# 0000 RCODE
# Above results in 0000000100000000, which is 0100 in hex.
payloadbuf = ''
payloadbuf += 'A123' # 16 bit ID in Hex
payloadbuf += '0100' # Flags as seen above
payloadbuf += '0001' # Number of Questions
payloadbuf += '0000' # Number of Answers
payloadbuf += '0000' # Number of Authority Records
payloadbuf += '0000' # Number of Additional Records

# Question (Formatted in ASCII)
questionbuf = ''
# Split URL into 2
spliturl = url.split('.')
# If the part of the url before period has less than 15 characters, add a 0 for formatting
if len(str(hex(len(spliturl[0])))) < 4:
  questionbuf += '0'
# Start with length of first part of URL
questionbuf += str(hex(len(spliturl[0])))[2:]
# Go through and add each letter of URL in hex format
for i in spliturl[0]:
  questionbuf += format(ord(i), "x")
# If the part of the url after period is less than 15 characters, add 0 for formatting
if len(str(hex(len(spliturl[1])))) < 4:
  questionbuf += '0'
questionbuf += str(hex(len(spliturl[1])))[2:]
# Go through and add each letter of URL in hex format
for i in spliturl[1]:
  questionbuf += format(ord(i), "x")
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

# print(f'in hex: {binascii.hexlify(message).decode("utf-8")}')
decmessage = binascii.hexlify(message).decode("utf-8")
responseid = decmessage[0:4] # Parse through id
# print(f'id is {responseid}')
# Header
flags = decmessage[4:8]
# print(f'flags are {flags}')
qdcount = decmessage[8:12]
# print(f'qdcount is {qdcount}')
ancount = decmessage[12:16]
# print(f'ancount is {ancount}')
nscount = decmessage[16:20]
print(f'nscount is {int(nscount, 16)}')
arcount = decmessage[20:24]
print(f'arcount is {int(arcount, 16)}')
# Question
print(f'question should be: {decmessage[24:24+questionLen]}')
startofRR = 24 + questionLen

ipArray = []
# Resource Record
def decodeResourceRecord(decmessage, startofRR):
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
  print(f'responseRDLength: {int(responseRDLength, 16)}')
  responseRDData = decmessage[startofRR+24:startofRR+24+(2*int(responseRDLength, 16))]
  print(f'responseRDData: {responseRDData}')
  ipaddr = ''
  if int(responseType, 16) == 2:
    for i in range(0, len(responseRDData),2):
      ipaddr += bytes.fromhex(responseRDData[i:i+2]).decode()
      # ipaddr += '.'
  else:
    for i in range(0, len(responseRDData),2):
      ipaddr += str(int(responseRDData[i:i+2], 16))
      ipaddr += '.'

  print(ipaddr[0:len(ipaddr)-1])
  ipArray.append(ipaddr[0:len(ipaddr)-1])
  lengthofRR = startofRR+24+(2*int(responseRDLength, 16)) - startofRR
  print(lengthofRR)
  return lengthofRR


for i in range(int(nscount, 16)):
  lengthofRR = decodeResourceRecord(decmessage, startofRR)
  # Start of RR Won't always be 32, change to be dynamic
  startofRR += lengthofRR

print(f'Domain Name: {url}')

for i in range(len(ipArray)):
  print(f'IP Address {i+1}: {ipArray[i]}')

