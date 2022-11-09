import sqlite3
import pandas as pd
import os


if not os.path.isdir("data/db"):
    os.makedirs("data/db")


## ## ## DOWNLOAD DATA FROM KAGGLE IN data/sources FILE ## ## ##
## ## ## PUT KAGGLE FILES IN BELOW DIRECTORY ## ## ##

if not os.path.isdir("data/files"):
    os.makedirs("data/files/")


def build_database():
    conn = sqlite3.connect('sqlite:///../data/db/nfl.db')

    data_dir = "data/files/"
    files = [
        "games.csv",
        "pffScoutingData.csv",
        "players.csv",
        "plays.csv",
        "week1.csv",
        "week2.csv",
        "week3.csv",
        "week4.csv",
        "week5.csv",
        "week6.csv",
        "week7.csv",
        "week8.csv",
    ]

    weeks = [week for week in files if "week" in week]

    print("write every csv file to a table")
    for file in files:
        csvfile = data_dir+file

        df = pd.read_csv(csvfile)

        table_name = file.split(".")[0]

        df.to_sql(table_name, conn, if_exists='replace', index=False)

        # p2 = pd.read_sql('select * from ' + table_name, conn)

        print(table_name, "written to DB file")

    print("create dedicated weeklies table")
    for week in weeks:
        csvfile = data_dir+week

        df = pd.read_csv(csvfile)

        table_name = "weekly"

        df.to_sql(table_name, conn, if_exists='append', index=False)

        p2 = pd.read_sql('select count(*) from ' + table_name, conn)
        print(p2)
        print(table_name, "written to DB file")

def show_tables():
    try:

        # Making a connection between sqlite3
        # database and Python Program
        sqliteConnection = sqlite3.connect('sqlite:///../data/db/nfl.db')

        # If sqlite3 makes a connection with python
        # program then it will print "Connected to SQLite"
        # Otherwise it will show errors
        print("Connected to SQLite")

        # Getting all tables from sqlite_master
        sql_query = """
            SELECT name 
            FROM sqlite_master 
            WHERE 
            type='table';
        """

        # Creating cursor object using connection object
        cursor = sqliteConnection.cursor()

        # executing our sql query
        cursor.execute(sql_query)
        print("List of tables\n")

        # printing all tables list
        for table in cursor.fetchall():
            print(table[0])

    except sqlite3.Error as error:
        print("Failed to execute the above query", error)

    finally:

        # Inside Finally Block, If connection is
        # open, we need to close it
        if sqliteConnection:
            # using close() method, we will close
            # the connection
            sqliteConnection.close()

            # After closing connection object, we
            # will print "the sqlite connection is
            # closed"
            print()
            print("the sqlite connection is closed")

    return None

build_database()
show_tables()