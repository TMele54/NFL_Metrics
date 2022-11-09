import sqlite3
import pandas as pd
import os

data_dir = "data/files/"
files = os.listdir(data_dir)
table_name = files[0].split(".")[0]
weeks = [week for week in files if "week" in week]

def query_db(Q, head=5):
    conn = sqlite3.connect('sqlite:///../data/db/nfl.db')
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
    rs = pd.read_sql(Q, conn)

    print(rs.head(head))


########################################################################################################################
games_query = '''
    SELECT 
    P.gameId, 
    P.playId, 
    P.playDescription, 
    P.quarter, 
    P.down, 
    P.gameClock, 
    P.yardsToGo, 
    P.possessionTeam, 
    P.passResult, 
    
    /*P.defensiveTeam, 
    P.yardlineSide, 
    P.yardlineNumber, 
    P.preSnapHomeScore, 
    P.preSnapVisitorScore, 
    P.penaltyYards, 
    P.prePenaltyPlayResult, 
    P.playResult, 
    P.foulName1, 
    P.foulNFLId1, 
    P.foulName2, 
    P.foulNFLId2, 
    P.foulName3, 
    P.foulNFLId3, 
    P.absoluteYardlineNumber, 
    P.offenseFormation, 
    P.personnelO, 
    P.dropBackType,
    P.pff_playAction, 
    P.pff_passCoverage, 
    P.pff_passCoverageType,*/ 
    
    G.gameDate, 
    G.gameTimeEastern
        FROM games as G 
        INNER JOIN plays as P
            ON G.gameId = P.gameId
            WHERE G.gameId = "2021101700" 
            ORDER BY P.quarter ASC,  P.gameClock DESC    
'''
query_db(games_query)
########################################################################################################################

########################################################################################################################
physical_kinetics_query = '''
    SELECT 
        *
        FROM players as P
        INNER JOIN weekly as W
            ON P.nflId = W.nflId
            ORDER BY W.gameId ASC, W.playId ASC 
'''
query_db(physical_kinetics_query)
########################################################################################################################