import gpiozero
from time import sleep

led = gpiozero.LED(15)

for i in range(5):
    led.on()
    print("LED ON 💡")
    sleep(1)
    led.off()
    print("LED OFF 💤" )
    sleep(1)
