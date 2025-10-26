from flask import Flask
import adafruit_dht
import board
import time

dhtDevice = adafruit_dht.DHT11(board.D4)

app = Flask(__name__)


@app.route("/")
def home():
    return "Welcome to the Dashboard!"


if __name__ == "__main__":
    app.run(debug=True)

    temperature_c = dhtDevice.temperature
    humidity = dhtDevice.humidity
    print(f"Temp: {temperature_c:.1f} C    Humidity: {humidity}% ")
    time.sleep(2.0)
