from multiprocessing import Queue
import sys
import serial
import traceback
import threading
import random
import time
import psycopg2
sys.path.append("..")
import connexion
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
'''
two threads:
    one queries UART and puts incoming data into a global queue
    the other takes the queue and throws the data into the db
'''
dataQueue = Queue()
runID = -1
distance = 0
conn = None
def getRunID():
    global runID
    with open("runid.txt","r+") as file:
        runID = int(file.readline())
        file.seek(0)
        file.write(str(runID+1))
        file.truncate()

packets = 0
packets_lost = 0
# def calculate_packet_loss(seqnums):
#     """Calculate packet loss percentage based on sequence numbers."""
#     if len(seqnums) < 2:
#         return []
#     total_packets = seqnums[-1] - seqnums[0] + 1
#     received_packets = len(seqnums)
#     loss_percentage = ((total_packets - received_packets) / total_packets) * 100 if total_packets > 0 else 0
#     return [loss_percentage] * len(seqnums)

def serialRunner():
    while True:
        with serial.Serial('/dev/ttyUSB0',115200,timeout=1) as ser:
            try:
                data = [float(x) for x in ser.readline().split()]
                dataQueue.put(data) 
            except:
                print("Bad data received")

def connect():
    global conn
    while not conn:
        conn = connexion.connexion(connexion.DB_CONFIG)
        if not conn:
            print("Unable to establish DB connexion. Retrying")
            time.sleep(1)
            continue

def dbRunner():
    global runID
    global conn
    global distance
    global packets
    global packets_lost
    last_seq = -1
    while not conn:
        print("dbRunner() waiting for connection")
        time.sleep(1)
    while conn:
        if dataQueue:
            data = dataQueue.get()
            if len(data) == 0:
                continue
            print(data)
            packets+=1
            insert_query = f"INSERT INTO DataCapture (runID, distance, seqnum, temperature,humidity, heatIndex, packetRSSI,packets, packet_loss) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            if last_seq == -1:
                last_seq = data[0]
                print(-1,data[0])
            else:
                packets_lost += data[0] - last_seq - 1 if  data[0] - last_seq - 1 > 0 else 0
                print(packets_lost)
                last_seq = data[0]
            with conn.cursor() as cursor:
                try:
                    cursor.execute(insert_query,(runID,distance,data[0],data[1],data[2],data[3],data[4],packets,packets_lost))
                    conn.commit()
                    # si insertion d'un mauvais type
                except psycopg2.DataError as e:
                    conn.rollback()
                    traceback.print_exc()
                    print("Contrainte non respectée")
                    print("message système : ",e)

                except psycopg2.IntegrityError as e:
                    conn.rollback()
                    traceback.print_exc()
                    print("message système : ",e)

                except ValueError as e:
                    conn.rollback()
                    traceback.print_exc()
                    print("message système : ",e)
                except Exception as e:
                    traceback.print_exc()
                    conn.close()
    print("Connection closed")

def liveGraph():
    global conn
    global runID
    while not conn:
        print("liveGraph() waiting for connection")
        time.sleep(1)

    def fetch_latest_data():
        """Fetch the latest data from the database."""
        query = f"""
        SELECT capture_time, seqnum, temperature, humidity, heatIndex, packetRSSI, packets, packet_loss
        FROM DataCapture
        WHERE runID = {runID}
        ORDER BY capture_time DESC
        LIMIT 100;
        """
        try:
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
                return rows[::-1]  # Reverse to get chronological order
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return []

    # Initialize data storage
    capture_times = []
    temperatures = []
    humidities = []
    heat_indices = []
    packet_rssis = []

    def update_graph(frame):
        """Update the graph with the latest data."""
        global capture_times, sequence_numbers, temperatures, humidities, heat_indices, packet_rssis

        # Fetch latest data
        data = fetch_latest_data()
        if not data:
            return

        # Unpack data
        capture_times = [row[0] for row in data]
        sequence_numbers = [row[1] for row in data]
        temperatures = [row[2] for row in data]
        humidities = [row[3] for row in data]
        heat_indices = [row[4] for row in data]
        packet_rssis = [row[5] for row in data]
        packet_loss_percent = [row[7]/row[6] for row in data]

        # Calculate packet loss
        #packet_loss = calculate_packet_loss(sequence_numbers)

        # Clear and redraw subplots
        ax1.clear()
        ax2.clear()
        ax3.clear()
        ax4.clear()
        ax5.clear()

        ax1.plot(capture_times, temperatures, label="Temperature", color="red")
        ax2.plot(capture_times, humidities, label="Humidity", color="blue")
        ax3.plot(capture_times, heat_indices, label="Heat Index", color="orange")
        ax4.plot(capture_times, packet_rssis, label="Packet RSSI", color="green")
        ax5.plot(capture_times,packet_loss_percent,label="Packet Loss %",color="purple")

        # Format plots
        for ax in [ax1, ax2, ax3, ax4, ax5]:
            ax.legend(loc="upper right")
            ax.set_xlabel("Time")
            ax.tick_params(axis="x", rotation=45)

        ax1.set_ylabel("Temperature")
        ax2.set_ylabel("Humidity")
        ax3.set_ylabel("Heat Index")
        ax4.set_ylabel("Packet RSSI")
        ax5.set_ylabel("Packet Loss %")

    # Create figure and subplots
    fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1, figsize=(10, 10), sharex=True)
    fig.tight_layout(pad=3.0)

    # Set up animation
    ani = animation.FuncAnimation(fig, update_graph, interval=1000)

    # Display the plot
    plt.show()

def startThreads():
    global distance
    distance = float(input("Distance (m): "))
    getRunID()
    serial_thread = threading.Thread(target=serialRunner)
    db_thread = threading.Thread(target=dbRunner)
    graph_thread = threading.Thread(target=liveGraph)
    connect()
    graph_thread.start()
    serial_thread.start()
    db_thread.start()
    
if __name__ == "__main__":
    startThreads()