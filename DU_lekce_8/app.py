from flask import Flask, render_template
import time
import adafruit_dht
import board    


app = Flask(__name__)

# Na RPi4/5 je často nutné use_pulseio=False
dht = adafruit_dht.DHT11(board.D4, use_pulseio=False)

@app.get("/api/data")
def read_dht():

    try:
        # Senzor potřebuje čas na inicializaci
        time.sleep(2)
        t = dht.temperature
        h = dht.humidity
        return {"temperature": float(t), "humidity": float(h)}

    except RuntimeError as error:
        print(f"Chyba při čtení senzoru: {error.args[0]}")
        return {"temperature": None, "humidity": None}
    
@app.get("/")
def home():
    data = read_dht()
    return render_template(
        "index.html", temperature=data["temperature"], humidity=data["humidity"]
    )

# Spuštění aplikace
if __name__ == "__main__":
    app.run(debug=True, port = 1234)

