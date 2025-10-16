import time
import board
import adafruit_dht

import os
os.environ.setdefault("GPIOZERO_PIN_FACTORY", "lgpio")

# tenhle řádek změň:
dht_sensor = adafruit_dht.DHT11(board.D4)   # místo DHT22

while True:
    try:
        t = dht_sensor.temperature
        h = dht_sensor.humidity
        print(f"Teplota: {t}°C | Vlhkost: {h}%")
    except Exception as e:
        print("Chyba čtení:", e)
    time.sleep(2)
