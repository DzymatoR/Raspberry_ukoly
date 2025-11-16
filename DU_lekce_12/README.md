# 📊 IoT Senzorový Monitoring - Raspberry Pi

> Flask webová aplikace pro monitorování environmentálních dat (teplota, vlhkost) s pokročilými funkcemi jako RBAC, systemd watchdog a HTTPS.

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg)

---

## 📋 Obsah

- [Přehled projektu](#přehled-projektu)
- [Funkce](#funkce)
- [Hardware](#hardware)
- [Instalace](#instalace)
- [Konfigurace](#konfigurace)
- [Spuštění](#spuštění)
- [Architektura](#architektura)
- [API Dokumentace](#api-dokumentace)
- [Bezpečnost](#bezpečnost)
- [Testování](#testování)
- [Troubleshooting](#troubleshooting)
- [Licence](#licence)

---

## 🎯 Přehled projektu

Tento projekt je komplexní IoT řešení pro **Raspberry Pi**, které monitoruje environmentální data pomocí senzoru **DHT11** a poskytuje webové rozhraní pro zobrazení dat a ovládání aktuátorů.

### Klíčové vlastnosti:

- 🌡️ **Real-time monitoring** - Teplota a vlhkost každých 30 sekund
- 📈 **Grafická vizualizace** - Interaktivní grafy pomocí Plotly
- 💡 **Ovládání LED** - Manuální režim + automatický termostat
- 🔐 **Role-based Access Control (RBAC)** - Tři úrovně přístupu
- 🛡️ **HTTPS** - Cloudflare Tunnel s automatickými certifikáty
- 📝 **Comprehensive Logging** - 30denní rotace logů
- 🔄 **Systemd Watchdog** - Automatický restart při pádu
- 🗄️ **SQLite databáze** - Persistentní ukládání dat

---

## ✨ Funkce

### Základní funkce (20 bodů)

#### 1. **Webový Dashboard**
- Zobrazení aktuálních hodnot teploty a vlhkosti
- Historie posledních 10 měření v tabulce
- Interaktivní graf za poslední 24 hodin (Plotly)
- Responzivní design s moderním UI

#### 2. **Ovládání LED**
- **Manuální režim**: Zapnuto/Vypnuto
- **Auto režim**: Termostat s nastavitelnou teplotou (10-36°C)
- Hystereze ±1°C pro stabilní chování
- Real-time feedback v UI

#### 3. **Periodický sběr dat**
- Automatické čtení senzoru každých 30 sekund
- Ukládání do SQLite databáze
- Multi-threading pro bezproblémový chod

#### 4. **Systemd integrace**
- Automatické spuštění při bootu
- Watchdog monitoring (30s timeout)
- Graceful restart při pádu aplikace

#### 5. **Logování**
- TimedRotatingFileHandler (rotace každý den)
- 30denní retence logů
- Logování: start, data collection, LED změny, chyby, RBAC události
- Output do souboru i journald

#### 6. **HTTPS & Cloudflare**
- Cloudflare Tunnel pro bezpečný přístup z internetu
- Automatické SSL certifikáty
- DDoS ochrana
- Zero-trust přístup

#### 7. **Autentizace**
- HTTP Basic Authentication
- PBKDF2-SHA256 password hashing (260,000 iterací)
- Bezpečné generování hesel pomocí utility skriptu

### Rozšíření (10 bodů)

#### 🔒 **Role-based Access Control (RBAC)**

Granulární systém oprávnění se třemi rolemi:

| Role | Aktuální data | Historie | Graf | Ovládání LED | Přihlášení |
|------|---------------|----------|------|--------------|------------|
| **Admin** | ✅ | ✅ | ✅ | ✅ | admin / admin123 |
| **User** | ✅ | ✅ | ✅ | ❌ | user / user123 |
| **Viewer** | ✅ | ❌ | ❌ | ❌ | viewer / viewer123 |

**Funkce:**
- Server-side validace oprávnění
- Client-side dynamické skrývání UI elementů
- Logování zamítnutých přístupů
- Decorator-based permission checks
- Role-specific dashboards

---

## 🔧 Hardware

### Požadované komponenty:

- **Raspberry Pi 4/5** (doporučeno) nebo starší model
- **DHT11** - Teploměr a vlhkoměr (GPIO 4)
- **LED** - Indikátor/aktuátor (GPIO 15)
- **Rezistor** - 220Ω pro LED
- **Breadboard a propojovací kabely**

### Schéma zapojení:

```
DHT11:
  VCC  -> 3.3V (Pin 1)
  DATA -> GPIO 4 (Pin 7)
  GND  -> Ground (Pin 6)

LED:
  Anoda  -> GPIO 15 (Pin 10)
  Katoda -> GND přes rezistor 220Ω
```

---

## 📦 Instalace

### 1. Systémové balíčky

```bash
# Aktualizace systému
sudo apt update && sudo apt upgrade -y

# Instalace Python a závislostí
sudo apt install -y python3 python3-pip python3-venv git

# Systemd knihovna (pro watchdog)
sudo apt install -y python3-systemd
```

### 2. Klonování projektu

```bash
cd ~/Documents/Raspberry_ukoly
git clone <your-repo-url> DU_lekce_12
cd DU_lekce_12
```

### 3. Virtuální prostředí (volitelné)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Python závislosti

```bash
pip install -r requirements.txt
```

**Obsah `requirements.txt`:**
```
Flask==3.0.0
adafruit-circuitpython-dht==4.0.3
gpiozero==2.0.1
plotly==5.18.0
pandas==2.1.4
Flask-HTTPAuth==4.8.0
Werkzeug==3.0.1
```

---

## ⚙️ Konfigurace

### 1. Uživatelé a hesla

Pro změnu hesel použij utility skript:

```bash
python3 generate_password_hash.py
```

Vygenerovaný hash přidej do `app.py`:

```python
users = {
    "novy_uzivatel": {
        "password_hash": "pbkdf2:sha256:260000$...",
        "role": "user"  # admin, user, nebo viewer
    }
}
```

### 2. Systemd Service

Zkopíruj service soubor:

```bash
sudo cp sensor-app.service /etc/systemd/system/rpdashboard.service
```

Uprav cesty v service souboru (pokud je potřeba):

```ini
[Service]
WorkingDirectory=/home/dzymator/Documents/Raspberry_ukoly/DU_lekce_12
ExecStart=/usr/bin/python3 /home/dzymator/Documents/Raspberry_ukoly/DU_lekce_12/app.py
Environment="PYTHONPATH=/home/dzymator/Documents/Raspberry_ukoly/.venv/lib/python3.11/site-packages"
```

Reload a enable službu:

```bash
sudo systemctl daemon-reload
sudo systemctl enable rpdashboard.service
sudo systemctl start rpdashboard.service
```

### 3. Cloudflare Tunnel (volitelné)

Pro HTTPS přístup z internetu:

```bash
# Instalace cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o cloudflared
sudo mv cloudflared /usr/local/bin/
sudo chmod +x /usr/local/bin/cloudflared

# Autentizace
cloudflared tunnel login

# Vytvoření tunelu
cloudflared tunnel create sensor-app
cloudflared tunnel route dns sensor-app sensor.example.com

# Spuštění
cloudflared tunnel run sensor-app
```

---

## 🚀 Spuštění

### Manuální spuštění (pro testování)

```bash
cd /home/dzymator/Documents/Raspberry_ukoly/DU_lekce_12
python3 app.py
```

Aplikace běží na `http://localhost:5000`

### Spuštění pomocí systemd (produkce)

```bash
# Start
sudo systemctl start rpdashboard.service

# Stop
sudo systemctl stop rpdashboard.service

# Restart
sudo systemctl restart rpdashboard.service

# Status
sudo systemctl status rpdashboard.service

# Logy
sudo journalctl -u rpdashboard.service -f
```

### Automatický update služby

Použij připravený skript:

```bash
./update_service.sh
```

---

## 🏗️ Architektura

### Struktura projektu

```
DU_lekce_12/
├── app.py                          # Hlavní Flask aplikace
├── generate_password_hash.py       # Generátor hashů hesel
├── requirements.txt                # Python závislosti
├── sensor-app.service             # Systemd service soubor (příklad)
├── update_service.sh              # Update skript pro službu
├── .gitignore                     # Git ignore pravidla
├── README.md                      # Tento soubor
├── templates/
│   └── index.html                 # Webové rozhraní
├── logs/                          # Aplikační logy (ignorováno gitem)
│   ├── app.log                    # Aktuální log
│   └── app.log.YYYY-MM-DD         # Rotované logy
├── sensor_data.db                 # SQLite databáze (ignorováno)
└── Dokumentace/
    ├── RBAC.md                    # Dokumentace RBAC
    ├── Bezpečnost.md              # Bezpečnostní praktiky
    ├── Logování.md                # Dokumentace loggingu
    ├── SystemD a Watchdog.md      # Watchdog dokumentace
    └── Implementovane_funkce.md   # Přehled funkcí
```

### Komponenty aplikace

#### **Flask Application** (`app.py`)

**Hlavní moduly:**
- **Logging** (řádky 21-49) - Konfigurace TimedRotatingFileHandler
- **Authentication** (řádky 54-92) - Uživatelé, role, oprávnění
- **Database** (řádky 107-118) - SQLite inicializace
- **Sensor Reading** (řádky 122-129) - DHT11 čtení
- **Data Collection** (řádky 133-156) - Threading pro periodický sběr
- **LED Controller** (řádky 159-207) - Termostat s hysterezí
- **Watchdog** (řádky 210-237) - Systemd heartbeat
- **RBAC Helpers** (řádky 250-278) - Permission checking
- **API Routes** (řádky 293-435) - Flask endpoints

#### **Frontend** (`templates/index.html`)

**Technologie:**
- Vanilla JavaScript (žádné frameworky)
- CSS3 s gradientním designem
- Fetch API pro AJAX requesty
- Jinja2 templating pro RBAC

**Funkce:**
- Real-time data updates (každé 2 minuty)
- Graph updates pomocí iframe reload
- Permission-based UI rendering
- Radio buttons a range slider pro LED ovládání

#### **Database Schema** (`sensor_data.db`)

```sql
CREATE TABLE sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    temperature REAL,
    humidity REAL
);
```

### Threading model

Aplikace používá 4 vlákna:

1. **Main Thread** - Flask server
2. **Sensor Thread** - Periodický sběr dat (30s interval)
3. **LED Thread** - Ovládání LED a termostat (1s check)
4. **Watchdog Thread** - Systemd heartbeat (15s interval)

Všechna vlákna jsou daemon threads, takže se automaticky ukončí při shutdown.

---

## 📡 API Dokumentace

### Endpointy

#### `GET /`
Hlavní dashboard stránka.

**Autentizace:** Required
**Oprávnění:** Všichni uživatelé
**Response:** HTML

---

#### `GET /api/data`
Získání aktuálních dat a historie.

**Autentizace:** Required
**Oprávnění:** `can_view_data`

**Response:**
```json
{
  "timestamp": "2025-11-16 17:15:34",
  "temperature": 18.7,
  "humidity": 63.0,
  "user": "admin",
  "role": "admin",
  "history": [
    {
      "timestamp": "2025-11-16 17:15:34",
      "temperature": 18.7,
      "humidity": 63.0
    },
    ...
  ]
}
```

**Poznámka:** Pole `history` je prázdné pro uživatele bez oprávnění `can_view_history`.

---

#### `POST /api/led`
Ovládání LED.

**Autentizace:** Required
**Oprávnění:** `can_control_led`

**Request:**
```json
{
  "state": "on"    // "on", "off", nebo číslo 10-36 (auto režim)
}
```

**Response:**
```json
{
  "status": "LED zapnuta"
}
```

**Chyby:**
- `403 Forbidden` - Nedostatečná oprávnění
- `400 Bad Request` - Neplatný stav

---

#### `GET /api/graph`
Získání grafu za poslední 24 hodin.

**Autentizace:** Required
**Oprávnění:** `can_view_graph`

**Response:** HTML (Plotly graf)

---

## 🔐 Bezpečnost

### Password Hashing

- **Algoritmus:** PBKDF2-SHA256
- **Iterace:** 260,000
- **Salt:** Automaticky generovaný

**Generování nového hesla:**
```bash
python3 generate_password_hash.py
```

### HTTP Basic Authentication

Všechny endpointy vyžadují autentizaci. Prohlížeč automaticky zobrazí přihlašovací dialog.

**Curl příklad:**
```bash
curl -u admin:admin123 http://localhost:5000/api/data
```

### RBAC Oprávnění

Oprávnění jsou kontrolována na dvou úrovních:

1. **Server-side:** Dekorátor `@require_permission()`
2. **Client-side:** Jinja2 podmínky v šabloně

### Logování bezpečnostních událostí

Všechny zamítnuté přístupy jsou logovány:

```
2025-11-16 17:37:54,460 - WARNING - Zamítnut přístup pro viewer - chybí oprávnění: can_control_led
```

### Best Practices

✅ Nikdy necommituj `sensor_data.db` nebo `logs/` do gitu
✅ Změň výchozí hesla v produkci
✅ Používej HTTPS (Cloudflare Tunnel)
✅ Pravidelně kontroluj logy na podezřelé aktivity
✅ Aktualizuj závislosti: `pip list --outdated`

---

## 🧪 Testování

### Test RBAC oprávnění

```bash
# Admin - měl by vidět historii
curl -u admin:admin123 http://localhost:5000/api/data | jq '.history | length'
# Output: 10

# Viewer - neměl by vidět historii
curl -u viewer:viewer123 http://localhost:5000/api/data | jq '.history | length'
# Output: 0

# Viewer pokus o ovládání LED - měl by dostat 403
curl -u viewer:viewer123 -X POST -H "Content-Type: application/json" \
  -d '{"state":"on"}' http://localhost:5000/api/led
# Output: {"error": "Nemáte oprávnění k této akci"}
```

### Test watchdog

```bash
# Zjištění PID
sudo systemctl status rpdashboard.service | grep "Main PID"

# Simulace pádu
sudo kill -9 <PID>

# Systemd by měl automaticky restartovat službu do 30 sekund
sudo journalctl -u rpdashboard.service -f
```

### Test logování

```bash
# Real-time monitoring
tail -f logs/app.log

# Filtrování chyb
grep ERROR logs/app.log

# Poslední zápisy
tail -n 50 logs/app.log
```

### Test grafu a dat

```bash
# Kontrola databáze
sqlite3 sensor_data.db "SELECT COUNT(*) FROM sensor_readings;"

# Poslední záznam
sqlite3 sensor_data.db "SELECT * FROM sensor_readings ORDER BY id DESC LIMIT 1;"

# Data za poslední hodinu
sqlite3 sensor_data.db "SELECT * FROM sensor_readings WHERE datetime(timestamp) >= datetime('now', '-1 hour');"
```

---

## 🐛 Troubleshooting

### Aplikace se nespustí

**Problém:** `ModuleNotFoundError: No module named 'systemd'`

**Řešení:**
```bash
sudo apt install python3-systemd
```

---

**Problém:** `RuntimeError: Cannot access /dev/gpiomem`

**Řešení:**
```bash
# Přidej uživatele do gpio skupiny
sudo usermod -a -G gpio $USER

# Restart nebo relogin
```

---

**Problém:** `sqlite3.OperationalError: unable to open database file`

**Řešení:** Zkontroluj cesty v `app.py`:
```python
DB_NAME = "/home/dzymator/Documents/Raspberry_ukoly/DU_lekce_12/sensor_data.db"
```

---

### Služba spadne po startu

**Kontrola logů:**
```bash
sudo journalctl -u rpdashboard.service -n 50 --no-pager
```

**Časté problémy:**
- Chybná cesta v `WorkingDirectory`
- Chybná cesta v `PYTHONPATH`
- Chybějící oprávnění k souborům

---

### Watchdog timeout

**Problém:** Služba se restartuje každých 30 sekund

**Příčiny:**
- Zablokované vlákno (deadlock)
- Velmi pomalé čtení senzoru
- Vysoké zatížení CPU

**Řešení:** Zkontroluj logy a zvyš `WatchdogSec` v service souboru.

---

### DHT11 vrací None hodnoty

**Příčiny:**
- Špatné zapojení
- Vadný senzor
- Nedostatečná power

**Řešení:**
```bash
# Test čtení
python3 -c "import adafruit_dht, board; dht = adafruit_dht.DHT11(board.D4, use_pulseio=False); print(f'Temp: {dht.temperature}°C, Humidity: {dht.humidity}%')"
```

---

## 📊 Statistiky projektu

- **Počet řádků kódu (app.py):** ~477
- **Počet API endpointů:** 4
- **Počet rolí:** 3
- **Počet oprávnění:** 4
- **Retention logů:** 30 dní
- **Interval sběru dat:** 30 sekund
- **Interval aktualizace UI:** 2 minuty
- **Graf zobrazuje:** 24 hodin
- **Watchdog timeout:** 30 sekund

---

## 📚 Dokumentace

Detailní dokumentace je k dispozici ve složce `Dokumentace/`:

- [**RBAC.md**](Dokumentace/RBAC.md) - Role-based Access Control
- [**Bezpečnost.md**](Dokumentace/Bezpečnost.md) - Bezpečnostní praktiky
- [**Logování.md**](Dokumentace/Logování.md) - Logging system
- [**SystemD a Watchdog.md**](Dokumentace/SystemD%20a%20Watchdog.md) - Systemd konfigurace
- [**Implementovane_funkce.md**](Dokumentace/Implementovane_funkce.md) - Kompletní přehled

---

## 🚀 Možná rozšíření

- [ ] Email notifikace při kritických hodnotách
- [ ] Databázový backend pro uživatele (PostgreSQL/MySQL)
- [ ] API klíče místo Basic Auth
- [ ] Export dat do CSV/JSON
- [ ] Mobilní aplikace (React Native)
- [ ] Push notifikace (Firebase Cloud Messaging)
- [ ] Více senzorů (DHT22, BME280, DS18B20)
- [ ] Podpora více LED/relé
- [ ] Časové plánování (cron-like scheduling)
- [ ] Webové rozhraní pro správu uživatelů
- [ ] Prometheus metrics export
- [ ] Docker kontejnerizace

---

## 🤝 Přispívání

Příspěvky jsou vítány! Pokud chceš přidat novou funkci nebo opravit bug:

1. Fork projektu
2. Vytvoř feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit změny (`git commit -m 'Add some AmazingFeature'`)
4. Push do branch (`git push origin feature/AmazingFeature`)
5. Otevři Pull Request

---

## 📝 Licence

Tento projekt je licencován pod MIT licencí - viz [LICENSE](LICENSE) soubor pro detaily.

---

## 👤 Autor

**dzymator**
- GitHub: [@dzymator](https://github.com/dzymator)
- Projekt: Raspberry Pi: Vytvářej chytrá zařízení - Lekce 12

---

## 🙏 Poděkování

- **Adafruit** - Za knihovnu pro DHT senzory
- **Plotly** - Za skvělou grafovací knihovnu
- **Flask** - Za jednoduchý webový framework
- **Cloudflare** - Za bezplatné HTTPS tunely
- **Raspberry Pi Foundation** - Za úžasný hardware

---

## 📞 Kontakt

Pokud máš otázky nebo narazíš na problémy, neváhej vytvořit issue v GitHub repozitáři.

**Happy Coding! 🎉**
