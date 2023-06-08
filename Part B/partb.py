import binascii
import sys
from socket import *
# Save url from command line
url = sys.argv[1]

# Set up socket
serverName = '198.41.0.4'
serverPort = 53
clientSocket = socket(AF_INET, SOCK_DGRAM)
ipArray = []
ancount, nscount, arcount = '', '', ''


# Building Header
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

# Once DNS Message has been built, send the DNS Message first to Root Server

clientSocket.sendto(binascii.unhexlify(payloadbuf), (serverName, serverPort))
try:
  message, serverAddress = clientSocket.recvfrom(4096)
finally:
  clientSocket.close()

decmessage = binascii.hexlify(message).decode("utf-8")

def decodeHeader(decmessage):
  # Header
  responseid = decmessage[0:4] # Parse through id
  # print(f'id is {responseid}')
  flags = decmessage[4:8]
  # print(f'flags are {flags}')
  qdcount = decmessage[8:12]
  # print(f'qdcount is {qdcount}')
  ancount = decmessage[12:16]
  # print(f'ancount is {ancount}')
  nscount = decmessage[16:20]
  # print(f'nscount is {int(nscount, 16)}')
  arcount = decmessage[20:24]
  # print(f'arcount is {int(arcount, 16)}')
  # Question
  # print(f'question should be: {decmessage[24:24+questionLen]}')
  return ancount, nscount, arcount

# No need to keep track of question as it will always be the same
startofRR = 24 + questionLen # Keep track of index where Resource Record Starts

# Resource Record
def decodeResourceRecord(decmessage, startofRR):
  # print(f'full RR: {decmessage[startofRR:len(decmessage)]}')
  responseName = decmessage[startofRR:startofRR+4]
  # print(f'responseName: {responseName}')
  responseType = decmessage[startofRR+4:startofRR+8]
  # print(f'responseType: {responseType}')
  responseClass = decmessage[startofRR+8:startofRR+12]
  # print(f'responseClass: {responseClass}')
  responseTTL = decmessage[startofRR+12:startofRR+20]
  # print(f'responseTTL: {responseTTL}')
  responseRDLength = decmessage[startofRR+20:startofRR+24]
  # print(f'responseRDLength: {int(responseRDLength, 16)}')
  responseRDData = decmessage[startofRR+24:startofRR+24+(2*int(responseRDLength, 16))]
  # print(f'responseRDData: {responseRDData}')
  ipaddr = ''
  if int(responseType, 16) == 1:
    for i in range(0, len(responseRDData),2):
      ipaddr += str(int(responseRDData[i:i+2], 16))
      ipaddr += '.'
    ipArray.append(ipaddr[0:len(ipaddr)-1])

  # print(ipaddr[0:len(ipaddr)-1])
  lengthofRR = startofRR+24+(2*int(responseRDLength, 16)) - startofRR
  # print(lengthofRR)
  return lengthofRR

ancount,nscount,arcount = decodeHeader(decmessage)

# Iterate through RRs until reach Additional Records for IP of TLD DNS Server
for i in range(int(nscount, 16)):
  lengthofRR = decodeResourceRecord(decmessage, startofRR)
  startofRR += lengthofRR

# Keep count of all IPs for TLD DNS Server(s)
for i in range(int(arcount, 16)):
  lengthofRR = decodeResourceRecord(decmessage, startofRR)
  startofRR += lengthofRR

print(f'Domain Name: {url}')

print('TLD Server IP Addresses:')
for i in range(len(ipArray)):
  print(f'IP Address {i+1}: {ipArray[i]}')


# Connect to TLD DNS Server to find Authoritative DNS Server IP
serverName = ipArray[0]
serverPort = 53
clientSocket = socket(AF_INET, SOCK_DGRAM)
ipArray = [] # Reset IP Addresses to keep track of Authoritative DNS Server IP Addresses
startofRR = 24 + questionLen # Reset startofRR for new Resource Records

clientSocket.sendto(binascii.unhexlify(payloadbuf), (serverName, serverPort))
try:
  message, serverAddress = clientSocket.recvfrom(4096)
finally:
  clientSocket.close()

decmessage = binascii.hexlify(message).decode("utf-8")
ancount,nscount,arcount = decodeHeader(decmessage)

# Iterate through RRs until reach Additional Records for IP of TLD DNS Server
for i in range(int(nscount, 16)):
  lengthofRR = decodeResourceRecord(decmessage, startofRR)
  # Start of RR Won't always be 32, change to be dynamic
  startofRR += lengthofRR

# Keep count of all IPs for TLD DNS Server(s)
for i in range(int(arcount, 16)):
  lengthofRR = decodeResourceRecord(decmessage, startofRR)
  # Start of RR Won't always be 32, change to be dynamic
  startofRR += lengthofRR

print('Authoritative DNS Server IP Addresses:')
for i in range(len(ipArray)):
  print(f'IP Address {i+1}: {ipArray[i]}')


# Connect to Authoritative DNS Server to find resolved IP Address for A record
serverName = ipArray[0]
serverPort = 53
clientSocket = socket(AF_INET, SOCK_DGRAM)
ipArray = [] # Reset IP Addresses to keep track of resolved IP Addresses
startofRR = 24 + questionLen # Reset startofRR for new Resource Records

clientSocket.sendto(binascii.unhexlify(payloadbuf), (serverName, serverPort))
try:
  message, serverAddress = clientSocket.recvfrom(4096)
finally:
  clientSocket.close()

decmessage = binascii.hexlify(message).decode("utf-8")
ancount,nscount,arcoutn = decodeHeader(decmessage)

# Iterate through answers and keep track of IP Addresses
for i in range(int(ancount, 16)):
  lengthofRR = decodeResourceRecord(decmessage, startofRR)
  startofRR += lengthofRR

print('Answer IP Addresses:')
for i in range(len(ipArray)):
  print(f'IP Address {i+1}: {ipArray[i]}')