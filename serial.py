# -*- coding: utf-8 -*-

# Bibliotheken laden
from machine import UART
import time
import json
import _thread

# Initialisierung: UART
uart = UART(1, 57600)
uart.init(57600, bits=8, parity=None, stop=1, timeout=10)

print('Warten auf Daten der Gegenstelle')

def myconv(s):
  # Workaround for Micropython UTF-8 limitation
  # Convert single LATIN-1 chars to UTF-8
  o = b""
  for b in s:  
    if b == 0xFC:
        o += bytes(chr(252), "utf-8")
    elif b == 0xE4:
        o += bytes(chr(228), "utf-8")
    elif b == 0xB0:
        o += bytes(chr(176), "utf-8")
    else:
        o += bytes(chr(b), "utf-8")
  #print(o)
  return o

def read_line():
    count = 0
    returnstring = None
    raw_list = []
    data = {}
    while not uart.any():
        time.sleep(0.001)
        count +=1
        #print("Stuck %d" % count)
        if count > 1000:
            return {
                'id': '99',
                'factor': 1,
                'value': "no serial data",
                'sensor': 'Fehler',
                'unit': " "
                }
    returnstring = myconv(uart.readline())
    raw_list = returnstring.split(b';')
    #print(returnstring)
    #print(len(raw_list))
    if len(raw_list) == 6:
      data['sensor'] = raw_list[0].decode()
      data['value'] = raw_list[1].decode()
      data['id'] = raw_list[2].decode()
      data['factor'] = raw_list[3].decode()
      data['unit'] = raw_list[4].decode()
    return (data)


def get_data():
  count = {}
  json_data = {}
  while True:
    try:
      data = read_line()
    except Exception as err:
      print(err)

    #print(data)

    if 'id' in data.keys():
      if data['id'] not in count:
        count[data['id']] = 0
      count[data['id']] += 1
      factor = int(data['factor'])
      try:
          value = float(data['value'])
          total = value / factor
      except ValueError:
          value = str(data['value'])
          total = value
      json_data[data['id']] = {
          'sensor': data['sensor'].strip(),
          'unit': data['unit'],
          'factor': factor,
          'value': value,
          'total': total
      }
      if count[data['id']] == 3:
          break
  return json_data

def get_json():
    # Output sample data
    with open('sample_data.json') as f:
        d = json.load(f)
    return d

# For single use
print(json.dumps(get_data(), separators=None))
