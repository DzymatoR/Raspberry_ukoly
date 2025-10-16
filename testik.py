from gpiozero import LED
from signal import pause
from time import sleep

import os
os.environ.setdefault("GPIOZERO_PIN_FACTORY", "lgpio")


# LED připojena na pin BCM 14 (fyzický pin 8)
led = LED(14)

print("Test LED – připojena na pin 14 (BCM).")
print("Blikám každou sekundu. Ukonči pomocí Ctrl+C.\n")

try:
    while True:
        led.on()
        print("LED ON 💡")
        sleep(1)
        led.off()
        print("LED OFF 💤")
        sleep(1)

except KeyboardInterrupt:
    led.off()
    print("\nTest ukončen. LED vypnuta bezpečně.")
