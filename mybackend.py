import csv
import sqlite3
import numpy as np
import pandas as pd

class MyBackend:
    def __init__(self):
        self._conn = sqlite3.connect("lite.db")

    def initialize_db(self, path):
        self._create_table_in_db()
        self.load_csv_into_db(path)
        self._conn.commit()
        #self._conn.close()

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

    def get_recommendations(self, starting_location, time, num_of_recommendations):
        df = self._load_data_from_db(starting_location, time)
        recommendations = self._create_recommendations(df, time, starting_location, num_of_recommendations)
        return recommendations

    def _load_data_from_db(self, starting_location, time):
        delta_time_percentage = 0.1

        #Select all trips that have a duration within +-delta_time_percentage of the requested time.
        query = "SELECT * FROM bikeShare"
        cursor = self._conn.execute(query)

        #Construct dataframe
        cols = [column[0] for column in cursor.description]
        df = pd.DataFrame.from_records(data=cursor.fetchall(), columns=cols)
        return df

    def _create_recommendations(self, df, time, starting_location, num_of_recommendations):
        start_location_df = df[df['StartStationName'] == starting_location]

        if len(start_location_df) == 0:
            return None

        df = self._filter_distance_parameter(df, start_location_df)
        df = self._score_trips(df, time)
        df.sort_values(by=['score'], ascending=False, inplace=True)

        df = df.head(num_of_recommendations)
        return df

    def _filter_distance_parameter(self, df, start_location_df):
        x = start_location_df.iloc()[0]['StartStationLatitude']  # Get the requested starting point's latitude
        y = start_location_df.iloc()[0]['StartStationLongitude']  # Get the requested starting point's longitude
        # Calculate distance between requested point and other points
        df['dist'] = np.sqrt(pow(df['StartStationLatitude'] - x, 2) + pow(df['StartStationLongitude'] - y, 2))
        # print(df.shape)
        # Keep only points within +-1KM
        df = df.drop(df[df['dist'] > 0.001].index)
        # print(df.shape)
        return df

    def _score_trips(self, df, requested_time):
        time_difference_weight = 1
        distance_weight = 1
        df = df.groupby(['StartStationName', 'EndStationName']).agg({'dist': np.median, 'TripDurationinmin': np.median})
        df['score'] = -(df['dist'] * distance_weight) - (np.abs(df['TripDurationinmin'] - requested_time) * time_difference_weight)
        return df


nu = MyBackend()
nu.initialize_db("BikeShare.csv")
print(nu.get_recommendations('5 Corners Library',4, 5))
