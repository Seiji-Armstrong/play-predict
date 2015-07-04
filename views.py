from flask import render_template, request
from app import app
from a_Model import ModelIt
import play_predict as nba
import pandas as pd
import pymysql as mdb



@app.route('/')
@app.route('/index')

def play_predict_input(): # above decorator modifies the function (so function name useless)
    return render_template("play_predict_home.html")

@app.route('/play_predict_game_select')

def play_predict_game_select(): # above decorator modifies the function (so function name useless)
    date_input = request.args.get('date')
    team_list = nba.teams_from_date(date_input)

    return render_template("play_predict_game_select.html", team_list = team_list)



@app.route('/dashboard')

def play_predict_output(): # above decorator modifies the function (so function name useless)
    # set some defaults

    rowIndex = int(request.args.get('game_row'))
    game_id = request.args.get('game_select')
    print game_id
    database = 'next_play'
    table = 'season_2008'
    teams_list = nba.teams_in_game(game_id) # redundant
    this_game = nba.create_game_frame_sql(database,table,game_id)
    row = min(rowIndex, len(this_game.index)-1)
    starting_five = nba.starting_five_from_game(this_game)
    table = 'streak_frame_with_perf'   
    
    starting_five_1 = starting_five[:5]
    performance_list_table_1 = nba.last_5_next_performance(database,table,starting_five_1,this_game,row)

    starting_five_2 = starting_five[5:]
    performance_list_table_2 = nba.last_5_next_performance(database,table,starting_five_2,this_game,row)

    play_now = nba.current_play_description(this_game,row)
    period_time = nba.current_period_time(this_game,row)

    return render_template("dashboard.html", period_time = period_time, play_now = play_now, 
        teams_list = teams_list, table_from_list_1 = performance_list_table_1, table_from_list_2 = performance_list_table_2)











