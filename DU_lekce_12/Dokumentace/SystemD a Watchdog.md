## Automatické spouštění aplikace

**systemd**
Linuxové systémy (tedy i RPi) nabízí možnost spouštění skriptů za definovaných podmínek - po restartu, v určitém časovém intervalu apod. V našem případě chceme, aby se aplikace spouštěla automaticky po restartu RPi.


## Watchdog - softwarový

Watchdog je mechanismus, který hlídá, zda aplikace běží správně. Pokud aplikace "zamrzne" nebo spadne, systemd ji automaticky restartuje.

### Jak watchdog funguje

1. **Aplikace musí pravidelně posílat "heartbeat" signály** do systemd
2. **Pokud systemd nedostane signál ve stanoveném čase**, považuje aplikaci za zmrzlou a restartuje ji
3. **Interval watchdog notifikací** by měl být kratší než timeout (obvykle polovina)

### Instalace

```bash
# Instalace systemd knihovny pro Python
sudo apt install python3-systemd
```

### Nastavení v aplikaci

V [app.py](../app.py) je implementováno:

1. **Import systemd knihovny** (řádek 13):
```python
from systemd import daemon
```

2. **Watchdog vlákno** (řádky 122-142) - pravidelně posílá signály:
```python
def watchdog_notify():
    watchdog_usec = daemon.watchdog_enabled()
    if not watchdog_usec:
        return

    interval = watchdog_usec / 2_000_000  # polovina timeoutu
    while True:
        daemon.notify("WATCHDOG=1")
        time.sleep(interval)
```

3. **Notifikace o startu** (řádek 298):
```python
daemon.notify("READY=1")
```

### Systemd Service soubor

Soubor [sensor-app.service](../sensor-app.service) obsahuje:

```ini
[Unit]
Description=Flask Sensor Monitoring Application
After=network.target

[Service]
Type=notify              # Aplikace posílá notifikace
User=dzymator
WorkingDirectory=/home/dzymator/Documents/Raspberry_ukoly/DU_lekce_12
ExecStart=/usr/bin/python3 /home/dzymator/Documents/Raspberry_ukoly/DU_lekce_12/app.py
Restart=always           # Vždy restartovat při pádu
RestartSec=5             # Čekat 5s před restartem

WatchdogSec=30          # Timeout 30 sekund
# Pokud aplikace nepošle signál 30s, systemd ji restartuje

Environment="PYTHONUNBUFFERED=1"
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Instalace služby

```bash
# Zkopírovat service soubor do systemd
sudo cp sensor-app.service /etc/systemd/system/

# Načíst novou službu
sudo systemctl daemon-reload

# Povolit automatický start při bootování
sudo systemctl enable sensor-app.service

# Spustit službu
sudo systemctl start sensor-app.service
```

### Užitečné příkazy

```bash
# Zobrazit stav služby (včetně watchdog info)
sudo systemctl status sensor-app.service

# Zobrazit logy aplikace
sudo journalctl -u sensor-app.service -f

# Zobrazit poslední logy
sudo journalctl -u sensor-app.service -n 50

# Restartovat službu
sudo systemctl restart sensor-app.service

# Zastavit službu
sudo systemctl stop sensor-app.service

# Zakázat automatický start
sudo systemctl disable sensor-app.service
```

### Testování watchdog

Pro otestování, že watchdog funguje, můžeš:

1. **Simulovat zamrznutí** - přidej do kódu nekonečný cyklus
2. **Zabít proces násilně**:
```bash
# Najít PID procesu
sudo systemctl status sensor-app.service

# Poslat SIGSTOP (zamrzne proces)
sudo kill -STOP <PID>

# Sledovat logy - systemd by měl po 30s aplikaci restartovat
sudo journalctl -u sensor-app.service -f
```

### Důležité poznámky

- **WatchdogSec=30** znamená, že aplikace musí poslat signál minimálně jednou za 30 sekund
- Aplikace posílá signály každých **15 sekund** (polovina timeoutu)
- **Type=notify** je nutný pro watchdog fungování
- Pokud watchdog není aktivní (spuštění mimo systemd), aplikace běží normálně