from multiprocessing import Queue
import threading
import random
import time
'''
two threads:
    one queries UART and puts incoming data into a global queue
    the other takes the queue and throws the data into the db
'''
dataQueue = Queue()
runID = -1
def getRunID():
    global runID
    with open("runid.txt","wr") as file:
        runID = int(file.readline())
        file.write(runID+1)

def generateRandomData() -> tuple:
    return (random.randint(24,25))

def UARTRunner():
    while True:
        dataQueue.put(generateRandomData())
        time.sleep(1)

def dbRunner():
    while True:
        if dataQueue:
            data = dataQueue.get()

def startThreads():
    
    getRunID()
    uart_thread = threading.Thread(target=UARTRunner)
    
if __name__ == "__main__":
    main()return