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
'''
two threads:
    one queries UART and puts incoming data into a global queue
    the other takes the queue and throws the data into the db
'''
dataQueue = Queue()
runID = -1
def getRunID():
    global runID
    with open("runid.txt","r+") as file:
        runID = int(file.readline())
        file.seek(0)
        file.write(str(runID+1))
        file.truncate()

def generateRandomData() -> tuple:
    return (random.randint(24,25))

def serialRunner():
    while True:
        with serial.Serial('/dev/ttyUSB0',115200,timeout=1) as ser:
            try:
                data = [float(x) for x in ser.readline().split()]
                dataQueue.put(data) 
            except:
                print("Bad data received")


def dbRunner():
    global runID
    while True:
        conn = connexion.connexion(connexion.DB_CONFIG)
        if not conn:
            print("Unable to establish DB connexion. Retrying")
            time.sleep(1)
            continue
        try:
            print("Connection success.")
            while True:
                if dataQueue:
                    data = dataQueue.get()
                    if len(data) == 0:
                        continue
                    print(data)
                    insert_query = f"INSERT INTO DataCapture (runID, seqnum, temperature,humidity, heatIndex, packetRSSI) VALUES (%s,%s,%s,%s,%s,%s)"
                    with conn.cursor() as cursor:
                        try:
                            cursor.execute(insert_query,(runID,data[0],data[1],data[2],data[3],data[4]))
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


def startThreads():
    getRunID()
    serial_thread = threading.Thread(target=serialRunner)
    db_thread = threading.Thread(target=dbRunner)
    serial_thread.start()
    db_thread.start()
    
if __name__ == "__main__":
    startThreads()