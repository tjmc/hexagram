import hexagram
import json
from datetime import datetime
from bitarray import bitarray
from bitarray.util import ba2hex

def go():
  with open('../today/burst_bits.csv', 'r') as f:
    for line in f.readlines():
      sp = line.split(',')
      d = sp[0]
      sp = ''.join(sp[4:])
      if len(sp) <= 10:
        continue

      try:
        bits = bitarray(sp)
      except:
        continue 
      packet = hexagram.go(bits)
      if packet:
        packet['time'] = d
        print(json.dumps(packet))
      else:
        print(d)
  return

if __name__ == '__main__':
  go()
