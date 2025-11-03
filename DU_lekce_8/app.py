from flask import Flask, render_template, jsonify, request
import threading
import adafruit_dht
import board
import time
import sqlite3
from datetime import datetime
import gpiozero

app = Flask(__name__)

# Konfigurace databáze
DB_NAME = "DU_lekce_8/sensor_data.db"


# Na RPi4/5 je často nutné use_pulseio=False
dht = adafruit_dht.DHT11(board.D4, use_pulseio=False)
led = gpiozero.LED(15)  # LED připojená na GPIO15


# Inicializace databáze
def init_db():
    """Inicializace databáze"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS sensor_readings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  temperature REAL,
                  humidity REAL)"""
    )
    conn.commit()
    conn.close()


# Čtení dat ze senzoru DHT11
def read_dht():
    try:
        # Senzor potřebuje čas na inicializaci
        time.sleep(2)
        t = dht.temperature
        h = dht.humidity
        # return {"temperature": float(t), "humidity": float(h)}
        return t, h
    except RuntimeError as error:
        print(f"Chyba při čtení senzoru: {error.args[0]}")
        return {"temperature": None, "humidity": None}


# ukládání dat do databáze
def save_to_database():
    while True:
        try:
            temp, hum = read_dht()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute(
                "INSERT INTO sensor_readings (timestamp, temperature, humidity) VALUES (?, ?, ?)",
                (timestamp, temp, hum),
            )
            conn.commit()
            conn.close()

            print(f"Uloženo: {timestamp} - Teplota: {temp:.2f}°C, Vlhkost: {hum:.2f}%")
        except Exception as e:
            print(f"Chyba při ukládání: {e}")

        time.sleep(2)  # Čekat 2 sekundy před dalším čtením


# Načtení posledních dat z databáze
def get_latest_data():
    """Načtení posledních dat z databáze"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT timestamp, temperature, humidity FROM sensor_readings ORDER BY id DESC LIMIT 10"
    )
    rows = c.fetchall()
    conn.close()
    return rows


# Hlavní stránka
@app.get("/")
def index():
    return render_template("index.html")


# API endpoint pro získání dat
@app.get("/api/data")
def get_data():
    data = get_latest_data()
    if data:
        latest = {
            "timestamp": data[0][0],
            "temperature": round(float(data[0][1]), 1),  # Převod na float
            "humidity": round(float(data[0][2]), 1),  # Převod na float
            "history": [
                {
                    "timestamp": row[0],
                    "temperature": round(float(row[1]), 1),  # Převod na float
                    "humidity": round(float(row[2]), 1),  # Převod na float
                }
                for row in data
            ],
        }
        return jsonify(latest)
    return jsonify({"error": "Žádná data"})


@app.post("/api/led")
def control_led():
    try:
        state = request.json.get("state")
    except Exception as e:
        return jsonify({"error": str(e)}), 415

    if state == "on":
        led.on()
        return jsonify({"status": "LED zapnuta"})
    elif state == "off":
        led.off()
        return jsonify({"status": "LED vypnuta"})
    else:
        return jsonify({"error": "Neplatný stav"}), 400


if __name__ == "__main__":
    # Inicializace databáze
    init_db()

    # Spuštění vlákna pro ukládání dat
    sensor_thread = threading.Thread(target=save_to_database, daemon=True)
    sensor_thread.start()

    # Spuštění Flask aplikace
    app.run(debug=True, use_reloader=False, port=1234)
