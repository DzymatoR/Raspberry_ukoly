## Popis zprovoznění Cloudflare Autentifikace

Postup platí, pokud je již na Cloudflare zaregistrovaná doména

**1) Nastavení metod ověření**
a.  V Zero Trust / Settings / Authentication zpřístupníme pořadované metody: 
![alt text](image-2.png)
b.  Postupujeme podle instrukcí.

---
**2) Založení aplikace**
a. v záložce Access zadáme "Create an application"
b. zvolíme "Self-hosted" 
c. zadáme jméno aplikace a přidáme "Public hostname" 

![alt text](image-3.png)

d. Přidáme "Access policies". Pokud nemáme, vytvoříme

![alt text](image-4.png)

e. vybereme požadovanou metodu

![alt text](image-5.png)

f. další parametry nastavíme dle potřeby

---
**3) Nastavení Policies**
a.  Add policy
b.  Nastavíme požadovaná pravidla (například, že je umožněn přístup jen z ČR, určité domény apod.)

![alt text](image-6.png)

