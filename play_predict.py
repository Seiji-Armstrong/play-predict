from __future__ import division
import MySQLdb
import MySQLdb.cursors
import glob
import urllib
import urllib2
import sqlite3
from urllib2 import urlopen
import json
import pandas as pd
from pandas import DataFrame
import numpy as np
import scipy as sp
# import seaborn as sns
# import matplotlib as mpl
# import matplotlib.pyplot as plt
# %matplotlib inline
import re
from datetime import datetime
import bisect
from collections import Counter
from sqlalchemy import create_engine
import ast
import scipy.optimize as optimize

teams_dict = {'bos':'Boston Celtics',
                  'njn':'New Jersey Nets',
                  'nyk':'New York Knicks',
                  'phi':'Philadelphia 76ers',
                  'tor':'Toronto Raptors',
                  'gsw':'Golden State Warriors',
                  'lac':'Los Angeles Clippers',
                  'lal':'Los Angeles Lakers',
                  'phx':'Phoenix Suns',
                  'sac':'Sacramento Kings',
                  'chi':'Chicago Bulls',
                  'cle':'Cleveland Cavaliers',
                  'det':'Detroit Pistons',
                  'ind':'Indiana Pacers',
                  'mil':'Milwaukee Bucks',
                  'dal':'Dallas Mavericks',
                  'hou':'Houston Rockets',
                  'mem':'Memphis Grizzlies',
                  'noh':'New Orleans Hornets',
                  'nok':'New Orleans/Oklahoma City Hornets',
                  'sas':'San Antonio Spurs',
                  'atl':'Atlanta Hawks',
                  'cha':'Charlotte Bobcats',
                  'mia':'Miami Heat',
                  'orl':'Orlando Magic',
                  'was':'Washington Wizards',
                  'den':'Denver Nuggets',
                  'min':'Minnesota Timberwolves',
                  'okc':'Oklahoma City Thunder',
                  'por':'Portland Trail Blazers',
                  'uta':'Utah Jazz',
                  'sea':'Seattle SuperSonics'
                  }

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

month_dict = {'01':'January',
              '02':'Febuary',
              '03':'March',
              '04':'April',
              '05':'May',
              '06':'June',
              '07':'July',
              '08':'August',
              '09':'September',
              '10':'October',
              '11':'November',
              '12':'December'
              }


# sns.set_context("notebook", font_scale=1.6)
stats_weights = {'point': 1, 'rebound': 1.2, 'assist': 1.5, 
                'steal': 2, 'block': 2, 'turnover': -1, 'foul': -0.5,
                'missed_fg': -0.5, 'missed_ft': -0.5, 'three_pt': 1.5}
stats_weights_rand_forest = {'point': 1.1, 'rebound': 1.2, 'assist': 1.5, 
                'steal': 2.3, 'block': 2.1, 'turnover': -1, 'foul': -0.7,
                'missed_fg': -0.5, 'missed_ft': -0.3, 'three_pt': 1.3}
adj_dict = {'point': 0.62782609, 'rebound': 0.58347826, 'assist': 0.59891304, 
                'steal': 0.64141304, 'block': 0.61315217, 'three_pt': 0.59684783}
adj_list = ['point', 'rebound', 'assist','steal', 'block', 'three_pt']

#########################

def game_date_input_tidy(date_input):
    game_date = '2009' + date_input[3:5] + date_input[:2]
    return game_date

def game_date_tidy(date_input):
    year = int(date_input[-4:])
    game_date = str(year-6) + date_input[3:5] + date_input[:2]
    return game_date
# MySQL
def gameIDs_sql(database,table):
    conn = MySQLdb.connect(user="root",passwd="xxxx",db=database, host="0.0.0.0",
        cursorclass=MySQLdb.cursors.DictCursor)
    cmd_target = 'SELECT DISTINCT gameID FROM season_2008;'
    df_gameIDs = pd.read_sql(cmd_target, con=conn)
    conn.close()
    return df_gameIDs

def create_game_frame_sql(database,table,game_id):
    conn = MySQLdb.connect(user="root",passwd="xxxx",db=database, host="0.0.0.0",
        cursorclass=MySQLdb.cursors.DictCursor)
    cmd_target = 'SELECT * FROM '+ table + ' WHERE gameID IN (\''+ game_id +'\');'
    this_game = pd.read_sql(cmd_target, con=conn)
    # starting_five = this_game.iloc[0][["a1","a2","a3","a4","a5","h1","h2","h3","h4","h5"]]
    conn.close()
    return this_game

