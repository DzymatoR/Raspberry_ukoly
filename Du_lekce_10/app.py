from flask import Flask, render_template, jsonify, request, make_response
import threading
import adafruit_dht
import board
import time
import sqlite3
from datetime import datetime
import gpiozero
import plotly.express as px
import pandas as pd
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
auth = HTTPBasicAuth()

# Uživatelské účty (v produkci by měly být v databázi)
users = {
    "admin": generate_password_hash("heslo123"),
    "user": generate_password_hash("user123"),
}

# Konfigurace databáze
DB_NAME = "/home/dzymator/Documents/Raspberry_ukoly/Du_lekce_10/sensor_data.db"

# Na RPi4/5 je často nutné use_pulseio=False
dht = adafruit_dht.DHT11(board.D4, use_pulseio=False)
led = gpiozero.LED(15)  # LED připojená na GPIO15

# Globální proměnné pro ovládání LED
led_mode = "off"  # možné hodnoty: "on", "off", nebo číslo (teplota)
led_lock = threading.Lock()


# Inicializace databáze
def init_db():
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
        return t, h
    except RuntimeError as error:
        print(f"Chyba při čtení senzoru: {error.args[0]}")
        return None, None


# ukládání dat do databáze
def save_to_database():
    while True:
        try:
            temp, hum = read_dht()
            if temp is not None and hum is not None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute(
                    "INSERT INTO sensor_readings (timestamp, temperature, humidity) VALUES (?, ?, ?)",
                    (timestamp, temp, hum),
                )
                conn.commit()
                conn.close()

                print(
                    f"Uloženo: {timestamp} - Teplota: {temp:.2f}°C, Vlhkost: {hum:.2f}%"
                )
        except Exception as e:
            print(f"Chyba při ukládání: {e}")

        time.sleep(2)  # Čekat 2 sekundy před dalším čtením


# Vlákno pro ovládání LED s termostatem
def led_controller():
    global led_mode

    while True:
        try:
            with led_lock:
                current_mode = led_mode

            if current_mode == "on":
                led.on()
            elif current_mode == "off":
                led.off()
            elif isinstance(current_mode, (int, float)):
                # Auto režim - termostat s hysterezí
                target_temp = current_mode
                temp, _ = read_dht()

                if temp is not None:
                    if temp <= target_temp - 1:
                        led.on()
                        print(f"LED ON - Teplota {temp}°C <= {target_temp - 1}°C")
                    elif temp >= target_temp + 1:
                        led.off()
                        print(f"LED OFF - Teplota {temp}°C >= {target_temp + 1}°C")
                    # Jinak LED zůstane ve svém stavu (hystereze)

            time.sleep(1)  # Kontrola každou sekundu

        except Exception as e:
            print(f"Chyba v LED controlleru: {e}")
            time.sleep(1)


# Verifikační funkce pro HTTP Basic Auth
@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None


# Načtení posledních dat z databáze
def get_latest_data():
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
@auth.login_required
def index():
    return render_template("index.html", sensor_graph=graph())


# API endpoint pro získání dat
@app.get("/api/data")
@auth.login_required
def get_data():
    data = get_latest_data()
    if data:
        latest = {
            "timestamp": data[0][0],
            "temperature": round(float(data[0][1]), 1),
            "humidity": round(float(data[0][2]), 1),
            "history": [
                {
                    "timestamp": row[0],
                    "temperature": round(float(row[1]), 1),
                    "humidity": round(float(row[2]), 1),
                }
                for row in data
            ],
        }
        return jsonify(latest)
    return jsonify({"error": "Žádná data"})


# API endpoint pro ovládání LED
@app.post("/api/led")
@auth.login_required
def control_led():
    global led_mode  # Přístup k globální proměnné

    # Získání požadavku
    try:
        state = request.json.get("state")
    except Exception as e:
        return jsonify({"error": str(e)}), 415

    # Nastavení režimu LED
    with led_lock:
        if state == "on":
            led_mode = "on"
            return jsonify({"status": "LED zapnuta"})
        elif state == "off":
            led_mode = "off"
            return jsonify({"status": "LED vypnuta"})
        elif isinstance(state, int) and 10 <= state <= 35:
            led_mode = state
            return jsonify({"status": f"LED auto režim na {state}°C"})
        else:
            return jsonify({"error": "Neplatný stav"}), 400


# plotly graph to html route
@app.route("/api/graph")
@auth.login_required
def graph():
    with sqlite3.connect(DB_NAME) as conn:
        df = pd.read_sql_query(
            """SELECT timestamp, temperature, humidity
               FROM sensor_readings
               WHERE datetime(timestamp) >= datetime('now', '-1 hour')
               ORDER BY timestamp ASC""",
            conn,
        )
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    fig = px.line(
        df,
        x="timestamp",
        y=["temperature", "humidity"],
        title="",
        labels={"timestamp": "Čas", "value": "Hodnota", "variable": "Veličina"},
    )
    fig.data[0].name = "Teplota (°C)"
    fig.data[1].name = "Vlhkost (%)"
    fig.data[0].line.color = "#667eea"  # Fialová barva z designu
    fig.data[1].line.color = "#764ba2"  # Tmavší fialová
    fig.data[0].line.width = 3
    fig.data[1].line.width = 3
    fig.update_layout(
        xaxis=dict(
            tickformat="%H:%M:%S",
            title="Čas",
            showgrid=True,
            gridcolor="rgba(0,0,0,0.05)",
        ),
        yaxis=dict(title="Hodnota", showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
        hovermode="x unified",
        template="plotly_white",
        font=dict(family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif", size=14),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=50, r=50, t=20, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12),
        ),
        height=550,
    )

    graph_html = fig.to_html(full_html=False, include_plotlyjs="cdn")
    resp = make_response(graph_html)
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp


if __name__ == "__main__":
    # Inicializace databáze
    init_db()

    # Spuštění vlákna pro ukládání dat
    sensor_thread = threading.Thread(target=save_to_database, daemon=True)
    sensor_thread.start()

    # Spuštění vlákna pro ovládání LED
    led_thread = threading.Thread(target=led_controller, daemon=True)
    led_thread.start()

    # Spuštění Flask aplikace
    app.run(debug=True, use_reloader=False, port=5000)
