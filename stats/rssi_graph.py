
import psycopg2
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Database connection configuration
DB_CONFIG = {
    'dbname': 'mydb',
    'user': 'me',
    'password': 'secret',
    'host': 'localhost',
}

def fetch_data():
    """Fetches all data from the DataCapture table."""
    query = """SELECT runID, seqnum, capture_time, temperature, humidity, heatIndex, packetRSSI FROM DataCapture ORDER BY runID, capture_time;"""
    
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                data = cur.fetchall()
                return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def get_last_run_data(data):
    """Filters data for the last runID."""
    if not data:
        return []

    last_runID = max(row[0] for row in data)
    return [row for row in data if row[0] == last_runID]

def plot_last_run(data):
    """Generates subplots for the last runID showing humidity, temperature, and heat index."""
    if not data:
        print("No data available for the last run.")
        return

    capture_times = [row[2] for row in data]
    temperatures = [row[3] for row in data]
    humidities = [row[4] for row in data]
    heat_indices = [row[5] for row in data]

    plt.figure(figsize=(10, 8))

    # Temperature subplot
    plt.subplot(3, 1, 1)
    plt.plot(capture_times, temperatures, 'r-', label="Temperature")
    plt.title("Temperature Over Time")
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.legend()
    plt.grid()

    # Humidity subplot
    plt.subplot(3, 1, 2)
    plt.plot(capture_times, humidities, 'b-', label="Humidity")
    plt.title("Humidity Over Time")
    plt.xlabel("Time")
    plt.ylabel("Humidity (%)")
    plt.legend()
    plt.grid()

    # Heat index subplot
    plt.subplot(3, 1, 3)
    plt.plot(capture_times, heat_indices, 'g-', label="Heat Index")
    plt.title("Heat Index Over Time")
    plt.xlabel("Time")
    plt.ylabel("Heat Index")
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.show()

def plot_rssi_last_run(data):
    """Generates a graph for the RSSI of the last runID."""
    if not data:
        print("No data available for the last run.")
        return

    capture_times = [row[2] for row in data]
    rssi_values = [row[6] for row in data]

    plt.figure(figsize=(10, 5))
    plt.plot(capture_times, rssi_values, 'm-', label="Packet RSSI")
    plt.title("Packet RSSI Over Time for Last RunID")
    plt.xlabel("Time")
    plt.ylabel("RSSI (dB)")
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
    data = fetch_data()

    if data:
        last_run_data = get_last_run_data(data)
        plot_last_run(last_run_data)
        plot_rssi_last_run(last_run_data)
    else:
        print("No data to analyze.")
