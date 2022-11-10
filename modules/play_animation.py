import os, random
import numpy as np
import pandas as pd
from plotly import graph_objects as go

data_path = "data/files/"
_data_path = "data/output//"

games_df = pd.read_csv(os.path.join(data_path, "games.csv"))
scouting_data_df = pd.read_csv(os.path.join(data_path, "pffScoutingData.csv"))
players_df = pd.read_csv(os.path.join(_data_path, "out.csv"))
plays_df = pd.read_csv(os.path.join(data_path, "plays.csv"))
week_df_dict = {}

for i in range(1,9):
    week_df_dict[i] = pd.read_csv(os.path.join(data_path, "week"+str(i)+".csv"))
    week_df_dict[i]['Week'] = i

week_df = pd.concat(week_df_dict, ignore_index=True)

del(week_df_dict)

team_info_df = pd.read_csv("data/files/TeamColors.csv")

print()
print("Made it to the defs", "\n")
print("Made it to the defs", "\n")
print()

def getPlayerNameByNflId(nflId):
    '''
    Get the Player's Name Using Their NFL Id
    '''
    try:
        return players_df[players_df['nflId'] == nflId]['displayName'].values[0]
    except:
        return ""

def getPlayerJerseyNumberByNflIdAndGameId(nflId, gameId):
    '''
    Get the jersey number a player was wearing in a specific game
    using their NFL Id and the Game Id
    '''
    try:
        cur_week_df = week_df[week_df['gameId'] == gameId]
        return int(cur_week_df[cur_week_df['nflId'] == nflId]['jerseyNumber'].values[0])
    except:
        return None

def getTeamInfo(teamAbbr):
    '''
    Pull Out Some Info about a team including their full name, city, colors etc. from the team abbreviation

    NOTE: This utilizes the nfl-team-colors dataset at https://www.kaggle.com/datasets/spencerriggins/nfl-team-colors
    '''
    dtmp = team_info_df[team_info_df['teamAbbr'] == teamAbbr]
    team_info = {}
    team_info['teamAbbr'] = teamAbbr
    team_info['teamCity'] = dtmp['cityName'].values[0]
    team_info['teamName'] = dtmp['teamName'].values[0]
    team_info['primaryColor'] = dtmp['primaryCol'].values[0]
    team_info['secondaryColor'] = dtmp['secondaryCol'].values[0]
    return team_info

def getPlayerGameInfo(nflId, gameId, playId):
    '''
    Get info about what a certain player did on a certain play from the player's
    NFL Id, the Game Id, and the Play Id.
    Returned info includes the player's name, jersey number, position, role,
    PFF stats, and any penalties called on the player on that play.
    '''

    player_info_to_keep = [
        "nflId",
        "name",
        "jerseyNumber",
        "officialPosition",
        "pff_role",
        "pff_positionLinedUp",
        "pff_hit",
        "pff_hurry",
        "pff_sack",
        "pff_beatenByDefender",
        "pff_hitAllowed",
        "pff_hurryAllowed",
        "pff_sackAllowed",
        "pff_nflIdBlockedPlayer",
        "pff_blockType",
        "pff_backFieldBlock",
        "penalties"
    ]

    playerInfo = {}

    tmp_player_info = players_df[players_df['nflId'] == nflId].to_dict(orient='records')[0]
    tmp_pff_info = scouting_data_df[np.all([scouting_data_df['playId'] == playId,
                                            scouting_data_df['gameId'] == gameId,
                                            scouting_data_df['nflId'] == nflId], axis=0)].to_dict(orient='records')[0]
    tmp_play_info = \
    plays_df[np.logical_and(plays_df['playId'] == playId, plays_df['gameId'] == gameId)].to_dict(orient='records')[0]

    playerInfo = {**tmp_player_info, **tmp_pff_info}

    playerInfo['nflId'] = nflId
    playerInfo['name'] = getPlayerNameByNflId(nflId)
    playerInfo['jerseyNumber'] = getPlayerJerseyNumberByNflIdAndGameId(nflId, gameId)
    playerInfo['penalties'] = []

    for potential_foul, potential_foul_id in zip(["foulName1", "foulName2", "foulName3"],
                                                 ["foulNFLId1", "foulNFLId2", "foulNFLId3"]):
        if (tmp_play_info[potential_foul_id] == nflId):
            playerInfo['penalties'].append(tmp_play_info[potential_foul])

    for k in list(playerInfo.keys()):
        if (k not in player_info_to_keep):
            playerInfo.pop(k)

    for d in player_info_to_keep:
        playerInfo[d] = playerInfo.get(d, None)

        if (not isinstance(playerInfo[d], list)
                and not isinstance(playerInfo[d], str)
                and playerInfo[d] is not None
                and np.isnan(playerInfo[d])):
            playerInfo[d] = None

    return playerInfo

