# Přehled implementovaných funkcí

## Základní funkce

### 1. Senzor DHT11
- ✅ Čtení teploty a vlhkosti každých 30 sekund
- ✅ Ukládání dat do SQLite databáze
- ✅ Zobrazení aktuálních hodnot na webové stránce

### 2. LED ovládání
- ✅ Manuální zapnutí/vypnutí
- ✅ Auto režim (termostat) s nastavitelnou teplotou
- ✅ Hystereze ±1°C pro stabilní chování

### 3. Webové rozhraní
- ✅ Moderní responzivní design
- ✅ Real-time zobrazení teploty a vlhkosti
- ✅ Ovládání LED přes webové rozhraní
- ✅ Graf posledních 24 hodin (Plotly)
- ✅ Tabulka s historií posledních 10 měření
- ✅ Automatická aktualizace každé 2 minuty

### 4. HTTP Basic Authentication
- ✅ Ochrana všech endpointů
- ✅ Bezpečné ukládání hesel pomocí PBKDF2-SHA256
- ✅ Utility skript pro generování hashů hesel

## Pokročilé funkce

### 5. Systemd Watchdog
- ✅ Automatické sledování běhu aplikace
- ✅ Restart při pádu nebo zmrznutí (30s timeout)
- ✅ Heartbeat notifikace každých 15 sekund
- ✅ Systemd Type=notify služba

**Soubory**:
- [sensor-app.service](../sensor-app.service) - Systemd service s watchdog konfigurací
- [update_service.sh](../update_service.sh) - Automatizační skript pro update služby
- [Dokumentace/SystemD a Watchdog.md](SystemD%20a%20Watchdog.md) - Detailní dokumentace

### 6. Comprehensive Logging
- ✅ Logování všech důležitých událostí
- ✅ Automatická rotace logů každý den
- ✅ Uchovávání posledních 30 dní
- ✅ Strukturovaný formát s časovými razítky
- ✅ Různé úrovně logování (INFO, WARNING, ERROR, CRITICAL)

**Co se loguje**:
- Spuštění a ukončení aplikace
- Úspěšné uložení dat do databáze
- Změny stavu LED (manuální i auto režim)
- Chyby při čtení senzoru nebo ukládání dat
- Zamítnuté přístupy (RBAC)
- Uživatelské akce (kdo změnil LED)

**Soubory**:
- `logs/app.log` - Aktuální log
- `logs/app.log.YYYY-MM-DD` - Rotované logy
- [Dokumentace/Logování.md](Logování.md) - Dokumentace loggingu

### 7. Role-based Access Control (RBAC) ⭐ BONUS
- ✅ Tři úrovně přístupu: Admin, User, Viewer
- ✅ Granulární oprávnění pro každou funkci
- ✅ Server-side i client-side ochrana
- ✅ Logování pokusů o neoprávněný přístup
- ✅ Dynamické skrývání/zobrazování UI elementů

**Role a oprávnění**:

| Role   | Aktuální data | Historie | Graf | Ovládání LED |
|--------|---------------|----------|------|--------------|
| Admin  | ✅            | ✅       | ✅   | ✅           |
| User   | ✅            | ✅       | ✅   | ✅           |
| Viewer | ✅            | ❌       | ❌   | ❌           |

**Přihlašovací údaje**:
- Admin: `admin` / `admin123`
- User: `user` / `user123`
- Viewer: `viewer` / `viewer123`

**Soubory**:
- [Dokumentace/RBAC.md](RBAC.md) - Kompletní dokumentace RBAC
- [Dokumentace/Bezpečnost.md](Bezpečnost.md) - Bezpečnostní praktiky

## Bezpečnostní funkce

### 8. Password Security
- ✅ PBKDF2-SHA256 hash algoritmus
- ✅ 260,000 iterací pro ochranu proti brute-force
- ✅ Nikdy neukládat hesla v plaintextu
- ✅ Utility pro bezpečné generování hashů

**Soubory**:
- [generate_password_hash.py](../generate_password_hash.py) - Generátor hashů

### 9. API Security
- ✅ HTTP Basic Authentication na všech endpointech
- ✅ RBAC kontroly před provedením akce
- ✅ Validace vstupních dat
- ✅ Rate limiting pomocí watchdog timeout

