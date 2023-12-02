# Complete project details at https://RandomNerdTutorials.com

try:
  import usocket as socket
except:
  import socket

from time import sleep
from machine import Pin
import onewire, ds18x20

import network

import esp
esp.osdebug(None)

import gc
gc.collect()

ds_pin = Pin(4)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

ssid = 'SSID'
password = 'ein passwort'

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())
def read_ds_sensor():
  roms = ds_sensor.scan()
  print('Found DS devices: ', roms)
  print('Temperatures: ')
  ds_sensor.convert_temp()
  allTemps = []
  for rom in roms:
    temp = ds_sensor.read_temp(rom)
    if isinstance(temp, float):
      msg = round(temp, 2)
      print(temp, end=' ')
      print('Valid temperature from ', rom)
      allTemps.append(msg)
  return allTemps

def web_page():
  temps = read_ds_sensor()
  html1 = """<!DOCTYPE HTML><html><head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
  <style> html { font-family: Arial; display: inline-block; margin: 0px auto; text-align: center; }
    h2 { font-size: 3.0rem; } p { font-size: 3.0rem; } .units { font-size: 1.2rem; }
    .ds-labels{ font-size: 1.5rem; vertical-align:middle; padding-bottom: 15px; }
  </style></head><body><h2>ESP with DS18B20</h2>"""

  thtml=''
  i = 1
  for t in temps:
    thtml = thtml + """
    <p><i class="fas fa-thermometer-half" style="color:#159e8a;"></i>
        <span class="ds-labels">Temperature """ + str(i) + """</span>
        <span id="temperature">""" + str(t) + """</span>
        <sup class="units">&deg;C</sup>
    </p>
    """
    i += 1

  html2 = """</body></html>"""

  return html1 + thtml + html2

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
  try:
    if gc.mem_free() < 102000:
      gc.collect()
    conn, addr = s.accept()
    conn.settimeout(3.0)
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    conn.settimeout(None)
    request = str(request)
    print('Content = %s' % request)
    response = web_page()
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()
  except OSError as e:
    conn.close()
    print('Connection closed')
