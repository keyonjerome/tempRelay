CREATE TABLE DataCapture (
    runID SERIAL NOT NULL,
    seqnum INT NOT NULL,
    temperature FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    heatIndex FLOAT NOT NULL,
    packetRSSI FLOAT NOT NULL,
    capture_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (runID, seqnum, capture_time)
);