def buildPlayerHoverTextFromGameInfo(playerGameInfo):
    '''
    This is pretty verbose, but this looks at the info about what the player
    did on the current play (the output of getPlayerGameInfo()), and builds an html
    string which will be used to generate the text that shows up when you hover on that
    player in the visualization.
    '''
    hoverText = ""

    # Player Name, Number, and Position
    playerNameLine = str(playerGameInfo['name']) if playerGameInfo['name'] is not None else ""
    playerPositionAndNumberLine = str(playerGameInfo['officialPosition']) if playerGameInfo[
                                                                                 'officialPosition'] is not None else ""
    playerPositionAndNumberLine += " #" + str(playerGameInfo['jerseyNumber']) if playerGameInfo[
                                                                                     'jerseyNumber'] is not None else ""
    if (playerNameLine != "" and playerPositionAndNumberLine != ""):
        playerNameLine = playerNameLine + "<br>" + playerPositionAndNumberLine
    if (playerNameLine != ""):
        hoverText += "<span style='font-weight:bold; font-size:14.0pt'>" + playerNameLine + "</span>"

    if (playerGameInfo['officialPosition'] != playerGameInfo['pff_positionLinedUp']
            and playerGameInfo['pff_positionLinedUp'] != None):
        if (playerPositionAndNumberLine == ""):
            hoverText += "<br>"
        else:
            hoverText += " "
        hoverText += "<span>(Lined Up At: " + playerGameInfo['pff_positionLinedUp'] + ")</span>"

    # Player Role
    playerRoleLine = "<span style='font-weight:bold'>Role: </span>" + str(playerGameInfo['pff_role']) if playerGameInfo[
                                                                                                             'pff_role'] is not None else ""
    if (playerRoleLine != ""):
        hoverText += "<br><span>" + playerRoleLine + "</span>"

    # Player Stats
    binary_stats_to_readable_names = {'pff_hit': 'Hit \U0001f4a5',
                                      'pff_hurry': 'Hurry \u23F3',
                                      'pff_sack': 'Sack \U0001f4b0',
                                      'pff_beatenByDefender': 'Beaten By Defender \U0001f643',
                                      'pff_hitAllowed': 'Hit Allowed \U0001f4a5 \U0001f613',
                                      'pff_hurryAllowed': 'Hurry Allowed \u23F3 \U0001f628',
                                      'pff_sackAllowed': 'Sack Allowed \U0001f4b0 \U0001f62d'}
    stats_lines = ""
    for stat in binary_stats_to_readable_names.keys():
        if (playerGameInfo[stat] == 1):
            stats_lines += "<br><span>" + binary_stats_to_readable_names[stat] + "</span>"

    if (stats_lines != ""):
        stats_lines = "<br><br><span style='font-weight:bold; font-size:12.0pt'>Stats:</span>" + stats_lines
        hoverText += stats_lines

    # Player Block Info
    block_types_to_readable_names = {'BH': 'A Backfield Help',
                                     'CH': 'A Chip',
                                     'CL': 'A Second Level',
                                     'NB': 'No',
                                     'PA': 'A Play Action Pass Protection',
                                     'PP': 'A Pass Protection',
                                     'PR': 'A Pocket Roll',
                                     'PT': 'A Post',
                                     'PU': 'A Backfield Pickup',
                                     'SR': 'A Set and Release',
                                     'SW': 'A Switch',
                                     'UP': 'A Pull Pass Protection'
                                     }

    block_lines = ""
    if (playerGameInfo['pff_blockType'] is not None):
        block_lines += "Performed " + block_types_to_readable_names.get(playerGameInfo['pff_blockType'],
                                                                        "A") + " Block "
        if (playerGameInfo['pff_nflIdBlockedPlayer'] is not None):
            opposing_player = getPlayerNameByNflId(playerGameInfo['pff_nflIdBlockedPlayer'])
        else:
            opposing_player = ""
        if (opposing_player != ""):
            block_lines += "Against <span style='font-weight:bold'>" + opposing_player + "</span>"
            # block_lines += "Against " + opposing_player
    if (block_lines != "" and playerGameInfo['pff_backFieldBlock'] == 1):
        block_lines += " in the backfield."
    elif (block_lines != ""):
        block_lines += "."
    if (block_lines != ""):
        block_lines = "<br><br><span style='font-weight:bold; font-size:12.0pt'>Blocking:</span><br>" + block_lines
        hoverText += block_lines

    # Player Penalty Info
    penalty_lines = ""
    for i, penalty in enumerate(playerGameInfo['penalties']):
        penalty_lines += "\U0001f7e8 " + penalty
        if (i != len(playerGameInfo['penalties']) - 1):
            penalty_lines += "<br>"

    if (penalty_lines != ""):
        penalty_lines = "<br><br><span style='font-weight:bold; font-size:12.0pt'>Penalties:</span><br>" + penalty_lines
        hoverText += penalty_lines

    return hoverText

