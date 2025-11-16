from flask import Flask, render_template, jsonify, request, make_response
import threading
import adafruit_dht
import board
import time
import sqlite3
from datetime import datetime, timedelta
import gpiozero
import plotly.express as px
import pandas as pd
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash
from systemd import daemon  # type: ignore
import logging
from logging.handlers import TimedRotatingFileHandler
import os

app = Flask(__name__)
auth = HTTPBasicAuth()

# Konfigurace loggeru
LOG_DIR = "/home/dzymator/Documents/Raspberry_ukoly/DU_lekce_12/logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Vytvoření složky pro logy, pokud neexistuje
os.makedirs(LOG_DIR, exist_ok=True)

# Nastavení loggeru
logger = logging.getLogger("SensorApp")
logger.setLevel(logging.INFO)

# Handler pro rotaci logů každý den, uchovávat 30 dní
file_handler = TimedRotatingFileHandler(
    LOG_FILE, when="midnight", interval=1, backupCount=30, encoding="utf-8"
)
file_handler.setLevel(logging.INFO)

# Formát logu
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Přidat handler do loggeru
logger.addHandler(file_handler)

# Console handler pro výpis do terminálu (volitelné)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Uživatelské účty s rolemi
# Struktura: username -> {"password_hash": hash, "role": role}
# Role: "admin", "user", "viewer"
users = {
    "admin": {
        "password_hash": "pbkdf2:sha256:260000$1OQAf9UpDgDVdwIk$056529a4afe4b8aff6df05ba14df5cedf26a4cc3395255fbe45470ed9f13646d",
        "role": "admin"
    },
    "user": {
        "password_hash": "pbkdf2:sha256:260000$wLlXZ2evlh7rXZPa$ca7528424a497fa54690abf3281df93161ce5f7583871c30d2a318d502a52226",
        "role": "user"
    },
    "viewer": {
        "password_hash": "pbkdf2:sha256:260000$B5WwL3kdUgPmzExN$6cc3e014127746cd9deccfe9ee8914b9e2ea1a537a6a598a2a18df74d2420839",
        "role": "viewer"
    },
}

# Definice rolí a jejich oprávnění
ROLES = {
    "admin": {
        "can_view_data": True,
        "can_view_history": True,
        "can_view_graph": True,
        "can_control_led": True,
        "description": "Plný přístup ke všem funkcím"
    },
    "user": {
        "can_view_data": True,
        "can_view_history": True,
        "can_view_graph": True,
        "can_control_led": False,
        "description": "Čtení dat a historie (bez ovládání LED)"
    },
    "viewer": {
        "can_view_data": True,
        "can_view_history": False,
        "can_view_graph": False,
        "can_control_led": False,
        "description": "Pouze aktuální data"
    },
}

# Konfigurace databáze
DB_NAME = "/home/dzymator/Documents/Raspberry_ukoly/DU_lekce_12/sensor_data.db"

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

                # Logování úspěšného uložení
                logger.info(
                    f"Data uložena - Teplota: {temp:.1f}°C, Vlhkost: {hum:.1f}%"
                )
        except Exception as e:
            logger.error(f"Chyba při ukládání do databáze: {e}")

        time.sleep(30)  # Čekat 30 sekund před dalším čtením


# Vlákno pro ovládání LED s termostatem
def led_controller():
    global led_mode
    last_led_state = None  # Pro sledování změn stavu

    while True:
        try:
            with led_lock:
                current_mode = led_mode

            current_led_state = led.is_lit

            if current_mode == "on":
                if not current_led_state:
                    led.on()
                    logger.info("LED zapnuta - manuální režim")
                    last_led_state = True
            elif current_mode == "off":
                if current_led_state:
                    led.off()
                    logger.info("LED vypnuta - manuální režim")
                    last_led_state = False
            elif isinstance(current_mode, (int, float)):
                # Auto režim - termostat s hysterezí
                target_temp = current_mode
                temp, _ = read_dht()

                if temp is not None:
                    if temp <= target_temp - 1:
                        if not current_led_state:
                            led.on()
                            logger.info(
                                f"LED zapnuta - Auto režim (teplota {temp:.1f}°C <= {target_temp - 1}°C)"
                            )
                            last_led_state = True
                    elif temp >= target_temp + 1:
                        if current_led_state:
                            led.off()
                            logger.info(
                                f"LED vypnuta - Auto režim (teplota {temp:.1f}°C >= {target_temp + 1}°C)"
                            )
                            last_led_state = False
                    # Jinak LED zůstane ve svém stavu (hystereze)

            time.sleep(1)  # Kontrola každou sekundu

        except Exception as e:
            logger.error(f"Chyba v LED controlleru: {e}")
            time.sleep(1)


# Vlákno pro systemd watchdog
def watchdog_notify():
    """Periodicky posílá watchdog notifikace do systemd"""
    # Zjistit watchdog timeout z environment proměnné
    watchdog_usec = os.environ.get("WATCHDOG_USEC")

    if not watchdog_usec:
        logger.info("Systemd watchdog není aktivní")
        return

    try:
        watchdog_usec = int(watchdog_usec)
    except ValueError:
        logger.error(f"Neplatná hodnota WATCHDOG_USEC: {watchdog_usec}")
        return

    # Interval pro watchdog notifikace (polovina watchdog timeout)
    interval = watchdog_usec / 2_000_000  # převod z mikrosekund na sekundy
    logger.info(f"Systemd watchdog aktivní, interval: {interval}s")

    while True:
        try:
            # Poslat watchdog notifikaci
            daemon.notify("WATCHDOG=1")
            time.sleep(interval)
        except Exception as e:
            logger.error(f"Chyba při posílání watchdog notifikace: {e}")
            time.sleep(interval)


