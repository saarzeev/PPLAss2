import csv
import sqlite3

class MyBackend():
    def __init__(self):
        self._conn = sqlite3.connect("lite.db")

    def initialize_db(self, path):
        self._create_table_in_db()
        self.load_csv_into_db(path)
        self._conn.commit()
        self._conn.close()

    def _create_table_in_db(self):
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS bikeShare (TripDuration INTEGER ,StartTime TIMESTAMP ,StopTime TIMESTAMP, StartStationID INTEGER, StartStationName TEXT, StartStationLatitude REAL, StartStationLongitude REAL, EndStationID INTEGER, EndStationName TEXT, EndStationLatitude REAL, EndStationLongitude REAL, BikeID INTEGER, UserType TEXT, BirthYear INTEGER, Gender INTEGER, TripDurationinmin INTEGER)")

    def load_csv_into_db(self, path):
        with open(path, 'r') as f:
            reader = csv.reader(f)
            columns = next(reader)
            query = 'insert into bikeShare({0}) values ({1})'
            query = query.format(','.join(columns), ','.join('?' * len(columns)))
            cursor = self._conn.cursor()
            for data in reader:
                cursor.execute(query, data)


nu = MyBackend()
nu.initialize_db("BikeShare.csv")
