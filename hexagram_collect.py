import time
import zmq
import paho.mqtt.publish as publish
import settings
import hexagram
from influxdb import InfluxDBClient
from bitarray import bitarray
from bitarray.util import vl_decode

def send_influxdb(meter_id, meter_num, usage, timestamp):
 client = InfluxDBClient(INFLUX_HOST, INFLUX_PORT, INFLUX_USER, INFLUX_PASSWORD, INFLUX_BUCKET)
 data = []
 data.append(f"water,meter_id={meter_id},meter_num={meter_num} usage={usage} {timestamp}")
 client.write_points(data, database='aep', time_precision="s", protocol="line")


def process(message):
  bits = bitarray()
  bits.pack(message)
  decoded = hexagram.go(bits)
  print(decoded)
  if decoded is None:
    return
  if decoded['invalid_crc']:
    print(decoded)
    return
  s_adr = decoded['source_addr']
  if decoded['meter1'] != None:
    TOPIC = f"rtlwater/{s_adr}/water_meter1"
    publish.single(TOPIC, payload=decoded['meter1'], qos=1, hostname=settings.MQTT_HOST, port=settings.MQTT_PORT)
    send_influxdb(s_adr, "1", decoded['meter1'], int(time.time()))
    if decoded['meter2'] != None:
      TOPIC = f"rtlwater/{s_adr}/water_meter2"
      publish.single(TOPIC, payload=decoded['meter2'], qos=1, hostname=settings.MQTT_HOST, port=settings.MQTT_PORT)
      send_influxdb(s_adr, "2", decoded['meter2'], int(time.time()))

if __name__ == '__main__':
  context = zmq.Context()
  socket = context.socket(zmq.SUB)
  socket.connect("tcp://127.0.0.1:5555")
  socket.setsockopt(zmq.SUBSCRIBE, b'') # subscribe to topic of all (needed or else it won't work)
  f = open('save.txt', 'ab')
  while True:
    #  Wait for next request from client
    message = socket.recv()
    print("Received request: %s" % message)
    f.write(message)
    process(message)

    #  Do some 'work'
    time.sleep(1)
