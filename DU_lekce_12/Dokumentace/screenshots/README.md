# Screenshots Guide

Tato složka obsahuje screenshoty aplikace pro dokumentaci.

## Jak pořídit screenshoty

### 1. Spusť aplikaci
```bash
sudo systemctl start rpdashboard.service
```

### 2. Otevři prohlížeč
Navštiv `http://localhost:5000` (nebo Cloudflare Tunnel URL)

### 3. Pořiď screenshoty pro každou roli

#### Admin Dashboard
1. Přihlas se jako: `admin` / `admin123`
2. Počkej na načtení dat
3. Poři screenshot celé stránky
4. Ulož jako: `admin-dashboard.png`

#### User Dashboard
1. Odhlásit se (zavřít všechna okna prohlížeče)
2. Otevři anonymní okno
3. Přihlas se jako: `user` / `user123`
4. Počkej na načtení dat
5. Poři screenshot celé stránky
6. Ulož jako: `user-dashboard.png`

#### Viewer Dashboard
1. Otevři další anonymní okno
2. Přihlas se jako: `viewer` / `viewer123`
3. Počkej na načtení dat
4. Poři screenshot celé stránky
5. Ulož jako: `viewer-dashboard.png`

### 4. Dodatečné screenshoty (volitelné)

#### LED Ovládání - Detail
- Screenshot pouze sekce LED ovládání
- Ukázat Auto režim s nastavenou teplotou
- Ulož jako: `led-control-detail.png`

#### Graf - Detail
- Screenshot pouze grafu
- Ukázat hover efekt s hodnotami
- Ulož jako: `graph-detail.png`

#### Přihlašovací dialog
- Screenshot HTTP Basic Auth dialogu
- Ulož jako: `login-dialog.png`

#### Mobilní view
- Zmenši okno prohlížeče na 400px šířku
- Screenshot responzivního layoutu
- Ulož jako: `mobile-view.png`

## Nástroje pro screenshots

### Linux (Raspberry Pi)
```bash
# Gnome Screenshot
gnome-screenshot -w -f admin-dashboard.png

# Scrot
scrot -s admin-dashboard.png

# Flameshot (recommended)
sudo apt install flameshot
flameshot gui
```

### Alternativa: Browser Extensions
- **Firefox:** Shift+F2 → `screenshot --fullpage --filename admin-dashboard.png`
- **Chrome:** F12 → Ctrl+Shift+P → "Capture full size screenshot"

## Optimalizace obrázků

Po pořízení screenshotů je doporučeno je optimalizovat:

```bash
# Instalace ImageMagick
sudo apt install imagemagick

# Komprese PNG
mogrify -quality 85 -resize 1920x1080\> *.png

# Nebo použij online nástroj:
# https://tinypng.com/
```

## Checklist

- [x] admin-dashboard.png
- [x] user-dashboard.png
- [x] viewer-dashboard.png
- [x] led-control-detail.png (volitelné)
- [x] graph-detail.png (volitelné)
- [x] login-dialog.png (volitelné)
- [x] mobile-view.png (volitelné)

## Rozměry

Doporučené rozměry screenshotů:
- **Celý dashboard:** 1920x1080 (Full HD)
- **Detaily:** 1200x800
- **Mobilní:** 400x800

## Formát

- **Formát:** PNG (kvůli kvalitě)
- **Komprese:** 85% quality
- **Naming:** lowercase-with-dashes.png

## Poznámky

- Screenshot by měl obsahovat reálná data (ne placeholder hodnoty)
- Graf by měl mít viditelné křivky (alespoň několik hodin dat)
- Ujisti se, že je vidět uživatelské jméno a role v pravém horním rohu
- Pro viewer screenshot zkontroluj, že jsou vidět disabled sekce s informačními zprávami

---

**Po pořízení screenshotů je aktualizuj v README.md:**

```markdown
![Admin Dashboard](Dokumentace/screenshots/admin-dashboard.png)
```
