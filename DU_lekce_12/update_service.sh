#!/bin/bash
# Skript pro aktualizaci rpdashboard.service na novou verzi s watchdog

echo "=========================================="
echo "Aktualizace rpdashboard.service"
echo "=========================================="
echo ""

# Kontrola, zda běžíme jako root
if [ "$EUID" -ne 0 ]; then
   echo "CHYBA: Tento skript musí být spuštěn s sudo"
   echo "Použití: sudo bash update_service.sh"
   exit 1
fi

# Zastavit aktuální službu
echo "1. Zastavuji aktuální službu..."
systemctl stop rpdashboard.service

# Zkopírovat nový service soubor
echo "2. Kopíruji nový service soubor..."
cp /home/dzymator/Documents/Raspberry_ukoly/DU_lekce_12/sensor-app.service /etc/systemd/system/rpdashboard.service

# Reload systemd daemon
echo "3. Načítám novou konfiguraci..."
systemctl daemon-reload

# Povolit službu (pokud ještě není)
echo "4. Povoluji automatický start při bootování..."
systemctl enable rpdashboard.service

# Spustit službu
echo "5. Spouštím aktualizovanou službu..."
systemctl start rpdashboard.service

# Zobrazit stav
echo ""
echo "=========================================="
echo "Stav služby:"
echo "=========================================="
systemctl status rpdashboard.service --no-pager

echo ""
echo "=========================================="
echo "Aktualizace dokončena!"
echo "=========================================="
echo ""
echo "Užitečné příkazy:"
echo "  - Zobrazit stav: sudo systemctl status rpdashboard.service"
echo "  - Zobrazit logy: sudo journalctl -u rpdashboard.service -f"
echo "  - Zobrazit soubor logů: tail -f /home/dzymator/Documents/Raspberry_ukoly/DU_lekce_12/logs/app.log"
echo ""
