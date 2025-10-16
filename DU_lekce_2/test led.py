import gpiozero
import time 
from time import sleep

led = gpiozero.LED(14)

for i in range(5):
    led.on()
    print("LED ON 💡")
    sleep(1)
    led.off()
    print("LED OFF 💤" )