def starting_five_from_game(game_frame):
    starting_five = game_frame.iloc[0][["a1","a2","a3","a4","a5","h1","h2","h3","h4","h5"]]
    return starting_five

def create_performance_table_test(database,table,starting_five):
    performance_list = []
    # current_streak_pos for each player in starting_five.
    for player_name in starting_five:
        player_dict = {}
        player_frame = player_frame_from_sql(database,table,player_name)
        pos_or_neg = 'pos_streak_list'
        pos_streak_counts = streak_counts_pos_neg(player_frame,pos_or_neg)
        pos_or_neg = 'neg_streak_list' 
        neg_streak_counts = streak_counts_pos_neg(player_frame,pos_or_neg)
        current_streak_pos = 1
        Next_1_play = good_play_next(pos_streak_counts,neg_streak_counts,current_streak_pos)
        Next_2_play = good_play_2_next(pos_streak_counts,neg_streak_counts,current_streak_pos)
        player_dict = {'player': player_name, 'Next_1_play': str(round(100*Next_1_play,2))+' %',
                       'Next_2_play': str(round(100*Next_2_play,2))+' %'}
        performance_list.append(player_dict)
    return performance_list

def player_frame_from_sql(database,table,player_name):
    conn = MySQLdb.connect(user="root",passwd="xxxx",db=database, host="0.0.0.0",
        cursorclass=MySQLdb.cursors.DictCursor)
    cmd_target = 'SELECT * FROM '+ table + ' WHERE player IN (\''+ player_name +'\');'
    player_frame = pd.read_sql(cmd_target, con=conn)
    return player_frame

def counts_from_streaks(streaks):
    streak_data = np.concatenate(streaks)
    df_streaks = pd.DataFrame(streak_data)
    streak_counts = pd.value_counts(df_streaks.values.ravel())
    return streak_counts

def streak_counts_player(player_frame):
    # return list of 4 predictions
    player_values = player_frame['pos_streak_list'].values
    streaks = [ast.literal_eval(x) for x in player_values]
    streak_counts = counts_from_streaks(streaks)
    return streak_counts

def streak_counts_pos_neg(player_frame,pos_or_neg):
    # pos_or_neg = 'pos_streak_list' or 'neg_streak_list'
    player_values = player_frame[pos_or_neg].values
    streaks = [ast.literal_eval(x) for x in player_values]
    streak_counts = counts_from_streaks(streaks)
    return streak_counts


def current_play_description(this_game,row):
    return str(this_game.iloc[row].player) + ' with a ' + this_game.iloc[row].etype

def current_period_time(this_game,row):
    return [this_game.iloc[row].period, this_game.iloc[row].time]





def teams_in_game(game_id):
    team_1_xxx = game_id[-6:-3].lower()
    team_2_xxx = game_id[-3:].lower()
    teams_list = [teams_dict[team_1_xxx], teams_dict[team_2_xxx]]
    return teams_list

def pos_or_neg_play(this_play):
    # bad play = 0
    # good play = 1
    if this_play.etype in ['foul', 'turnover']:
        return -1
    if this_play.etype in ['shot', 'free throw'] and this_play.result == 'missed':
        return -1
    else:
        return 1



def current_streak_pos_player(player_name,this_game,row):
    player_this_game = this_game[this_game["player"] == player_name]
    player_last_row = find_previous_event_row(player_this_game,row).name
    this_play = this_game.iloc[player_last_row]
    minus_1 = pos_or_neg_play(this_play)
    player_last_row = find_previous_event_row(player_this_game,player_last_row-1).name
    this_play = this_game.iloc[player_last_row]
    minus_2 = pos_or_neg_play(this_play)
    one_two = minus_1+minus_2
    if one_two == 0:
        return int(minus_1)
    else:
        player_last_row = find_previous_event_row(player_this_game,player_last_row-1).name
        this_play = this_game.iloc[player_last_row]
        minus_3 = pos_or_neg_play(this_play)
        return int(one_two + 0.5*(minus_1+minus_3))

