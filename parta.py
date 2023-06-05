import time
import random
import binascii
from socket import *

serverName = '169.237.229.88'
serverPort = 53

clientSocket = socket(AF_INET, SOCK_DGRAM)

payloadbuf = bytearray()
# Header
payloadbuf += b'1010000100100011' # 16 bit ID (A123)
payloadbuf += b'0' # QR indicating query
payloadbuf += b'0000' # OPCODE to specify what kind of query
payloadbuf += b'0' # AA not applicable, set to 0
payloadbuf += b'0' # TC to indicate not truncated
payloadbuf += b'1' # RD to indicate recursion is desired
payloadbuf += b'0' # RA not applicable, set to 0
payloadbuf += b'000' # Z reserved for future use
payloadbuf += b'0000' # rest are 0's
payloadbuf += b'0000000000000001' # Number of Questions
payloadbuf += b'0000000000000000' # Number of Answers
payloadbuf += b'0000000000000000' # Number of Authority Records
payloadbuf += b'0000000000000000' # Number of Additional Records

# Question (Formatted in ASCII)
questionbuf = ''
questionbuf += '03' # tmz has length 3
questionbuf += '74' # ascii for t
questionbuf += '6D' # ascii for m
questionbuf += '7A' # ascii for z
questionbuf += '00' # zero byte to end QNAME
questionbuf += '0001' # QTYPE
questionbuf += '0001' # QCLASS
payloadbuf += binascii.unhexlify(questionbuf)


print(payloadbuf)

clientSocket.sendto(payloadbuf, (serverName, serverPort))
# try:
#   message, serverAddress = clientSocket.recvfrom(4096)