# Verifikační funkce pro HTTP Basic Auth
@auth.verify_password
def verify_password(username, password):
    if username in users:
        user_data = users[username]
        if check_password_hash(user_data["password_hash"], password):
            return username
    return None


# Pomocné funkce pro RBAC
def get_user_role(username):
    """Vrátí roli uživatele"""
    if username in users:
        return users[username]["role"]
    return None


def has_permission(username, permission):
    """Zkontroluje, zda má uživatel dané oprávnění"""
    role = get_user_role(username)
    if role and role in ROLES:
        return ROLES[role].get(permission, False)
    return False


def require_permission(permission):
    """Dekorátor pro kontrolu oprávnění"""
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            username = auth.current_user()
            if not has_permission(username, permission):
                logger.warning(f"Zamítnut přístup pro {username} - chybí oprávnění: {permission}")
                return jsonify({"error": "Nemáte oprávnění k této akci"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


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
    username = auth.current_user()
    role = get_user_role(username)
    permissions = ROLES.get(role, {})

    return render_template(
        "index.html",
        username=username,
        role=role,
        permissions=permissions,
    )


# API endpoint pro získání dat
@app.get("/api/data")
@auth.login_required
@require_permission("can_view_data")
def get_data():
    username = auth.current_user()
    data = get_latest_data()

    if data:
        # Základní data pro všechny
        latest = {
            "timestamp": data[0][0],
            "temperature": round(float(data[0][1]), 1),
            "humidity": round(float(data[0][2]), 1),
            "user": username,
            "role": get_user_role(username),
        }

        # Historie jen pro uživatele s oprávněním
        if has_permission(username, "can_view_history"):
            latest["history"] = [
                {
                    "timestamp": row[0],
                    "temperature": round(float(row[1]), 1),
                    "humidity": round(float(row[2]), 1),
                }
                for row in data
            ]
        else:
            latest["history"] = []

        return jsonify(latest)
    return jsonify({"error": "Žádná data"})


# API endpoint pro ovládání LED
@app.post("/api/led")
@auth.login_required
@require_permission("can_control_led")
def control_led():
    global led_mode  # Přístup k globální proměnné
    username = auth.current_user()

    # Získání požadavku
    try:
        state = request.json.get("state")
    except Exception as e:
        logger.error(f"Chyba při parsování požadavku na ovládání LED: {e}")
        return jsonify({"error": str(e)}), 415

    # Nastavení režimu LED
    with led_lock:
        if state == "on":
            led_mode = "on"
            logger.info(f"Režim LED změněn na: ON (manuální) - uživatel: {username}")
            return jsonify({"status": "LED zapnuta"})
        elif state == "off":
            led_mode = "off"
            logger.info(f"Režim LED změněn na: OFF (manuální) - uživatel: {username}")
            return jsonify({"status": "LED vypnuta"})
        elif isinstance(state, int) and 10 <= state <= 35:
            led_mode = state
            logger.info(f"Režim LED změněn na: AUTO ({state}°C) - uživatel: {username}")
            return jsonify({"status": f"LED auto režim na {state}°C"})
        else:
            logger.warning(f"Neplatný požadavek na změnu LED režimu: {state}")
            return jsonify({"error": "Neplatný stav"}), 400


# plotly graph to html route
@app.route("/api/graph")
@auth.login_required
@require_permission("can_view_graph")
def graph():
    with sqlite3.connect(DB_NAME) as conn:
        df = pd.read_sql_query(
            """SELECT timestamp, temperature, humidity
               FROM sensor_readings
               WHERE datetime(timestamp) >= datetime('now', '-1 day')
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
    try:
        logger.info("=" * 60)
        logger.info("Spuštění aplikace Flask Sensor Monitoring")
        logger.info("=" * 60)

        # Inicializace databáze
        init_db()
        logger.info("Databáze inicializována")

        # Spuštění vlákna pro ukládání dat
        sensor_thread = threading.Thread(target=save_to_database, daemon=True)
        sensor_thread.start()
        logger.info("Vlákno pro ukládání dat spuštěno")

        # Spuštění vlákna pro ovládání LED
        led_thread = threading.Thread(target=led_controller, daemon=True)
        led_thread.start()
        logger.info("Vlákno pro ovládání LED spuštěno")

        # Spuštění watchdog vlákna
        watchdog_thread = threading.Thread(target=watchdog_notify, daemon=True)
        watchdog_thread.start()

        # Notifikace systemd o úspěšném startu
        daemon.notify("READY=1")
        logger.info("Aplikace úspěšně spuštěna a připravena")

        # Spuštění Flask aplikace
        app.run(debug=True, use_reloader=False, port=5000)

    except KeyboardInterrupt:
        logger.info("Aplikace ukončena uživatelem (Ctrl+C)")
    except Exception as e:
        logger.critical(f"Kritická chyba při spuštění aplikace: {e}", exc_info=True)
        raise
    finally:
        logger.info("Ukončení aplikace")
        logger.info("=" * 60)