## Infrastruktura

### 10. Cloudflare Tunnel
- ✅ HTTPS přístup z internetu
- ✅ Automatické SSL certifikáty
- ✅ Ochrana před DDoS útoky
- ✅ HTTP Basic Auth před Cloudflare Access

### 11. Git & Verzování
- ✅ `.gitignore` pro logy, databázi, cache
- ✅ Verzovaný zdrojový kód
- ✅ Dokumentace v Markdown

## Soubory projektu

```
DU_lekce_12/
├── app.py                          # Hlavní aplikace
├── generate_password_hash.py       # Generátor hashů hesel
├── requirements.txt                # Python závislosti
├── sensor-app.service             # Systemd service (příklad)
├── update_service.sh              # Skript pro update služby
├── .gitignore                     # Git ignorované soubory
├── templates/
│   └── index.html                 # Webové rozhraní
├── logs/                          # Logy (ignorováno gitem)
│   ├── app.log                    # Aktuální log
│   └── app.log.*                  # Rotované logy
├── sensor_data.db                 # SQLite databáze (ignorováno)
└── Dokumentace/
    ├── Implementovane_funkce.md   # Tento soubor
    ├── RBAC.md                    # Dokumentace RBAC
    ├── Bezpečnost.md              # Bezpečnostní praktiky
    ├── Logování.md                # Dokumentace loggingu
    └── SystemD a Watchdog.md      # Watchdog dokumentace
```

## Statistiky

- **Počet řádků kódu (app.py)**: ~477 řádků
- **Počet API endpointů**: 4
- **Počet rolí**: 3
- **Počet oprávnění**: 4
- **Retention logů**: 30 dní
- **Interval sběru dat**: 30 sekund
- **Interval aktualizace UI**: 2 minuty
- **Graf zobrazuje**: 24 hodin

## Testování

### Otestování RBAC
```bash
# Test jako admin (měl by vidět vše)
curl -u admin:admin123 http://localhost:5000/api/data

# Test jako viewer (neměl by vidět historii)
curl -u viewer:viewer123 http://localhost:5000/api/data

# Test ovládání LED jako viewer (měl by dostat 403)
curl -u viewer:viewer123 -X POST -H "Content-Type: application/json" \
  -d '{"state":"on"}' http://localhost:5000/api/led
```

### Otestování watchdog
```bash
# Zjištění PID procesu
sudo systemctl status rpdashboard.service | grep "Main PID"

# "Zabití" procesu (simulace pádu)
sudo kill -9 <PID>

# Systemd by měl automaticky restartovat službu do 30 sekund
sudo journalctl -u rpdashboard.service -f
```

### Sledování logů
```bash
# Real-time monitoring
tail -f logs/app.log

# Filtrování chyb
grep ERROR logs/app.log

# Zobrazení posledních 50 řádků
tail -n 50 logs/app.log
```

## Možná rozšíření (pro budoucnost)

- [ ] Email notifikace při kritických hodnotách
- [ ] Databázový backend pro uživatele (místo slovníku)
- [ ] API klíče místo Basic Auth
- [ ] Export dat do CSV/JSON
- [ ] Mobilní aplikace
- [ ] Push notifikace
- [ ] Více senzorů (DHT22, BME280)
- [ ] Podpora více LED/relé
- [ ] Časové plánování (cron-like)
- [ ] Webové rozhraní pro správu uživatelů

## Získané znalosti

### Technologie
- Flask framework a routing
- Jinja2 templating
- SQLite databáze
- Systemd služby a watchdog
- Python threading
- HTTP Basic Authentication
- PBKDF2-SHA256 hashing
- Role-based Access Control
- Plotly graphing
- Responsive web design

### Best practices
- Secure password storage
- Logging a monitoring
- Service reliability (watchdog)
- Access control patterns
- Code organization
- Documentation
- Git workflow

## Závěr

Projekt implementuje komplexní systém pro monitorování senzorů s pokročilými funkcemi jako:
- Systemd watchdog pro spolehlivost
- Comprehensive logging pro debugging
- **RBAC pro granulární řízení přístupu (BONUS ⭐)**
- Moderní webové rozhraní
- Bezpečné ukládání hesel

Všechny funkce jsou plně otestované a dokumentované.
