#!/usr/bin/env python3
"""
Skript pro bezpečné generování hashů hesel.
Použití: python3 generate_password_hash.py
"""

from werkzeug.security import generate_password_hash
import getpass

def main():
    print("=== Generátor hashe hesel ===\n")

    username = input("Zadej uživatelské jméno: ")
    password = getpass.getpass("Zadej heslo (nebude viditelné): ")
    password_confirm = getpass.getpass("Potvrď heslo: ")

    if password != password_confirm:
        print("❌ Hesla se neshodují!")
        return

    # Generování hashe
    password_hash = generate_password_hash(password)

    print("\n✅ Hash vygenerován!")
    print(f"\nPřidej tento řádek do app.py:")
    print(f'    "{username}": "{password_hash}",')
    print("\n⚠️  DŮLEŽITÉ: Nikdy nesdílej tento hash veřejně!")
    print("Hash je uložen pouze pro tento běh skriptu.\n")

if __name__ == "__main__":
    main()
