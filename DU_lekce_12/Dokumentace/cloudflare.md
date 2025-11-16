## Popis zprovoznění Cloudflare Autentifikace

Postup platí, pokud je již na Cloudflare zaregistrovaná doména

**1) Nastavení metod ověření**
a.  V Zero Trust / Settings / Authentication zpřístupníme pořadované metody: 
![alt text](/DU_lekce_12/Dokumentace/obrazky/image-2.png)
b.  Postupujeme podle instrukcí.

---
**2) Založení aplikace**
a. v záložce Access zadáme "Create an application"
b. zvolíme "Self-hosted" 
c. zadáme jméno aplikace a přidáme "Public hostname" 

![alt text](/DU_lekce_12/Dokumentace/obrazky/image-3.png)

d. Přidáme "Access policies". Pokud nemáme, vytvoříme

![alt text](/DU_lekce_12/Dokumentace/obrazky/image-4.png)

e. vybereme požadovanou metodu

![alt text](/DU_lekce_12/Dokumentace/obrazky/image-5.png)

f. další parametry nastavíme dle potřeby

---
**3) Nastavení Policies**
a.  Add policy
b.  Nastavíme požadovaná pravidla (například, že je umožněn přístup jen z ČR, určité domény apod.)

![alt text](/DU_lekce_12/Dokumentace/obrazky/image-6.png)

