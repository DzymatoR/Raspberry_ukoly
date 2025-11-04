# Raspberry Pi - Domácí úkoly

Repozitář obsahuje domácí úkoly z kurzu programování na Raspberry Pi s využitím senzorů a webových aplikací.

## Hardware

- **Raspberry Pi** (testováno na RPi 4/5)
- **DHT11** - teplotní a vlhkostní senzor
- **LED diody** - modrá, žlutá, červená (lekce 2)
- **Odpory** (volitelné pro LED)
- **Breadboard a propojovací kabely**

### Zapojení

**DHT11 senzor:**
- Pin 1 → 3.3V (pin 1)
- Pin 2 → GPIO 4 (pin 7)
- Pin 4 → Ground (pin 9)

**LED diody (lekce 2):**
- Všechny LED → Ground přes breadboard (pin 6)
- Modrá LED → GPIO 14 (pin 8)
- Žlutá LED → GPIO 15 (pin 10)
- Červená LED → GPIO 18 (pin 12)

## Instalace

```bash
# Naklonování repozitáře
git clone <repository-url>
cd Raspberry_ukoly

# Instalace závislostí
pip install adafruit-circuitpython-dht
pip install board
pip install flask
pip install gpiozero
```

## Struktura projektu

```
Raspberry_ukoly/
├── DU_lekce_2/          # Základní čtení DHT11 + LED indikace
├── DU_lekce_4/          # Ukládání dat do SQLite databáze
├── DU_lekce_6/          # Základní Flask webová aplikace
├── DU_lekce_8/          # Pokročilá Flask aplikace s databází
└── pigpio/              # Knihovna pigpio
```

## Lekce

### Lekce 2 - Základní práce se senzorem DHT11

**Soubor:** `DU_lekce_2/DHT11.py`

**Funkcionalita:**
- Čtení teploty a vlhkosti každé 2 sekundy
- Vizuální indikace teploty pomocí LED:
  - Modrá LED svítí při teplotě < 0°C
  - Žlutá LED bliká podle desítek stupňů (teplota // 10)
  - Červená LED bliká podle jednotek stupňů (teplota % 10)

**Spuštění:**
```bash
python DU_lekce_2/DHT11.py
```

---

### Lekce 4 - Databáze a export dat

**Soubor:** `DU_lekce_4/Databaze.py`

**Funkcionalita:**
- Čtení dat ze senzoru DHT11 (5 měření)
- Ukládání do SQLite databáze (`sensor.db`)
- Export dat do CSV (`sensor_data.csv`)
- Výpočet průměrných hodnot teploty a vlhkosti

**Databázová struktura:**
```sql
CREATE TABLE sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timastamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    temperature REAL,
    humidity REAL
)
```

**Spuštění:**
```bash
python DU_lekce_4/Databaze.py
```

---

### Lekce 6 - Základní Flask webová aplikace

**Soubor:** `DU_lekce_6/app.py`

**Funkcionalita:**
- Jednoduché webové rozhraní pro zobrazení dat ze senzoru
- REST API endpoint `/api/data`
- Real-time čtení dat při každém požadavku

**Spuštění:**
```bash
python DU_lekce_6/app.py
# Otevřít prohlížeč na http://localhost:5000
```

**Poznámka:** Obsahuje návod na nastavení Cloudflare tunelu pro vzdálený přístup.

---

### Lekce 8 - Pokročilá webová aplikace s databází

**Soubor:** `DU_lekce_8/app.py`

**Funkcionalita:**
- Moderní responzivní webové rozhraní
- Automatické ukládání dat do databáze každé 2 sekundy (vlákno na pozadí)
- REST API endpoint `/api/data` pro získání aktuálních a historických dat
- Zobrazení posledních 10 měření
- Automatická aktualizace dat ve webovém rozhraní každých 5 sekund

**Technologie:**
- Flask web framework
- SQLite databáze (`sensor_data.db`)
- Threading pro paralelní sběr dat
- Responzivní design s gradient pozadím

**Spuštění:**
```bash
python DU_lekce_8/app.py
# Otevřít prohlížeč na http://localhost:1234
```

**API Response:**
```json
{
  "timestamp": "2024-11-04 20:15:30",
  "temperature": 22.5,
  "humidity": 45.2,
  "history": [
    {
      "timestamp": "2024-11-04 20:15:30",
      "temperature": 22.5,
      "humidity": 45.2
    }
  ]
}
```

## Běžné problémy

### DHT11 senzor nečte data
- Senzor potřebuje inicializační čas (~2 sekundy)
- Na RPi 4/5 používat `use_pulseio=False`
- Zkontrolovat zapojení pinů

### Chyba při přístupu k GPIO
```bash
sudo usermod -a -G gpio $USER
# Odhlásit se a přihlásit znovu
```

## Autor

Domácí úkoly z kurzu programování Raspberry Pi

## Licence

Kód v `DU_lekce_2/DHT11.py` obsahuje části z Adafruit Industries (MIT License)
