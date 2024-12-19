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
    query = """SELECT runID, seqnum, capture_time FROM DataCapture ORDER BY runID, capture_time;"""
    
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                data = cur.fetchall()
                return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def analyze_packet_loss(data):
    """Analyzes packet loss and returns loss statistics."""
    packet_loss = {}

    # Group by runID
    runs = {}
    for runID, seqnum, capture_time in data:
        if runID not in runs:
            runs[runID] = []
        runs[runID].append((seqnum, capture_time))

    for runID, seq_data in runs.items():
        seq_data.sort(key=lambda x: x[1])  # Sort by capture_time
        seqnums = [item[0] for item in seq_data]
        times = [item[1] for item in seq_data]
        lost_packets = 0
        total_packets = seqnums[-1] - seqnums[0] + 1 if seqnums else 0

        for i in range(1, len(seqnums)):
            if seqnums[i] != seqnums[i - 1] + 1:
                lost_packets += seqnums[i] - seqnums[i - 1] - 1

        packet_loss[runID] = {
            "times": times,
            "loss_percentage": (lost_packets / total_packets) * 100 if total_packets > 0 else 0
        }

    return packet_loss

def plot_packet_loss(packet_loss):
    """Generates a graph of packet loss percentage over time."""
    for runID, loss_data in packet_loss.items():
        times = loss_data["times"]
        loss_percentage = loss_data["loss_percentage"]

        plt.figure()
        plt.title(f"Packet Loss Percentage Over Time for RunID {runID}")
        plt.xlabel("Time")
        plt.ylabel("Packet Loss Percentage (%)")
        plt.plot(times, [loss_percentage] * len(times), 'r-', label="Packet Loss %")
        plt.legend()
        plt.grid()
        plt.show()

if __name__ == "__main__":
    data = fetch_data()

    if data:
        packet_loss = analyze_packet_loss(data)
        plot_packet_loss(packet_loss)
    else:
        print("No data to analyze.")