def last_3_next_performance_(database,table,starting_five,this_game,row):
    performance_list = []
    # look at last 3 plays for each player.
    for player_name in starting_five:
        last_play = []
        player_dict = {}
        player_frame = player_frame_from_sql(database,table,player_name)
        pos_or_neg = 'pos_streak_list'
        pos_streak_counts = streak_counts_pos_neg(player_frame,pos_or_neg)
        pos_or_neg = 'neg_streak_list' 
        neg_streak_counts = streak_counts_pos_neg(player_frame,pos_or_neg)
        current_streak_pos = current_streak_pos_player(player_name,this_game,row)
        Next_1_play = good_play_next(pos_streak_counts,neg_streak_counts,current_streak_pos)
        Next_2_play = good_play_2_next(pos_streak_counts,neg_streak_counts,current_streak_pos)
        player_dict = {'player': player_name, 'current_pos': current_streak_pos, 'Next_1_play': str(round(100*Next_1_play,2))+' %',
        'Next_2_play': str(round(100*Next_2_play,2))+' %'}
        performance_list.append(player_dict)
    return performance_list

def frame_from_player(player_name,this_game):
    activityFrame = this_game[this_game["player"] == player_name]
    stealFrame = this_game[this_game["steal"]== player_name]
    assistFrame = this_game[this_game["assist"]== player_name]
    blockFrame = this_game[this_game["block"]== player_name]
    player_frame_game = pd.concat([stealFrame,assistFrame,blockFrame,activityFrame])
    return player_frame_game.sort_index(axis=0) # might not need to sort_index.



def one_event_stat(player_name,current_series,stats_dict):
    # update dictionary of stats (stats_dict) with stat from current row.
    event = current_series
    event_dict = {'point': int(event.points)+int((event.result == 'made') & (event.etype == 'free throw')),
    'rebound': int(event.etype == 'rebound'), 
    'assist': int(event.assist == player_name),
    'steal': int(event.steal == player_name), 
    'block': int(event.block == player_name),
    'turnover': int(event.etype == 'turnover'),
    'foul': int(event.etype == 'foul'),
    'missed_fg': int((event.result == 'missed') & (event.etype != 'free throw')),
    'missed_ft': int((event.result == 'missed') & (event.etype == 'free throw')),
    'three_pt': int((event['type'] == '3pt') & (event.result == 'made'))}
    stats_dict = add_2_dict_values(stats_dict,event_dict)
    return stats_dict

def add_2_dict_values(dict1,dict2):
    return dict(Counter(dict1)+Counter(dict2))

def stats_performance(stats_dict,stats_weights):
    performance = sum([stats_dict[key]*stats_weights[key] for key in stats_dict])    
    return performance

def teams_from_date(date_input):
    game_date = game_date_tidy(date_input)
    database = 'next_play'
    table = 'season_2008'
    game_id_df = gameIDs_sql(database,table)
    games_by_date_df = game_id_df[game_id_df['gameID'].str.contains(game_date)]
    if games_by_date_df['gameID'].values.any():
        team_list = []
        for game in games_by_date_df['gameID']:
            team_1 = game[-6:-3].lower()
            team_2 = game[-3:].lower()
            dict_1 = {game:teams_dict[team_1]+ ' v ' + teams_dict[team_2]}
            team_list.append(dict_1)
    else:
        team_list = [{'20090121.CLEPOR': 'Cleveland Cavaliers v Portland Trail Blazers'}]    
    return team_list

def player_pos_count(player_name):
    database = 'next_play'
    table = 'pos_count_players'
    conn = MySQLdb.connect(user="root",passwd="xxxx",db=database, host="0.0.0.0",
        cursorclass=MySQLdb.cursors.DictCursor)
    cmd_target = 'SELECT * FROM '+ table + ';'
    this_frame = pd.read_sql(cmd_target, con=conn)
    pos_streak_counts = pd.Series(this_frame[player_name]).fillna(0)
    return pos_streak_counts

def player_neg_count(player_name):
    database = 'next_play'
    table = 'neg_count_players'
    conn = MySQLdb.connect(user="root",passwd="xxxx",db=database,host="0.0.0.0",
    cursorclass=MySQLdb.cursors.DictCursor)
    cmd_target = 'SELECT * FROM '+ table + ';'
    this_frame = pd.read_sql(cmd_target, con=conn)
    neg_streak_counts = pd.Series(this_frame[player_name]).fillna(0)
    return neg_streak_counts


def good_play_next(pos_streak_counts,neg_streak_counts,current_streak_pos):
    if current_streak_pos >= 0:
        count_current_streak = pos_streak_counts[current_streak_pos]
        count_remaining = sum(pos_streak_counts[current_streak_pos:])
        prob_next = count_remaining/(count_current_streak+count_remaining)
    else: # if current_streak_pos is negative
        count_current_streak = neg_streak_counts[abs(current_streak_pos)]
        count_remaining = sum(pos_streak_counts[abs(current_streak_pos):])
        prob_next = count_current_streak/(count_current_streak+count_remaining)
    return prob_next

