# Logování aplikace

Aplikace používá Python `logging` modul pro zaznamenávání důležitých událostí do souboru.

## Konfigurace

### Umístění logů
- **Složka**: `/home/dzymator/Documents/Raspberry_ukoly/DU_lekce_12/logs/`
- **Soubor**: `app.log`
- **Rotace**: Každý den o půlnoci
- **Uchovávání**: Posledních 30 dní

### Implementace v kódu

Konfigurace loggeru je v [app.py](../app.py) na řádcích 21-49:

```python
# Vytvoření složky pro logy
os.makedirs(LOG_DIR, exist_ok=True)

# Handler pro rotaci logů každý den, uchovávat 30 dní
file_handler = TimedRotatingFileHandler(
    LOG_FILE, when="midnight", interval=1, backupCount=30, encoding="utf-8"
)
```

## Co se loguje

### 1. Spuštění a ukončení aplikace
```
2025-11-16 10:15:32 - INFO - ============================================================
2025-11-16 10:15:32 - INFO - Spuštění aplikace Flask Sensor Monitoring
2025-11-16 10:15:32 - INFO - ============================================================
2025-11-16 10:15:32 - INFO - Databáze inicializována
2025-11-16 10:15:32 - INFO - Vlákno pro ukládání dat spuštěno
2025-11-16 10:15:32 - INFO - Vlákno pro ovládání LED spuštěno
2025-11-16 10:15:32 - INFO - Aplikace úspěšně spuštěna a připravena
```

### 2. Uložení dat do databáze
```
2025-11-16 10:15:34 - INFO - Data uložena - Teplota: 23.5°C, Vlhkost: 65.2%
```

### 3. Změny stavu LED

#### Manuální režim
```
2025-11-16 10:16:15 - INFO - Režim LED změněn na: ON (manuální)
2025-11-16 10:16:15 - INFO - LED zapnuta - manuální režim
```

```
2025-11-16 10:17:20 - INFO - Režim LED změněn na: OFF (manuální)
2025-11-16 10:17:20 - INFO - LED vypnuta - manuální režim
```

#### Auto režim (termostat)
```
2025-11-16 10:18:05 - INFO - Režim LED změněn na: AUTO (22°C)
2025-11-16 10:18:12 - INFO - LED zapnuta - Auto režim (teplota 21.5°C <= 21°C)
2025-11-16 10:20:45 - INFO - LED vypnuta - Auto režim (teplota 23.2°C >= 23°C)
```

### 4. Watchdog události
```
2025-11-16 10:15:32 - INFO - Systemd watchdog aktivní, interval: 15.0s
```

### 5. Chyby

#### Chyby při ukládání dat
```
2025-11-16 10:25:30 - ERROR - Chyba při ukládání do databáze: disk I/O error
```

#### Chyby v LED controlleru
```
2025-11-16 10:30:15 - ERROR - Chyba v LED controlleru: GPIO device not found
```

#### Kritické chyby při spuštění
```
2025-11-16 10:35:00 - CRITICAL - Kritická chyba při spuštění aplikace: [Errno 13] Permission denied
```

#### Neplatné požadavky
```
2025-11-16 10:40:22 - WARNING - Neplatný požadavek na změnu LED režimu: invalid_state
```

## Úrovně logování

Aplikace používá následující úrovně:

- **INFO**: Běžné události (start, změny stavu, úspěšné operace)
- **WARNING**: Upozornění (neplatné požadavky)
- **ERROR**: Chyby, které neukončí aplikaci (selhání čtení senzoru, DB chyby)
- **CRITICAL**: Kritické chyby ukončující aplikaci

## Prohlížení logů

### Zobrazení aktuálního logu
```bash
cat /home/dzymator/Documents/Raspberry_ukoly/DU_lekce_12/logs/app.log
```

### Sledování logů v reálném čase
```bash
tail -f /home/dzymator/Documents/Raspberry_ukoly/DU_lekce_12/logs/app.log
```

### Zobrazení posledních 50 řádků
```bash
tail -n 50 /home/dzymator/Documents/Raspberry_ukoly/DU_lekce_12/logs/app.log
```

### Vyhledání konkrétních událostí

**Pouze chyby:**
```bash
grep "ERROR" /home/dzymator/Documents/Raspberry_ukoly/DU_lekce_12/logs/app.log
```

**Změny LED režimu:**
```bash
grep "Režim LED změněn" /home/dzymator/Documents/Raspberry_ukoly/DU_lekce_12/logs/app.log
```

**Data z konkrétního dne:**
```bash
grep "2025-11-16" /home/dzymator/Documents/Raspberry_ukoly/DU_lekce_12/logs/app.log
```

## Rotované soubory

Starší logy jsou automaticky přejmenovány:
- `app.log` - aktuální den
- `app.log.2025-11-15` - předchozí den
- `app.log.2025-11-14` - předpředchozí den
- atd.

Soubory starší než 30 dní jsou automaticky smazány.

## Logy z systemd

Pokud běží aplikace jako systemd služba, logy jsou dostupné také přes `journalctl`:

```bash
# Zobrazit všechny logy služby
sudo journalctl -u sensor-app.service

# Sledovat logy v reálném čase
sudo journalctl -u sensor-app.service -f

# Zobrazit logy od včerejška
sudo journalctl -u sensor-app.service --since yesterday

# Zobrazit pouze chyby
sudo journalctl -u sensor-app.service -p err
```

## Důležité poznámky

- Logy se zapisují současně do souboru i do konzole
- Formát: `YYYY-MM-DD HH:MM:SS - LEVEL - Message`
- Kódování: UTF-8 (podporuje českou diakritiku)
- Automatická rotace každý den o půlnoci
- Maximálně 30 dní historie
- Složka `logs/` je v `.gitignore` a nebude commitována do git
