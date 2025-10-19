import sqlite3
from time import sleep
import board
import adafruit_dht

# data = [
#     {"temperature": 22.5, "humidity": 45.0},
#     {"temperature": 23.0, "humidity": 50.0},
#     {"temperature": 21.5, "humidity": 55.0}     
#     ]

result = []

def read_sensor():
    
    dhtDevice = adafruit_dht.DHT11(board.D4)
    temperature_c = dhtDevice.temperature
    humidity = dhtDevice.humidity

    counter = 6

    for i in range(5): 
        data = {"temperature": temperature_c, "humidity": humidity}
        result.append(data)
        counter -= 1
        print(f"Zbývá :{counter} měření")
        sleep(1)

    dhtDevice.exit()

    return result

def insert_data(sensor_data):
    with sqlite3.connect('DU_lekce_4/sensor.db') as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            timastamp DARTETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            humidity REAL)
        ''')

        for entry in sensor_data:
            conn.execute('''
            INSERT INTO sensor_data (temperature, humidity) VALUES (?, ?)
            ''', (entry["temperature"], entry["humidity"]))
            sleep(1)
    
        conn.commit()

def fetch_data():
    with sqlite3.connect('DU_lekce_4/sensor.db') as conn:
        cursor = conn.execute('SELECT * FROM sensor_data ORDER BY id DESC lIMIT 5')
        rows = cursor.fetchall()
        for row in rows:
            print(row)

def prumer_hodnot():
    with sqlite3.connect('DU_lekce_4/sensor.db') as conn:
        cursor = conn.execute('SELECT AVG(temperature), AVG(humidity) FROM sensor_data')
        avg_temp, avg_hum = cursor.fetchone()
        print(f"Průměrná teplota: {avg_temp:.2f} C, Průměrná vlhkost: {avg_hum:.2f} %")

if __name__ == "__main__":

    data = read_sensor()
    insert_data(data)
    fetch_data()
    prumer_hodnot()

