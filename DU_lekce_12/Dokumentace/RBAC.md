# Role-based Access Control (RBAC)

## Přehled

Aplikace implementuje systém řízení přístupu založený na rolích (RBAC), který umožňuje různým uživatelům mít různé úrovně přístupu k funkcím aplikace.

## Role

### 1. Admin
- **Popis**: Plný přístup ke všem funkcím aplikace
- **Oprávnění**:
  - ✅ Zobrazení aktuálních dat
  - ✅ Zobrazení historie měření
  - ✅ Zobrazení grafu
  - ✅ Ovládání LED
- **Přihlašovací údaje**:
  - Uživatelské jméno: `admin`
  - Heslo: `admin123`

### 2. User
- **Popis**: Běžný uživatel s možností čtení dat a historie (bez ovládání LED)
- **Oprávnění**:
  - ✅ Zobrazení aktuálních dat
  - ✅ Zobrazení historie měření
  - ✅ Zobrazení grafu
  - ❌ Ovládání LED
- **Přihlašovací údaje**:
  - Uživatelské jméno: `user`
  - Heslo: `user123`

### 3. Viewer
- **Popis**: Pouze prohlížení aktuálních dat, bez přístupu k historii a ovládání
- **Oprávnění**:
  - ✅ Zobrazení aktuálních dat
  - ❌ Zobrazení historie měření
  - ❌ Zobrazení grafu
  - ❌ Ovládání LED
- **Přihlašovací údaje**:
  - Uživatelské jméno: `viewer`
  - Heslo: `viewer123`

## Implementace

### Backend (app.py)

#### Struktura uživatelů
```python
users = {
    "admin": {
        "password_hash": "pbkdf2:sha256:...",
        "role": "admin"
    },
    # ... další uživatelé
}
```

#### Definice oprávnění
```python
ROLES = {
    "admin": {
        "can_view_data": True,
        "can_view_history": True,
        "can_view_graph": True,
        "can_control_led": True,
        "description": "Plný přístup ke všem funkcím"
    },
    # ... další role
}
```

#### Pomocné funkce

##### `get_user_role(username)`
Vrátí roli uživatele na základě uživatelského jména.

##### `has_permission(username, permission)`
Zkontroluje, zda má uživatel dané oprávnění.

##### `@require_permission(permission)`
Dekorátor pro Flask routy, který kontroluje oprávnění před zpracováním požadavku.

### API Endpointy s ochranou

#### `/` (GET)
- Vyžaduje autentifikaci
- Předává informace o uživateli a oprávněních do šablony

#### `/api/data` (GET)
- Vyžaduje oprávnění: `can_view_data`
- Filtruje historii podle oprávnění `can_view_history`

#### `/api/led` (POST)
- Vyžaduje oprávnění: `can_control_led`
- Loguje uživatele, který změnil stav LED

#### `/api/graph` (GET)
- Vyžaduje oprávnění: `can_view_graph`

### Frontend (index.html)

Šablona používá Jinja2 podmínky pro zobrazení/skrytí UI elementů:

```html
{% if permissions.can_control_led %}
    <!-- LED ovládání -->
{% else %}
    <!-- Zpráva o nedostatečných oprávněních -->
{% endif %}
```

JavaScript používá stejné oprávnění pro inicializaci event listenerů:

```javascript
const permissions = {
    can_view_history: {{ permissions.can_view_history|tojson }},
    can_view_graph: {{ permissions.can_view_graph|tojson }},
    can_control_led: {{ permissions.can_control_led|tojson }}
};
```

## Přidání nového uživatele

### 1. Vygenerování hashe hesla

```bash
python3 generate_password_hash.py
```

Zadejte uživatelské jméno a heslo. Skript vygeneruje hash.

### 2. Přidání do app.py

```python
users = {
    # ... existující uživatelé
    "novy_uzivatel": {
        "password_hash": "pbkdf2:sha256:260000$...",
        "role": "user"  # nebo "admin", "viewer"
    },
}
```

### 3. Restart služby

```bash
sudo systemctl restart rpdashboard.service
```

## Přidání nové role

### 1. Definice role v app.py

```python
ROLES = {
    # ... existující role
    "nova_role": {
        "can_view_data": True,
        "can_view_history": True,
        "can_view_graph": False,
        "can_control_led": False,
        "description": "Popis nové role"
    },
}
```

### 2. Přiřazení role uživateli

```python
users = {
    "uzivatel": {
        "password_hash": "...",
        "role": "nova_role"
    },
}
```

## Bezpečnostní funkce

1. **HTTP Basic Authentication**: Všechny routy vyžadují autentifikaci
2. **Password Hashing**: Hesla jsou ukládána pomocí PBKDF2-SHA256
3. **Permission Checks**: Server-side kontrola oprávnění před provedením akce
4. **Logging**: Všechny pokusy o přístup bez oprávnění jsou logovány
5. **Frontend Protection**: UI elementy jsou skryty pro uživatele bez oprávnění

## Testování RBAC

### Test jako Admin
```bash
curl -u admin:admin123 http://localhost:5000/api/data
```
Měl by vrátit data včetně historie.

### Test jako Viewer
```bash
curl -u viewer:viewer123 http://localhost:5000/api/data
```
Měl by vrátit data, ale prázdné pole historie.

### Test ovládání LED jako Viewer
```bash
curl -u viewer:viewer123 -X POST -H "Content-Type: application/json" \
  -d '{"state":"on"}' http://localhost:5000/api/led
```
Měl by vrátit chybu 403 Forbidden.

## Logy oprávnění

V logu (`logs/app.log`) se zobrazují:
- Zamítnuté přístupy s informací o chybějícím oprávnění
- Uživatel, který změnil stav LED

Příklad:
```
2025-11-16 17:14:25 - WARNING - Zamítnut přístup pro viewer - chybí oprávnění: can_control_led
2025-11-16 17:15:30 - INFO - Režim LED změněn na: ON (manuální) - uživatel: admin
```

## Rozšíření oprávnění

Pro přidání nového oprávnění:

1. Přidat do definice ROLES
2. Přidat dekorátor k příslušné route
3. Aktualizovat frontend pro zobrazení/skrytí UI
4. Aktualizovat dokumentaci

Příklad nového oprávnění `can_export_data`:
```python
ROLES = {
    "admin": {
        # ... existující oprávnění
        "can_export_data": True
    },
    "user": {
        # ... existující oprávnění
        "can_export_data": False
    },
}

@app.get("/api/export")
@auth.login_required
@require_permission("can_export_data")
def export_data():
    # Export dat
    pass
```
