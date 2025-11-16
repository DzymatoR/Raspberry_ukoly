# Bezpečnost aplikace

## Autentizace

Aplikace používá **HTTP Basic Authentication** s hashem hesel pomocí `werkzeug.security`.

### Důležité bezpečnostní zásady

#### ❌ NIKDY NEDĚLEJ:
```python
# ŠPATNĚ - heslo v plaintextu v kódu!
users = {
    "admin": generate_password_hash("heslo123"),
}
```

#### ✅ SPRÁVNĚ:
```python
# Hash vygenerovaný jednou pomocí generate_password_hash.py
users = {
    "admin": "pbkdf2:sha256:260000$...",
}
```

## Změna hesel

### 1. Vygeneruj nový hash

Spusť skript pro generování hashe:

```bash
python3 generate_password_hash.py
```

Skript bezpečně požádá o heslo (nebude viditelné při psaní):

```
=== Generátor hashe hesel ===

Zadej uživatelské jméno: admin
Zadej heslo (nebude viditelné):
Potvrď heslo:

✅ Hash vygenerován!

Přidej tento řádek do app.py:
    "admin": "pbkdf2:sha256:260000$xyz...",
```

### 2. Aktualizuj app.py

Zkopíruj vygenerovaný hash do [app.py](../app.py) (řádky 54-57):

```python
users = {
    "admin": "pbkdf2:sha256:260000$nový_hash...",
    "user": "pbkdf2:sha256:260000$existující_hash...",
}
```

### 3. Restartuj službu

```bash
sudo systemctl restart rpdashboard.service
```

## Aktuální uživatelé

| Username | Heslo (pouze pro vývoj) | Role |
|----------|-------------------------|------|
| admin | heslo123 | Plný přístup |
| user | user123 | Čtení + ovládání |

**⚠️ DŮLEŽITÉ**: Změň výchozí hesla před nasazením do produkce!

## Hashování hesel

Aplikace používá **PBKDF2-SHA256** s 260 000 iteracemi:
- Algorimus: PBKDF2 (Password-Based Key Derivation Function 2)
- Hash funkce: SHA-256
- Iterace: 260 000 (pomalé pro útočníka, rychlé pro legitimního uživatele)
- Salt: Automaticky generovaný náhodný řetězec

### Příklad hashe:
```
pbkdf2:sha256:260000$Suh8A278xc8IirRA$0b88a3f38bd81415a62f464a8d3ad1812092a61879974cb0ecd77af0a5d689c2
|       |      |      |                 |
|       |      |      |                 +-- Hash (64 znaků hex)
|       |      |      +-- Salt (16 znaků)
|       |      +-- Počet iterací
|       +-- Hash algoritmus
+-- Metoda (PBKDF2)
```

## Bezpečnostní doporučení

### Pro produkční nasazení:

1. **Změň výchozí hesla**
   ```bash
   python3 generate_password_hash.py
   ```

2. **Použij HTTPS** (nikoliv HTTP)
   - Basic Auth posílá credentials v každém requestu
   - Bez HTTPS jsou credentials v plaintextu po síti

3. **Přesuň credentials do environment variables**
   ```python
   users = {
       os.environ.get("ADMIN_USER"): os.environ.get("ADMIN_HASH"),
   }
   ```

4. **Používej databázi pro uživatele**
   - Větší flexibilita
   - Možnost přidávat uživatele bez restartu
   - Auditní log změn

5. **Implementuj rate limiting**
   - Ochrana proti brute-force útokům
   - Flask-Limiter: `@limiter.limit("5 per minute")`

6. **Přidej CSRF ochranu**
   - Flask-WTF pro formuláře
   - Tokeny pro POST požadavky

7. **Loguj přihlašovací pokusy**
   - Úspěšné i neúspěšné
   - IP adresy
   - Timestamp

## Cloudflare ochrana

Aplikace je vystavena přes **Cloudflare Tunnel**, který poskytuje:
- ✅ Automatický HTTPS
- ✅ DDoS ochrana
- ✅ Rate limiting na úrovni CDN
- ✅ Skrytá IP adresa serveru
- ✅ Web Application Firewall (WAF)

## Další bezpečnostní prvky

### Systemd watchdog
- Automatický restart při pádu
- Monitoring stavu aplikace
- Detekce zamrznutí

### Logování
- Všechny důležité události
- Rotace logů (30 dní)
- Audit trail pro změny LED

### Firewall
Doporučená pravidla pro `ufw`:

```bash
# Povolit pouze SSH a Cloudflare tunnel
sudo ufw allow 22/tcp
sudo ufw enable
```

Flask běží pouze na `127.0.0.1:5000` (localhost) - nepřístupný z internetu přímo.

## Kontrolní seznam

- [x] Hesla jsou hashována
- [x] Hesla nejsou v plaintextu v kódu
- [x] Aplikace běží pouze na localhost
- [x] Cloudflare poskytuje HTTPS
- [x] Watchdog monitoruje stav aplikace
- [x] Logy jsou zabezpečeny (chmod 640)
- [ ] Změněna výchozí hesla (před produkcí!)
- [ ] Implementován rate limiting (doporučeno)
- [ ] Database-backed users (doporučeno pro více uživatelů)
