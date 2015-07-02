from flask import render_template, request
from app import app
from a_Model import ModelIt
import nba_performance_app as nba
from nba_performance_app import recent_performance
from nba_performance_app import frame_from_player
# from nba_performance import create_image
import pandas as pd
import pymysql as mdb
import seaborn as sns



# @app.route('/week2_demo')

# def week2_ladida_demo_input(): # above decorator modifies the function (so function name useless)
#     return render_template("week2_demo.html")

# @app.route('/week2_output')

# def week2_ladida_demo_output(): # above decorator modifies the function (so function name useless)
#     # set some defaults

#     player_name = request.args.get('ID')
#     N = int(request.args.get('ID2')) # 34
#     rowIndex = int(request.args.get('ID3')) # 50

#     folder = "/home/seiji/Dropbox/Code/Data/Basketball/2009-2010/"
#     file_name = "20091027.BOSCLE.csv"
#     game_all = pd.read_csv(folder+file_name)
#     total_frame = game_all[["period","time","team","player","etype","type","points","assist","block","steal","result"]]
#     stats_weights = {'point': 1, 'rebound': 1.2, 'assist': 1.5, 'steal': 2, 'block': 2, 'turnover': -1, 'foul': -0.5,'missed_fg': -0.5, 'missed_ft': -0.5, 'three_pt': 1.5}
#     player_frame = frame_from_player(player_name,total_frame)

#     stats_dict, performance_rating = recent_performance(player_name,player_frame,N,rowIndex,stats_weights)
#     ### can do this better:
#     if performance_rating > 0:
#         coach_action = 'keep him on the court!'
#     else:
#         coach_action = 'take him out the game!'
#     ###
#     return render_template("week2_output.html", temp_dict = [stats_dict], the_result = performance_rating, player_name = player_name, coach_action = coach_action)


# @app.route('/week3_demo')

# def week3_demo_input(): # above decorator modifies the function (so function name useless)
#     return render_template("week3_demo.html")

# @app.route('/week3_output')

# def week3_demo_output(): # above decorator modifies the function (so function name useless)
#     # set some defaults

#     # game_date = request.args.get('ID')
#     # game_id = int(request.args.get('ID2')) # 34
#     rowIndex = int(request.args.get('ID3')) # 50
#     game_select = request.args.get('game_select')
#     date = request.args.get('date')
#     game_date = nba.game_date_from_date(date)

#     database = 'next_play'
#     table = 'season_2008'
#     game_id_df = nba.gameIDs_sql(database,table)
#     # game_date = '20090119'
#     games_by_date_df = game_id_df[game_id_df['gameID'].str.contains(game_date)]
#     game_id = games_by_date_df.gameID.values[2]
#     this_game = nba.create_game_frame_sql(database,table,game_id)
#     starting_five = nba.starting_five_from_game(this_game)
#     table = 'streak_frame_with_perf'   
#     performance_list_table_1 = nba.create_performance_table(database,table,starting_five)
#     starting_five_2 = starting_five[5:]
#     performance_list_table_2 = nba.create_performance_table(database,table,starting_five_2)
    
#     row = 250
#     row = rowIndex
#     play_now = nba.current_play_description(this_game,row)

#     return render_template("week3_output.html", play_now = play_now, table_from_list_1 = performance_list_table_1, table_from_list_2 = performance_list_table_2)


@app.route('/week4_demo')

def week3_demo_input(): # above decorator modifies the function (so function name useless)
    return render_template("week4_demo.html")

@app.route('/week4_output')

def week4_demo_output(): # above decorator modifies the function (so function name useless)
    # set some defaults

    rowIndex = int(request.args.get('ID3')) # 50
    game_select = request.args.get('game_select')
    date = request.args.get('date')
    game_date = nba.game_date_from_date(date)

    database = 'next_play'
    table = 'season_2008'
    game_id_df = nba.gameIDs_sql(database,table)
    # game_date = '20090119'
    games_by_date_df = game_id_df[game_id_df['gameID'].str.contains(game_date)]
    game_id = games_by_date_df.gameID.values[2]
    this_game = nba.create_game_frame_sql(database,table,game_id)
    starting_five = nba.starting_five_from_game(this_game)
    table = 'streak_frame_with_perf'   
    performance_list_table_1 = nba.create_performance_table(database,table,starting_five)
    starting_five_2 = starting_five[5:]
    performance_list_table_2 = nba.create_performance_table(database,table,starting_five_2)
    
    row = 250
    row = rowIndex
    play_now = nba.current_play_description(this_game,row)

    return render_template("week4_output.html", play_now = play_now, table_from_list_1 = performance_list_table_1, table_from_list_2 = performance_list_table_2)






# @app.route('/images/<temp_image>')
# def images(temp_image):
#     return render_template("images.html", title=temp_image)

# @app.route('/fig/<temp_image>')
# def fig(temp_image):
#     fig = create_image(temp_image)
#     img = StringIO()
#     fig.savefig(img)
#     img.seek(0)
#     return send_file(img, mimetype='image/png')

########


# db = mdb.connect(user="root", host="localhost", passwd="ZayDvlA204", db="world_innodb", charset='utf8')
# @app.route('/')
# @app.route('/index')
# def index():
#    user = { 'nickname': 'Seiji' } # fake user
#    return render_template("index.html", title = 'Home', user = user)

# @app.route('/db')
# def cities_page():
# 	with db:
# 		cur = db.cursor()
# 		cur.execute("SELECT Name FROM City LIMIT 15;")
# 		query_results = cur.fetchall()
# 	cities = ""
# 	for result in query_results:
# 		cities += result[0]
# 		cities += "<br>"
# 	return cities

# @app.route("/db_fancy")

# def cities_page_fancy():
# 	with db:
# 		cur = db.cursor()
# 		cur.execute("SELECT Name, CountryCode, Population FROM City ORDER BY Population LIMIT 15;")
# 		query_results = cur.fetchall()
# 	cities = []
# 	for result in query_results:
# 		cities.append(dict(name=result[0], country=result[1], population=result[2]))
# 	return render_template('cities.html', cities=cities)

# @app.route('/input')

# def cities_input():
# 	return render_template("input.html")

# @app.route('/output')

# def cities_output():
# 	#pull 'ID' from input field and store it
#     city = request.args.get('ID')
#     with db:
#     	cur = db.cursor()
#     	#just select the city from the world_innodb that the user inputs
#     	cur.execute("SELECT Name, CountryCode,  Population FROM City WHERE Name='%s';" % city)
#     	query_results = cur.fetchall()

#     cities = []
#     for result in query_results:
#     	cities.append(dict(name=result[0], country=result[1], population=result[2]))

#       #call a function from a_Model package. note we are only pulling one result in the query
#     pop_input = cities[0]['population']
#     the_result = ModelIt(city, pop_input)
#     return render_template("output.html", cities = cities, the_result = the_result)

#####################################################################################################   