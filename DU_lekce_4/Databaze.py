import sqlite3
from time import sleep
import board
import adafruit_dht
import csv

# Seznam výsledků měření (sbíráme více záznamů před uložením do DB)
result = []


def read_sensor():
    """
    Přečte hodnoty z DHT11 senzoru několikráte (5x) a uloží je do seznamu result.
    Vrací seznam slovníků s klíči 'temperature' a 'humidity'.
    """

    # Inicializace DHT senzoru na pinu D4
    dhtDevice = adafruit_dht.DHT11(board.D4)
    # Načtení jednorázových hodnot (může být None pokud senzor neodpoví)
    temperature_c = dhtDevice.temperature
    humidity = dhtDevice.humidity

    # Počet opakování (pouze pro výpis zbývajících měření)
    counter = 6

    # Pro účely cvičení opakujeme 5x a ukládáme stejné aktuální hodnoty
    for i in range(5):
        data = {"temperature": temperature_c, "humidity": humidity}
        result.append(data)
        counter -= 1
        print(f"Zbývá :{counter} měření")
        sleep(1)

    # Ukončí komunikaci se senzorem (u adafruit_dht některé verze vyžadují exit)
    dhtDevice.exit()

    return result


def uloz_CSV(sensor_data, filename="DU_lekce_4/sensor_data.csv"):
    """
    Uloží data (seznam slovníků) do CSV souboru.
    """
    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["temperature", "humidity"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for entry in sensor_data:
            writer.writerow(entry)


def insert_data(sensor_data):
    """
    Vloží data (seznam slovníků) do SQLite databáze.
    Pokud tabulka neexistuje, vytvoří ji.
    """
    with sqlite3.connect("DU_lekce_4/sensor.db") as conn:
        conn.execute(
            """
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            timastamp DARTETIME DEFAULT CURRENT_TIMESTAMP,
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
            sleep(1)

        conn.commit()


def fetch_data():
    """
    Načte a vytiskne posledních 5 záznamů z tabulky sensor_data.
    """
    with sqlite3.connect("DU_lekce_4/sensor.db") as conn:
        cursor = conn.execute("SELECT * FROM sensor_data ORDER BY id DESC lIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(row)


def prumer_hodnot():
    """
    Spočítá a vytiskne průměrnou teplotu a vlhkost ze všech záznamů v DB.
    """
    with sqlite3.connect("DU_lekce_4/sensor.db") as conn:
        cursor = conn.execute("SELECT AVG(temperature), AVG(humidity) FROM sensor_data")
        avg_temp, avg_hum = cursor.fetchone()
        print(f"Průměrná teplota: {avg_temp:.2f} C, Průměrná vlhkost: {avg_hum:.2f} %")


if __name__ == "__main__":

    data = read_sensor()
    insert_data(data)
    fetch_data()
    prumer_hodnot()
    uloz_CSV(data)