def animateplay(gameid, playid, marker_size=100, marker_line_width=2,
                marker_alpha=.75, fps=100, show_hash_marks=False):
    '''
    Displays the visualization for a game and play id.
    gameId: The gameId we wish to display
    playId: The playId we wish to display
    marker_size: The size of the markers in the visualization
    marker_alpha: The opacity of the markers in the visualization
    fps: The frames per second of the animation (100 is real time)...
    Lower fps -> Fast Motion...
    Higher fps -> Slow Motion
    show_hash_marks: If True, hash marks are displayed on the field...
    This greatly increases the time to render the animation if set to True
    '''

    # Extract Info On Current Play
    cur_play_df = week_df[week_df['gameId'] == gameid]
    cur_play_df = cur_play_df[cur_play_df['playId'] == playid]
    cur_play_df['size'] = 1
    cur_play_df['color'] = 1
    cur_play_df_football = cur_play_df[cur_play_df['team'] == 'football']

    # TODO: Only drop if NA in relevant columns
    cur_play_df = cur_play_df.dropna()

    # Get Team Info
    home_team_info = {}
    visitor_team_info = {}
    home_team_info = getTeamInfo(games_df[games_df['gameId'] == gameid]["homeTeamAbbr"].values[0])
    visitor_team_info = getTeamInfo(games_df[games_df['gameId'] == gameid]["visitorTeamAbbr"].values[0])

    cur_play_df_home_team = cur_play_df[cur_play_df['team'] == home_team_info['teamAbbr']]
    cur_play_df_visitor_team = cur_play_df[cur_play_df['team'] == visitor_team_info['teamAbbr']]

    # Get Game Info
    gameInfo = games_df[games_df['gameId'] == gameid]
    home_team_abbr = gameInfo['homeTeamAbbr'].values[0]
    visitor_team_abbr = gameInfo['visitorTeamAbbr'].values[0]
    home_team_city = home_team_info['teamCity']
    visitor_team_city = visitor_team_info['teamCity']
    home_team_name = home_team_info['teamName']
    visitor_team_name = visitor_team_info['teamName']
    home_team_primary_color = home_team_info['primaryColor']
    visitor_team_primary_color = visitor_team_info['primaryColor']
    gameWeek = gameInfo['week'].values[0]

    # Get Play Info
    play_info = plays_df[np.logical_and(plays_df['playId'] == playid, plays_df['gameId'] == gameid)]
    play_description = play_info['playDescription'].values[0]
    play_quarter = play_info['quarter'].values[0]
    play_time = play_info['gameClock'].values[0]
    home_team_score = play_info['preSnapHomeScore'].values[0]
    visitor_team_score = play_info['preSnapVisitorScore'].values[0]
    possession_team = play_info['possessionTeam'].values[0]
    yardline_number = play_info['yardlineNumber'].values[0]
    absolute_yardline_number = play_info['absoluteYardlineNumber'].values[0]
    yardline_side = play_info['yardlineSide'].values[0]
    yards_to_go = play_info['yardsToGo'].values[0]
    play_direction = cur_play_df['playDirection'].values[0]
    down_num = play_info['down'].values[0]
    down_readable = {1: "1st Down", 2: "2nd Down", 3: "3rd Down", 4: "4th Down"}[down_num]
    first_down_line = absolute_yardline_number + yards_to_go if play_direction == "right" else absolute_yardline_number - yards_to_go

    # Build Strings For Displaying Title And Scoreboard
    gameTitle = "Week " + str(gameWeek) + "<br><span style='color:" + str(visitor_team_primary_color) + "'>" + str(
        visitor_team_name) + \
                "</span> vs. <span style='color:" + str(home_team_primary_color) + "'>" + str(
        home_team_name) + "</span><br><sup>"

    for i, pr in enumerate(play_description.split('. ')):
        punc = '' if i == len(play_description.split('. ')) - 1 else '.'
        res = pr.strip() + punc
        if (res.lower().startswith("penalty")):
            res = "\U0001f7e8 " + res
        elif ("touchdown" in res.lower()):
            res = res + "\U0001f389 \U0001f64c \U0001f389"
        if (i == 0):
            gameTitle += "<span style='color:black; font-size:10pt'>" + res + "</span>"
        else:
            gameTitle += "<br><span style='color:black; font-size:7.5pt'>" + res + "</span>"
    gameTitle += "</sup>"

    scoreboardTitle = "<span style='font-size:15.0pt'>     " + str(
        play_time) + "     </span><br><span style='font-size:10.0pt'>Q" + str(
        play_quarter) + " " + down_readable + "</span><br><br>" \
                      + "<span style='font-size:16.0pt; color:" + visitor_team_primary_color + "'>" + str(
        visitor_team_score) + \
                      "</span>       <span style='font-size:16.0pt; color:" + home_team_primary_color + "'>" + str(
        home_team_score)

    # Determine the number of frames in our animation
    n_frames = min(max(cur_play_df_home_team['frameId'].values), max(cur_play_df_visitor_team['frameId'].values))

    fig_dict = {
        "data": [],
        "layout": {},
        "frames": []
    }

    xticks = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]
    xticktexts = ["", "G", "10", "20", "30", "40", "50", "40", "30", "20", "10", "G", ""]

    # fill in most of layout
    fig_dict["layout"]["xaxis"] = {"range": [0, 120], "tickvals": xticks, "ticktext": xticktexts}
    fig_dict["layout"]["yaxis"] = {"range": [0, 53.3], "tickvals": []}
    fig_dict["layout"]["hovermode"] = "closest"
    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    # This is what changes the speed it looks like
                    "args": [None, {"frame": {"duration": fps, "redraw": False},
                                    "fromcurrent": True, "transition": {"duration": 100,
                                                                        "easing": "quadratic-in-out"}}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                      "mode": "immediate",
                                      "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }
    ]

    # Add the Scoreboard
    fig_dict["layout"]["annotations"] = [
        go.layout.Annotation(
            text=scoreboardTitle,
            align='center',
            showarrow=False,
            xref='paper',
            yref='paper',
            x=0.025,
            y=1.15,
            bordercolor='black',
            borderwidth=1
        )
    ]

    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Frame:",
            "visible": False,
            "xanchor": "right"
        },
        "transition": {"duration": 10, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": []
    }

    # Get a list of players in the current play
    players = list(set(cur_play_df['nflId'].values))

    # Get the necessary info on each player, and build their hover text strings
    playersGameInfo = {player: getPlayerGameInfo(player, gameid, playid) for player in players}
    playersHoverTexts = {player: buildPlayerHoverTextFromGameInfo(playersGameInfo[player]) for player in
                         playersGameInfo.keys()}

    # Add the info for displaying each player to the figure
    frameId = 1
    for player in players:
        cur_player_name = getPlayerNameByNflId(player)

        cur_play_df_by_frame = cur_play_df[cur_play_df['frameId'] == frameId]
        cur_play_df_by_frame_and_player = cur_play_df_by_frame[
            cur_play_df_by_frame['nflId'] == player]

        team = cur_play_df_by_frame_and_player['team'].values[0]
        cur_team_info = home_team_info if home_team_info['teamAbbr'] == team else visitor_team_info

        data_dict = {
            "x": list(cur_play_df_by_frame_and_player['x']),
            "y": list(cur_play_df_by_frame_and_player['y']),
            "mode": "markers",
            "hovertext": playersHoverTexts[player],
            "marker": {
                "sizemode": "area",
                "sizeref": 1,
                "size": [marker_size] * len(cur_play_df_by_frame_and_player),
                "color": cur_team_info['primaryColor'],
                "line": {"width": marker_line_width, "color": cur_team_info['secondaryColor']},
                "opacity": marker_alpha
            },
            "name": ""
        }
        fig_dict["data"].append(data_dict)

    # Add Data For Football To Fig Dict
    data_dict = {
        "x": [list(cur_play_df_football['x'])[0]],
        "y": [list(cur_play_df_football['y'])[0]],
        "mode": "markers",
        "hovertext": "Football",
        "marker": {
            "sizemode": "area",
            "sizeref": 1,
            "size": [marker_size] * len(cur_play_df_football),
            "color": "#75161a",
            "line": {"width": marker_line_width, "color": "#FFFFFF"},
            "symbol": "diamond-wide",
            "opacity": marker_alpha
        },
        "name": ""
    }
    fig_dict["data"].append(data_dict)

    frames = range(1, n_frames + 1)
    # Add the info for displaying each player to each frame in the animation
    for cur_frameId in frames:
        frame = {"data": [], "name": str(cur_frameId)}
        for player in players:
            cur_player_name = getPlayerNameByNflId(player)

            cur_play_df_by_frame = cur_play_df[cur_play_df['frameId'] == cur_frameId]
            cur_play_df_by_frame_and_player = cur_play_df_by_frame[
                cur_play_df_by_frame['nflId'] == player]

            team = cur_play_df_by_frame_and_player['team'].values[0]
            cur_team_info = home_team_info if home_team_info['teamAbbr'] == team else visitor_team_info
            data_dict = {
                "x": list(cur_play_df_by_frame_and_player['x']),
                "y": list(cur_play_df_by_frame_and_player['y']),
                "mode": "markers",
                "hovertext": playersHoverTexts[player],
                "marker": {
                    "sizemode": "area",
                    "sizeref": 1,
                    "size": [marker_size] * len(cur_play_df_by_frame_and_player),
                    "color": cur_team_info['primaryColor'],
                    "line": {"width": marker_line_width, "color": cur_team_info['secondaryColor']},
                    "opacity": marker_alpha
                },
                "name": "",
            }
            frame["data"].append(data_dict)

        # Add Football Data To Frame
        cur_play_df_football_by_frame = cur_play_df_football[cur_play_df_football['frameId'] == cur_frameId]
        data_dict = {
            "x": list(cur_play_df_football_by_frame['x']),
            "y": list(cur_play_df_football_by_frame['y']),
            "mode": "markers",
            "hovertext": "Football",
            "marker": {
                "sizemode": "area",
                "sizeref": 1,
                "size": [marker_size] * len(cur_play_df_football_by_frame),
                "color": "#75161a",
                "line": {"width": marker_line_width, "color": "#FFFFFF"},
                "symbol": "diamond-wide",
                "opacity": marker_alpha
            },
            "name": ""
        }
        frame["data"].append(data_dict)

        fig_dict["frames"].append(frame)
        slider_step = {"args": [
            [cur_frameId],
            {"frame": {"duration": 300, "redraw": False},
             "mode": "immediate",
             "transition": {"duration": 300}}
        ],
            "label": cur_frameId,
            "method": "animate"}
        sliders_dict["steps"].append(slider_step)

    fig_dict["layout"]["sliders"] = [sliders_dict]

    # Display The Figure
    fig = go.Figure(fig_dict)

    fig.update_layout(
        title=go.layout.Title(
            text=gameTitle,
            xref="paper",
            x=.5,
            y=0.97
        ),
        width=1250,
        height=750,
        showlegend=False,
        plot_bgcolor='rgba(58,176,93,20)'
    )

    # Add Line Of Scrimmage
    fig.add_vline(x=absolute_yardline_number, line_width=3, line_dash="dash", line_color="blue", opacity=.75)
    # Add First Down Line
    fig.add_vline(x=first_down_line, line_width=3, line_dash="solid", line_color="yellow", opacity=.75)
    # Add Hash Marks (This slows down the generation of the graph a lot since it is adding so many shapes)
    if (show_hash_marks):
        for y in [.33333, 23.58333, 53.3 - 23.58333, 53.3 - .33333]:
            for x in range(10, 111):
                fig.add_shape(type="line", x0=x, y0=y - .33333, x1=x, y1=y + .33333, line_width=2, line_dash="solid",
                              line_color="white", opacity=.5)
    fig.show()

def getRandomPlay():
    '''
    Pick a random gameId and playId combo
    '''
    i = random.randint(0, len(plays_df)-1)
    return plays_df['gameId'].values[i], plays_df['playId'].values[i]

gameId, playId = getRandomPlay()

animateplay(gameId, playId)