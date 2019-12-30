import csv
import sqlite3
import numpy as np
import pandas as pd

class MyBackend:
    def __init__(self):
        self._conn = sqlite3.connect("database.db")
        if not self.doesTableExists():
            self._initialize_db("BikeShare.csv")

    def _initialize_db(self, path):
        self._create_table_in_db()
        self.load_csv_into_db(path)
        self._conn.commit()
        #self._conn.close()

    def _create_table_in_db(self):
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS bikeShare (TripDuration INTEGER ,StartTime TIMESTAMP ,StopTime TIMESTAMP, StartStationID INTEGER, StartStationName TEXT, StartStationLatitude REAL, StartStationLongitude REAL, EndStationID INTEGER, EndStationName TEXT, EndStationLatitude REAL, EndStationLongitude REAL, BikeID INTEGER, UserType TEXT, BirthYear INTEGER, Gender INTEGER, TripDurationinmin INTEGER)")

    def doesTableExists(self):
        tablename = 'bikeShare'
        dbcur = self._conn.cursor()
        dbcur.execute("""
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type='table' AND name = '{0}'
            """.format(tablename.replace('\'', '\'\'')))
        if dbcur.fetchone()[0] == 1:
            dbcur.close()
            return True

        dbcur.close()
        return False

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
        df = self._load_data_from_db()
        df_recommendations = self._create_recommendations(df, time, starting_location, num_of_recommendations)
        if df_recommendations is None:
            return []
        recommendations = df_recommendations.index.get_level_values('EndStationName').tolist()
        return recommendations

    def _load_data_from_db(self):

        #Load all trips to memory
        query = "SELECT StartStationName, StartStationLatitude, StartStationLongitude, TripDurationinmin, EndStationName FROM bikeShare"

        cursor = self._conn.execute(query)

        #Construct dataframe
        cols = [column[0] for column in cursor.description]
        df = pd.DataFrame.from_records(data=cursor.fetchall(), columns=cols)
        return df

    def _create_recommendations(self, df, time, starting_location, num_of_recommendations):

        df = self._filter_distance_parameter(df, starting_location)
        if df is None: #If no such starting_location exists in DB
            return None
        df = self._score_trips(df, time) #Add a score column to df
        df.sort_values(by=['score'], ascending=False, inplace=True)

        df = df.head(num_of_recommendations)
        return df

    def _filter_distance_parameter(self, df, starting_location):
        start_location_df = df[df['StartStationName'] == starting_location]

        #If such starting point exists in DB
        if starting_location in df['StartStationName'].values:

            x = start_location_df.iloc()[0]['StartStationLatitude']  # Get the requested starting point's latitude
            y = start_location_df.iloc()[0]['StartStationLongitude']  # Get the requested starting point's longitude
            # Calculate distance between requested point and other points
            df['dist'] = np.sqrt(pow(df['StartStationLatitude'] - x, 2) + pow(df['StartStationLongitude'] - y, 2))
            # Keep only points within +-1KM
            df = df.drop(df[df['dist'] > 0.001].index)

            return df
        else:
            return None

    def _score_trips(self, df, requested_time):
        time_difference_weight = 1
        distance_weight = 1

        #We only keep unique sets of starting and ending points.
        df = df.groupby(['StartStationName', 'EndStationName']).agg({'dist': np.median, 'TripDurationinmin': np.median})
        #The score is comprised of the sum of:
        # 1. minus the distance between the requested starting point (e.g., highest score is zero)
        # 2. minus the delta between the requested duration and the median duration of the trip (e.g., highest score is zero).
        df['score'] = -(df['dist'] * distance_weight) - (np.abs(df['TripDurationinmin'] - requested_time) * time_difference_weight)
        return df

