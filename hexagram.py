#!/usr/bin/env python

from bitarray import bitarray
from bitarray.util import ba2hex
from bitarray.util import hex2ba
from bitarray.util import ba2int 
from bitarray.util import make_endian 
import binascii

TEST_DATA = '111111110101010101010101010101011001100110011001100110011010010101011010101010100101011001101010100101010110101001011010010110011001100110101010100110010110011010011001101010010110011001010110010110011001011010101001010101100110011010011001011010011001011001100110101010000'

PREFIX = bitarray('1111110')

def decode_manchester_diff(bits):
  error = 0

  start_idx = bits.find(PREFIX)
  bits = bits[start_idx + len(PREFIX) - 1:]
  manchester_bits = bitarray()

  for i,j in next_pair(bits):
    # manchester 1 (ge) vs 2 (ieee) does not matter since Differential Manchester is used 
    if not i and j: 
      manchester_bits.append(1)
    elif i and not j:
      manchester_bits.append(0)
    else:
      error += 1

  for i in range(0, 4 - (len(manchester_bits) % 4)):
    manchester_bits.append(0)

  # decoded Differential Manchester 
  manchester_diff_bits = bitarray()

  for i in range(0, len(manchester_bits)):
    if manchester_bits[i] != manchester_bits[i-1]:
      manchester_diff_bits.append(1)
    else:
      manchester_diff_bits.append(0)
  
  if len(manchester_diff_bits) % 4 != 0:
    manchester_diff_bits
  return manchester_diff_bits 

PACKET_PREFIX = '00fffa'

def flip_and_little(hex_data):
  return make_endian((~hex2ba(hex_data)), 'little')

# figure out 00fffa1a0e4071b8d197e701a5 (length 26)
def valid_packet(hex_data):
  source_addr = ba2int(flip_and_little(hex_data[8:14]))
  flags = flip_and_little(hex_data[14:16]).to01()
  if len(hex_data) < 22:
    r = {
      'source_addr': source_addr,
      'meter1': None,
      'flags': flags,
      'meter2': None,

    }
    return r
  #BCD
  meter1 = ba2hex(flip_and_little((hex_data[16:22])))[::-1]
  r = {
    'source_addr': source_addr,
    'meter1': meter1,
    'meter2': None,
    'flags': flags,
  }
  if len(hex_data) == 32:
    r['meter2'] = ba2hex(flip_and_little(hex_data[22:28]))[::-1]

  return r

INITIAL_VALUE = 0xf492

def valid_crc(hex_bytes):
  msg = hex_bytes[:-4]
  expected_crc = int(hex_bytes[-4:], 16)
  print(msg)
  try:
    crc = binascii.crc_hqx(bytes.fromhex(msg), INITIAL_VALUE)
  except:
    return False
    
  if expected_crc == crc:
    return True
  #sometimes off by one. Looking into why this is happening (manchester decode issue or packet capture cuts off too early)
  if expected_crc - 1 == crc or expected_crc + 1 == crc:
    return True

  return False 

def process_packet(hex_bytes):
  index = hex_bytes.find(PACKET_PREFIX)
  if index == -1:
    return None
  hex_bytes = hex_bytes[index:]
  
  length = int(hex_bytes[6:8],16)
  if len(hex_bytes) > length:
    #trim extra bytes 
    hex_bytes = hex_bytes[:length]
  if len(hex_bytes) == length and valid_crc(hex_bytes):
    packet = valid_packet(hex_bytes)
    packet['invalid_crc'] = False 
    packet['invalid_length'] = False 
    return packet 
  elif len(hex_bytes) == length:
    packet = valid_packet(hex_bytes)
    packet['invalid_crc'] = True
    packet['invalid_length'] = False 
    return packet 
  elif len(hex_bytes) >= length - 4:
    #try anyway
    packet = valid_packet(hex_bytes)
    packet['invalid_crc'] = True
    packet['invalid_length'] = True 
    return packet 

def go(bits):
  manchester_diff_bits = decode_manchester_diff(bits) 
  decoded = process_packet(ba2hex(manchester_diff_bits))
  return decoded

def next_pair(it):
  it = iter(it)
  while True:
    try:
      yield next(it), next(it)
    except StopIteration:
      break

if __name__ == '__main__':
  bits = bitarray(TEST_DATA)
  print(go(bits))
