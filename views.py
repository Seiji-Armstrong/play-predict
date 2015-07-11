from flask import render_template, request
from app import app
from a_Model import ModelIt
import play_predict as nba
import pandas as pd
import pymysql as mdb


teams_dict_list = [{'bos':'Boston Celtics'},
                  {'njn':'New Jersey Nets'},
                  {'nyk':'New York Knicks'},
                  {'phi':'Philadelphia 76ers'},
                  {'tor':'Toronto Raptors'},
                  {'gsw':'Golden State Warriors'},
                  {'lac':'Los Angeles Clippers'},
                  {'lal':'Los Angeles Lakers'},
                  {'phx':'Phoenix Suns'},
                  {'sac':'Sacramento Kings'},
                  {'chi':'Chicago Bulls'},
                  {'cle':'Cleveland Cavaliers'},
                  {'det':'Detroit Pistons'},
                  {'ind':'Indiana Pacers'},
                  {'mil':'Milwaukee Bucks'},
                  {'dal':'Dallas Mavericks'},
                  {'hou':'Houston Rockets'},
                  {'mem':'Memphis Grizzlies'},
                  {'noh':'New Orleans Hornets'},
                  {'nok':'New Orleans/Oklahoma City Hornets'},
                  {'sas':'San Antonio Spurs'},
                  {'atl':'Atlanta Hawks'},
                  {'cha':'Charlotte Bobcats'},
                  {'mia':'Miami Heat'},
                  {'orl':'Orlando Magic'},
                  {'was':'Washington Wizards'},
                  {'den':'Denver Nuggets'},
                  {'min':'Minnesota Timberwolves'},
                  {'okc':'Oklahoma City Thunder'},
                  {'por':'Portland Trail Blazers'},
                  {'uta':'Utah Jazz'},
                  {'sea':'Seattle SuperSonics'}
                  ]



@app.route('/')
@app.route('/index')

# def play_predict_input(): # above decorator modifies the function (so function name useless)
#     return render_template("play_predict_home.html")


def play_predict_home_games(): # above decorator modifies the function (so function name useless)
    return render_template("play_predict_home_games.html", teams_dict_list = teams_dict_list)

@app.route('/play_predict_game_select')

def play_predict_game_select_games(): # above decorator modifies the function (so function name useless)
    team_input_1 = request.args.get('team_select_1')
    team_input_2 = request.args.get('team_select_2')
    team_list = nba.teams_from_select(team_input_1,team_input_2)

    return render_template("play_predict_game_select_games.html", team_list = team_list)





# def play_predict_game_select(): # above decorator modifies the function (so function name useless)
#     date_input = request.args.get('date')
#     if len(date_input) == 10 and date_input[2] == "/" and date_input[5]  == "/":
#         team_list = nba.teams_from_date(date_input)        
#     else:
#         err_message = 'Please pick from the calendar and do not enter text.'
#         return render_template("play_predict_home.html")
#     return render_template("play_predict_game_select.html", team_list = team_list)







@app.route('/dashboard')

def play_predict_output(): # above decorator modifies the function (so function name useless)
    # set some defaults

    rowIndex = int(request.args.get('game_row'))
    game_id = request.args.get('game_select')

    database = 'next_play'
    table = 'season_2008'
    teams_list = nba.teams_in_game(game_id) # redundant
    this_game = nba.create_game_frame_sql(database,table,game_id)
    

    times_list = nba.times_list_game(this_game)

    

    row = min(rowIndex, len(this_game.index)-1)
    starting_five = nba.starting_five_from_game(this_game)
    
    table = 'streak_frame_with_perf'   
    

    starting_five_1 = starting_five[:5]
    # performance_list_table_1 = nba.last_5_next_performance(database,table,starting_five_1,this_game,row)
    performance_list_table_1 = nba.last_5_next(database,table,starting_five_1,this_game,row)

    starting_five_2 = starting_five[5:]
    # performance_list_table_2 = nba.last_5_next_performance(database,table,starting_five_2,this_game,row)
    performance_list_table_2 = nba.last_5_next(database,table,starting_five_2,this_game,row)

    play_now = nba.current_play_description(this_game,row)
    period_time = nba.current_period_time(this_game,row)

    return render_template("dashboard.html", period_time = period_time, play_now = play_now, game_id = game_id, times_list = times_list,
        teams_list = teams_list, table_from_list_1 = performance_list_table_1, table_from_list_2 = performance_list_table_2)











