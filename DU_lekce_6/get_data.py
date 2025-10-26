import adafruit_dht
import board
import time

# Inicializace DHT11 senzoru na pinu D4
dhtDevice = adafruit_dht.DHT11(board.D4)


def get_sensor_data():

    print("temperature:", dhtDevice.temperature)

    return {"temperature": dhtDevice.temperature, "humidity": dhtDevice.humidity}

    # try:
    #     temperature_c = dhtDevice.temperature
    #     humidity = dhtDevice.humidity
    #     print(f"Teplota: {temperature_c:.1f} °C, Vlhkost: {humidity}%")
    #     return {"temperature": temperature_c, "humidity": humidity}
    # except RuntimeError as error:
    #     print(f"Chyba při čtení senzoru: {error.args[0]}")
    #     return None
    # except Exception as error:
    #     dhtDevice.exit()
    #     raise error


if __name__ == "__main__":

    for _ in range(5):  # Získat data 5krát s pauzou mezi čteními
        get_sensor_data()

        time.sleep(1)  # Pauza mezi čteními

    dhtDevice.exit()  # Uvolnění zdrojů senzoru po dokončení