def good_play_2_next(pos_streak_counts,neg_streak_counts,current_streak_pos):
    if current_streak_pos >= 0:
        prob_pos = good_play_next(pos_streak_counts,neg_streak_counts,current_streak_pos)
        pos = prob_pos*good_play_next(pos_streak_counts,neg_streak_counts,current_streak_pos+1)
        neg = (1-prob_pos)*good_play_next(pos_streak_counts,neg_streak_counts,-1)
    else: # if negative
        prob_neg = good_play_next(pos_streak_counts,neg_streak_counts,current_streak_pos)
        pos = (1-prob_neg)*good_play_next(pos_streak_counts,neg_streak_counts,1)
        neg = prob_neg*good_play_next(pos_streak_counts,neg_streak_counts,current_streak_pos-1)
    prob_2_next = pos + neg
    return prob_2_next




def good_play_next_cond(pos_streak_counts,neg_streak_counts,current_streak_pos):
    current_streak_pos = int(current_streak_pos)
    if current_streak_pos >= 0:
        if sum(pos_streak_counts) < 50:
            return 0.5195 # Measured relevant mean for lower rank players
        current_pos = current_streak_pos - 1
        count_current_streak = pos_streak_counts[current_pos]
        count_remaining = sum(pos_streak_counts[current_pos+1:])
        prob_next = count_remaining/(count_current_streak+count_remaining)
    else:
        if sum(neg_streak_counts) < 50:
            return 0.4895 # Measured relevant mean for lower rank players
        # if current_streak_pos is negative
        current_pos = abs(current_streak_pos) - 1
        count_current_streak = neg_streak_counts[current_pos]
        count_remaining = sum(neg_streak_counts[current_pos+1:])
        prob_next = count_current_streak/(count_current_streak+count_remaining)    
    return prob_next

def good_play_2_next_cond(pos_streak_counts,neg_streak_counts,current_streak_pos):
    if current_streak_pos >= 0:
        if sum(pos_streak_counts) < 50:
            return 0.4765 # Measured relevant mean for lower rank players        
        prob_pos = good_play_next(pos_streak_counts,neg_streak_counts,current_streak_pos)
        pos = prob_pos*good_play_next(pos_streak_counts,neg_streak_counts,current_streak_pos+1)
        neg = (1-prob_pos)*good_play_next(pos_streak_counts,neg_streak_counts,-1)
    else: # if negative
        if sum(neg_streak_counts) < 50:
            return 0.4590 # Measured relevant mean for lower rank players      
        prob_neg = good_play_next(pos_streak_counts,neg_streak_counts,current_streak_pos)
        pos = (1-prob_neg)*good_play_next(pos_streak_counts,neg_streak_counts,1)
        neg = prob_neg*good_play_next(pos_streak_counts,neg_streak_counts,current_streak_pos-1)
    prob_2_next = pos + neg
    return prob_2_next

def last_5_next_performance(database,table,starting_five,this_game,row):
    performance_list = []
    # current_streak_pos for each player in starting_five.
    # look at last 3 plays for each player.
    for player_name in starting_five:
        last_5_perf = []
        player_dict = {}
        player_frame = player_frame_from_sql(database,table,player_name)
        pos_or_neg = 'pos_streak_list'
        pos_streak_counts = streak_counts_pos_neg(player_frame,pos_or_neg)
        pos_or_neg = 'neg_streak_list' 
        neg_streak_counts = streak_counts_pos_neg(player_frame,pos_or_neg)

        current_streak_pos = current_streak_pos_player(player_name,this_game,row)
        Next_1_play = good_play_next(pos_streak_counts,neg_streak_counts,current_streak_pos)
        Next_2_play = good_play_2_next(pos_streak_counts,neg_streak_counts,current_streak_pos)
        N = 5
        player_frame_game = frame_from_player(player_name,this_game)
        player_last5 = recent_perf(player_name,player_frame_game,N,row,stats_weights)
        player_dict = {'player': player_name, 'current_pos': current_streak_pos, 'player_last5': player_last5[1], 'Next_1_play': str(round(100*Next_1_play,2))+' %', 'Next_2_play': str(round(100*Next_2_play,2))+' %'}
        performance_list.append(player_dict)
    return performance_list

