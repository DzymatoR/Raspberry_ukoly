import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DB_NAME = "/home/dzymator/Documents/Raspberry_ukoly/Du_lekce_10/sensor_data.db"


# Načtení posledních dat z databáze
def get_latest_data(limit=20):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        f"SELECT timestamp, temperature, humidity FROM sensor_readings ORDER BY id DESC LIMIT {limit}"
    )
    rows = c.fetchall()
    conn.close()
    return rows


# Vytvoření grafu z dat
def create_graph(data):
    if not data:
        print("Žádná data v databázi")
        return None

    # Převod na DataFrame
    df = pd.DataFrame(data, columns=["timestamp", "temperature", "humidity"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")  # Seřadit podle času (od nejstarších)

    # Vytvoření kombinovaného grafu s oběma hodnotami
    fig = px.line(
        df,
        x="timestamp",
        y=["temperature", "humidity"],
        title="Historie teploty a vlhkosti (posledních 20 měření)",
        labels={"timestamp": "Čas", "value": "Hodnota", "variable": "Veličina"},
    )

    # Úprava legendy a vzhledu
    fig.data[0].name = "Teplota (°C)"
    fig.data[1].name = "Vlhkost (%)"

    # Nastavení barev
    fig.data[0].line.color = "red"
    fig.data[1].line.color = "blue"

    fig.update_layout(
        xaxis=dict(tickformat="%H:%M:%S", title="Čas"),
        yaxis_title="Hodnota",
        hovermode="x unified",
        template="plotly_white",
        font=dict(size=14),
        width=1000,
        height=600,
    )

    return fig


if __name__ == "__main__":
    # Načtení dat z databáze
    data = get_latest_data(limit=20)

    if not data:
        print("❌ Žádná data v databázi")
        exit(1)

    print(f"✓ Načteno {len(data)} záznamů z databáze")

    # Vytvoření grafu
    fig = create_graph(data)

    # Zobrazení grafu v prohlížeči
    fig.show()
