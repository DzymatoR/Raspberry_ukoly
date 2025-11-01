from flask import Flask, render_template
import time
import adafruit_dht
import board
import sqlite3
from time import sleep

# Inicializace Flask aplikace
app = Flask(__name__)

# Na RPi4/5 je často nutné use_pulseio=False
dht = adafruit_dht.DHT11(board.D4, use_pulseio=False)

# Cesta k databázi
DB_PATH = "DU_lekce_8/sensor_data.db"


def uloz_data_do_SQL(sensor_data):

    # Připojení k databázi (vytvoří soubor, pokud neexistuje)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            humidity REAL)
        """
        )

        # Vloží každý záznam postupně
        for entry in sensor_data:
            conn.execute(
                """
            INSERT INTO sensor_data (temperature, humidity) VALUES (?, ?)
            """,
                (entry["temperature"], entry["humidity"]),
            )

        conn.commit()


def fetch_data():

    # Načte poslední záznam z tabulky sensor_data.
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT temperature, humidity FROM sensor_data ORDER BY id DESC lIMIT 1"
        )
        rows = cursor.fetchall()
        if rows:
            return {"temperature": rows[0][0], "humidity": rows[0][1]}
        else:
            print("Žádná data v databázi.")
            return []


def read_dht():
    try:
        # Senzor potřebuje čas na inicializaci
        time.sleep(2)
        t = dht.temperature
        h = dht.humidity
        return {"temperature": float(t), "humidity": float(h)}

    except RuntimeError as error:
        print(f"Chyba při čtení senzoru: {error.args[0]}")
        return {"temperature": None, "humidity": None}


@app.get("/api/data")
def api_data():

    uloz_data_do_SQL([read_dht()])  # Uložení dat přímo po načtení ze senzoru

    return fetch_data()  # Vrací poslední data z databáze


@app.get("/")
def home():
    data = read_dht()  # Načtení dat ze senzoru
    uloz_data_do_SQL([data])  # Uložení dat do databáze
    databaze_data = fetch_data()  # Načtení posledních dat z databáze

    # Renderování šablony s daty
    return render_template(
        "index.html",
        temperature=databaze_data["temperature"],
        humidity=databaze_data["humidity"],
    )


# Spuštění aplikace
if __name__ == "__main__":
    app.run(debug=True, port=1234)
