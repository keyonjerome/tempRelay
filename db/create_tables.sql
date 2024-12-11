CREATE TABLE DataCapture {
    runID SERIAL NOT NULL,
    seqnum SERIAL NOT NULL,
    timeCaptured timestamp CURRENT_DATE NOT NULL,
    temperature float NOT NULL,
    (runID,seqnum,timeCaptured) PRIMARY KEY
};