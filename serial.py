# -*- coding: utf-8 -*-

# Bibliotheken laden
from machine import UART
import time
import json

# Initialisierung: UART
# UART 0, TX=GPIO0 (Pin 1), RX=GPIO1 (Pin 2)
# UART 1, TX=GPIO4 (Pin 6), RX=GPIO5 (Pin 7)
uart = UART(1, 57600)
#uart.init(57600, bits=8, parity=None, stop=1, tx=10, rx=9)
uart.init(57600, bits=8, parity=None, stop=1, timeout=300)

#print(uart)
count = {}
json_data = {}
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
    returnstring = None
    raw_list = []
    data = {}
    while not uart.any():
        time.sleep(0.0001)
    returnstring = myconv(uart.readline())
    raw_list = returnstring.split(b';')
    #print(len(raw_list))
    if len(raw_list) == 6:
      try:
        data['sensor'] = raw_list[0][1:].decode()
      except UnicodeError as err:
        print('Fehler bei folgendem String:')
        print(raw_list[0][1:])
        print(err)
      data['value'] = raw_list[1].decode()
      data['id'] = raw_list[2].decode()
      data['factor'] = raw_list[3].decode()
      data['unit'] = raw_list[4].decode()
    return (data)


while True:

  data = read_line()
  #print(data)

  if 'id' in data.keys():
    if data['id'] not in count:
      count[data['id']] = 0
    count[data['id']] += 1
    json_data[data['id']] = {
        'sensor': data['sensor'],
        'unit': data['unit'],
        'factor': data['factor'],
        'count': count[data['id']]
    }
    if count[data['id']] == 3:
      break

print(json.dumps(json_data, separators=None))

    