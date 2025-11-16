#!/usr/bin/env python3
"""
Testovací skript pro ověření funkčnosti loggingu.
Spustí: python3 test_logging.py
"""

import logging
from logging.handlers import TimedRotatingFileHandler
import os
import time

# Konfigurace loggeru
LOG_DIR = "/home/dzymator/Documents/Raspberry_ukoly/DU_lekce_12/logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Vytvoření složky pro logy
os.makedirs(LOG_DIR, exist_ok=True)

# Nastavení loggeru
logger = logging.getLogger("SensorApp")
logger.setLevel(logging.INFO)

# Handler pro rotaci logů
file_handler = TimedRotatingFileHandler(
    LOG_FILE, when="midnight", interval=1, backupCount=30, encoding="utf-8"
)
file_handler.setLevel(logging.INFO)

# Formát logu
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Přidat handler
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Test loggingu
print("Testování logging systému...\n")

logger.info("=" * 60)
logger.info("TEST: Spuštění aplikace Flask Sensor Monitoring")
logger.info("=" * 60)

time.sleep(0.5)
logger.info("TEST: Databáze inicializována")

time.sleep(0.5)
logger.info("TEST: Vlákno pro ukládání dat spuštěno")

time.sleep(0.5)
logger.info("TEST: Data uložena - Teplota: 23.5°C, Vlhkost: 65.2%")

time.sleep(0.5)
logger.info("TEST: Režim LED změněn na: ON (manuální)")

time.sleep(0.5)
logger.info("TEST: LED zapnuta - manuální režim")

time.sleep(0.5)
logger.info("TEST: Režim LED změněn na: AUTO (22°C)")

time.sleep(0.5)
logger.info("TEST: LED zapnuta - Auto režim (teplota 21.5°C <= 21°C)")

time.sleep(0.5)
logger.warning("TEST: Neplatný požadavek na změnu LED režimu: invalid_state")

time.sleep(0.5)
logger.error("TEST: Chyba při ukládání do databáze: disk I/O error")

time.sleep(0.5)
logger.info("TEST: Ukončení aplikace")
logger.info("=" * 60)

print(f"\nTest dokončen!")
print(f"Logy byly zapsány do: {LOG_FILE}")
print(f"\nZobrazit logy: cat {LOG_FILE}")
print(f"Sledovat logy: tail -f {LOG_FILE}")
