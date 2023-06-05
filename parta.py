import time
import random
import binascii
from socket import *

serverName = '169.237.229.88'
serverPort = 53

clientSocket = socket(AF_INET, SOCK_DGRAM)

payloadbuf = bytearray()
# Header
# payloadbuf += '1010000100100011' # 16 bit ID
# Flags
headerbuf = ''
headerbuf += '0' # QR indicating query
headerbuf += '0000' # OPCODE to specify what kind of query
headerbuf += '0' # TC to indicate not truncated
headerbuf += '1' # RD to indicate recursion is desired
headerbuf += '0' # Z reserved for future use
headerbuf += '00000000' # rest are 0's
headerbuf += '0000000000000001' # Number of Questions
headerbuf += '0000000000000000' # Number of Answers
headerbuf += '0000000000000000' # Number of Authority Records
headerbuf += '0000000000000000' # Number of Additional Records

headerbuf = headerbuf.encode('ascii')
print(headerbuf)

# Question (Formatted in ASCII)
questionbuf = ''
questionbuf += '03' # tmz has length 3
questionbuf += '74' # ascii for t
questionbuf += '6D' # ascii for m
questionbuf += '7A' # ascii for z
questionbuf += '00' # zero byte to end QNAME
questionbuf += '0001' # QTYPE
questionbuf += '0001' # QCLASS
# print(questionbuf)
# print(f'question in binary is {binascii.unhexlify(questionbuf)}')
questionbuf = binascii.unhexlify(questionbuf)

# payloadbuf += headerbuf
# payloadbuf += questionbuf
payloadbuf.append(headerbuf)
print(payloadbuf)