def find_previous_event_row(PlayerFrame,rowIndex):
    # returns a pandas series of relevant play-by-play row.
    relevant_index = rowIndex
    if rowIndex not in PlayerFrame.index:
        relevant_index = PlayerFrame.index[bisect.bisect_left(PlayerFrame.index,rowIndex) - 1]
    return PlayerFrame.ix[relevant_index].fillna(0)

def recent_perf(player_name,player_frame_game,N,rowIndex,stats_weights):
    stats_dict={}
    # return performance rating (one number) and stats_dict given a player frame, rowIndex, and N plays
    row = rowIndex
    N = min(len(player_frame_game.index),N)
    for past_play in range(N):
        current_event_series = find_previous_event_row(player_frame_game,row)
        stats_dict = one_event_stat(player_name,current_event_series,stats_dict)
        row = current_event_series.name-1       
    performance_rating = stats_performance(stats_dict,stats_weights)
    return [stats_dict, performance_rating]


def last_5_next(database,table,starting_five,this_game,row):
    performance_list = []
    for player_name in starting_five:
        last_5_perf = []
        player_dict = {}

        pos_streak_counts = player_pos_count(player_name)
        neg_streak_counts = player_neg_count(player_name)

        current_streak_pos = current_streak_pos_player(player_name,this_game,row)
        Next_1_play = good_play_next_cond(pos_streak_counts,neg_streak_counts,current_streak_pos)
        Next_2_play = good_play_2_next_cond(pos_streak_counts,neg_streak_counts,current_streak_pos)
        N = 5
        player_frame_game = frame_from_player(player_name,this_game)
        player_last5 = recent_perf(player_name,player_frame_game,N,row,stats_weights)

        N=1
        last_play = recent_perf(player_name,player_frame_game,N,row,stats_weights)
        if len(last_play[0].keys()) > 0:
            if last_play[0].keys()[0] in adj_dict.keys():
                adj_key = last_play[0].keys()[0]
                Next_1_play = 0.9*Next_1_play+0.1*adj_dict[adj_key]
        player_dict = {'player': player_name, 'current_pos': current_streak_pos, 'player_last5': player_last5[1], 'Next_1_play': str(round(100*Next_1_play,2))+' %', 'Next_2_play': str(round(100*Next_2_play,2))+' %'}
        performance_list.append(player_dict)
    return performance_list


def times_list_game(this_game):
    times_list = []
    for i in range(len(this_game)):
        game_row = this_game.iloc[i]
        dict_1 = {i:'Quarter '+str(game_row['period'])+', '+str(game_row['time'])}
        times_list.append(dict_1)
    return times_list

def teams_from_select(team_input_1,team_input_2):
    database = 'next_play'
    table = 'season_2008'
    game_id_df = gameIDs_sql(database,table)
    games_by_team1_df = game_id_df[(game_id_df['gameID'].str.contains(team_input_1.upper()+team_input_2.upper()))]
    games_by_team2_df = game_id_df[(game_id_df['gameID'].str.contains(team_input_2.upper()+team_input_1.upper()))]
    games_by_team1_all_df = game_id_df[(game_id_df['gameID'].str.contains(team_input_1.upper()))]
    team_list = []
    if games_by_team1_df['gameID'].values.any():
        for game in games_by_team1_df['gameID']:
            team_1 = game[-6:-3].lower()
            team_2 = game[-3:].lower()
            dict_1 = {game:month_dict[game[4:6]]+ ' ' + game[6:8] + ', ' + teams_dict[team_1]+ ' v ' + teams_dict[team_2]}
            team_list.append(dict_1)
    if games_by_team2_df['gameID'].values.any():
        for game in games_by_team2_df['gameID']:
            team_1 = game[-6:-3].lower()
            team_2 = game[-3:].lower()
            dict_1 = {game:month_dict[game[4:6]]+ ' ' + game[6:8] + ', ' + teams_dict[team_1]+ ' v ' + teams_dict[team_2]}
            team_list.append(dict_1)
    else:
        if games_by_team1_all_df['gameID'].values.any():
            for game in games_by_team1_all_df['gameID']:
                team_1 = game[-6:-3].lower()
                team_2 = game[-3:].lower()
                dict_1 = {game:month_dict[game[4:6]]+ ' ' + game[6:8] + ', ' + teams_dict[team_1]+ ' v ' + teams_dict[team_2]}
                team_list.append(dict_1)
        else:
            team_list = [{'20090121.CLEPOR': 'Cleveland Cavaliers v Portland Trail Blazers'}]
    return team_list

