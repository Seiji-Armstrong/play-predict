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
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
# %matplotlib inline
import re
from datetime import datetime
import bisect
from collections import Counter
from sqlalchemy import create_engine
import ast
import scipy.optimize as optimize


sns.set_context("notebook", font_scale=1.6)
stats_weights = {'point': 1, 'rebound': 1.2, 'assist': 1.5, 
                'steal': 2, 'block': 2, 'turnover': -1, 'foul': -0.5,
                'missed_fg': -0.5, 'missed_ft': -0.5, 'three_pt': 1.5}
def frame_from_player(player_name,sub_frame):
    activityFrame = sub_frame[sub_frame["player"] == player_name]
    stealFrame = sub_frame[sub_frame["steal"]== player_name]
    assistFrame = sub_frame[sub_frame["assist"]== player_name]
    blockFrame = sub_frame[sub_frame["block"]== player_name]
    PlayerFrame = pd.concat([stealFrame,assistFrame,blockFrame,activityFrame])
    return PlayerFrame.sort_index(axis=0) # might not need to sort_index.
def stats_performance(stats_dict,stats_weights):
    performance = sum([stats_dict[key]*stats_weights[key] for key in stats_dict])    
    return performance
def find_previous_event_row(PlayerFrame,rowIndex):
    # returns a pandas series of relevant play-by-play row.
    relevant_index = rowIndex
    if rowIndex not in PlayerFrame.index:
        relevant_index = PlayerFrame.index[bisect.bisect_left(PlayerFrame.index,rowIndex) - 1]
    return PlayerFrame.ix[relevant_index].fillna(0)
def recent_performance(player_name,PlayerFrame,N,rowIndex,stats_weights):
    stats_dict={}
    # return performance rating (one number) and stats_dict given a player frame, rowIndex, and N plays
    row = rowIndex
    N = min(len(PlayerFrame.index),N)
    for past_play in range(N):
        current_event_series = find_previous_event_row(PlayerFrame,row)
        stats_dict = one_event_stat(player_name,current_event_series,stats_dict)
        row = current_event_series.name-1       
    performance_rating = stats_performance(stats_dict,stats_weights)
    return stats_dict, performance_rating

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
# A lot of this is redundant, as there will only be one event. Improve later.
# How to improve: Determine event type, update only relevant category.
# if event.etype == shot: etc.

def add_2_dict_values(dict1,dict2):
    return dict(Counter(dict1)+Counter(dict2))
def streak_counter(performance_list):
    pos_streak_list = []
    neg_streak_list = []
    pos_streak = 0
    neg_streak = 0
    for num in performance_list:
        if num > 0:
            pos_streak +=1
            if neg_streak > 2:
                neg_streak_list.append(neg_streak)
            neg_streak = 0
        elif num <0:
            neg_streak +=1
            if pos_streak > 2:
                pos_streak_list.append(pos_streak)
            pos_streak = 0        
    if pos_streak > 2:
        pos_streak_list.append(pos_streak)
    if neg_streak > 2:
        neg_streak_list.append(neg_streak)
    return [pos_streak_list, neg_streak_list]
def create_streak_dict(player_name,sub_frame,player_streak_dict):
    player_frame = frame_from_player(player_name,sub_frame)
    plays = [recent_performance(player_name,player_frame,1,rowIndex,stats_weights) for rowIndex in player_frame.index]
    performance_list =[event[1] for event in plays]
    streak_list = streak_counter(performance_list)
    player_streak_dict[player_name] = streak_list
    return player_streak_dict
def create_game_streak_dicts(df,game_streak_dict):
    game_id_list = df.gameID.unique()
    for game_id in game_id_list:
        this_game = df[df["gameID"] == game_id]
        starting_five = this_game.iloc[0][["a1","a2","a3","a4","a5","h1","h2","h3","h4","h5"]]
        player_streak_dict={}
        for player_name in starting_five:
            player_streak_dict = create_streak_dict(player_name,this_game,player_streak_dict)
        game_streak_dict[game_id]=player_streak_dict
    return game_streak_dict

def create_player_dict(player_name,this_game):
    current_streak_dict = {}
    player_frame = frame_from_player(player_name,this_game)
    plays = [recent_performance(player_name,player_frame,1,rowIndex,stats_weights) for rowIndex in player_frame.index]
    performance_list =[event[1] for event in plays]
    streak_list = streak_counter(performance_list)
    game_id = this_game.gameID.values[0]
    current_streak_dict = {'gameID': game_id, 'player': player_name, 
    'pos_streak_list': streak_list[0], 'neg_streak_list': streak_list[1]}
    return current_streak_dict

def create_streak_frame(df):
    games_streak_list = []
    game_id_list = df.gameID.unique()
    for game_id in game_id_list:
        this_game = df[df["gameID"] == game_id]
        starting_five = this_game.iloc[0][["a1","a2","a3","a4","a5","h1","h2","h3","h4","h5"]]
        for player_name in starting_five:
            current_streak_dict = create_player_dict(player_name,this_game)
            games_streak_list.append(current_streak_dict)
    game_streak_frame = pd.DataFrame(games_streak_list)
    return game_streak_frame

def gameIDs_sql(database,table):
    conn = MySQLdb.connect(user="root",passwd="xxxx",db=database,
                           cursorclass=MySQLdb.cursors.DictCursor)
    cmd_target = 'SELECT DISTINCT gameID FROM season_2008;'
    df_gameIDs = pd.read_sql(cmd_target, con=conn)
    conn.close()
    return df_gameIDs

def create_streak_frame_sql(database,table):
    df_gameIDs = gameIDs_sql(database,table)
    conn = MySQLdb.connect(user="root",passwd="xxxx",db=database,
                           cursorclass=MySQLdb.cursors.DictCursor)
    games_streak_list = []
    for game_id in df_gameIDs.values[:-1]:
        print game_id[0]
        cmd_target = 'SELECT * FROM '+ table + ' WHERE gameID IN (\''+ game_id[0] +'\');'
        this_game = pd.read_sql(cmd_target, con=conn)
        starting_five = this_game.iloc[0][["a1","a2","a3","a4","a5","h1","h2","h3","h4","h5"]]
        for player_name in starting_five:
            current_streak_dict = nba.create_player_dict(player_name,this_game)
            games_streak_list.append(current_streak_dict)
    game_streak_frame = pd.DataFrame(games_streak_list)
    conn.close()
    return game_streak_frame

def starting_five_from_game(game_frame):
    starting_five = game_frame.iloc[0][["a1","a2","a3","a4","a5","h1","h2","h3","h4","h5"]]
    return starting_five


def create_game_frame_sql(database,table,game_id):
    conn = MySQLdb.connect(user="root",passwd="xxxx",db=database,
                           cursorclass=MySQLdb.cursors.DictCursor)
    cmd_target = 'SELECT * FROM '+ table + ' WHERE gameID IN (\''+ game_id +'\');'
    this_game = pd.read_sql(cmd_target, con=conn)
    # starting_five = this_game.iloc[0][["a1","a2","a3","a4","a5","h1","h2","h3","h4","h5"]]
    conn.close()
    return this_game


def player_performance_plots(database,table,player_name):
    conn = MySQLdb.connect(user="root",passwd="xxxx",db=database,
                           cursorclass=MySQLdb.cursors.DictCursor)
    cmd_target = 'SELECT * FROM '+ table + ' WHERE player IN (\''+ player_name +'\');'
    player_frame = pd.read_sql(cmd_target, con=conn)
    conn.close()
    player_values = player_frame['pos_streak_list'].values
    streaks = [ast.literal_eval(x) for x in player_values]
    streak_data = np.concatenate(streaks)
    x=range(len(streak_data))
    y=streak_data
    df_streaks = pd.DataFrame(dict(streaks=x, streak_length=y))
    streak_counts = pd.value_counts(df_streaks.values.ravel())

    xData = streak_counts.index[:15]
    xData_1 = [x-1 for x in xData]
    yData = streak_counts.values[:15]
    # yData_1 = yData*(1000)/yData[0]

    popt, pcov = optimize.curve_fit(exp_func, xData, yData)

    yEXP = exp_func(xData, *popt)

    plt.figure()
    sns.factorplot("streak_length", data=df_streaks,kind="bar",palette="Blues",size=6,aspect=2,legend_out=False);
    plt.plot(xData_1, yData, label='Data', marker='o')
    plt.plot(xData_1, yEXP, 'r-',ls='--', label="Exp Fit")
    plt.legend()
    plt.show()
    a,b,c = popt
    return streak_counts


def next_good_play_from(streak_counts,current_streak_pos):
    count_current_streak = streak_counts[current_streak_pos]
    count_remaining = sum(streak_counts[current_streak_pos+1:10])
    prob_next = count_remaining/(count_current_streak+count_remaining)
    return prob_next

def target_good_play_from(streak_counts,current_streak_pos,target_pos):
    if target_pos == current_streak_pos:
        return 1
    count_current_streak = streak_counts[target_pos]
    count_remaining = sum(streak_counts[target_pos+1:])
    # count_remaining = sum(streak_counts[target_pos+1:target_pos+14])
    prob_next = count_remaining/(count_current_streak+count_remaining)
    soln = prob_next*target_good_play_from(streak_counts,current_streak_pos,target_pos-1)
    return soln

def player_frame_from_sql(database,table,player_name):
    conn = MySQLdb.connect(user="root",passwd="xxxx",db=database,
                           cursorclass=MySQLdb.cursors.DictCursor)
    cmd_target = 'SELECT * FROM '+ table + ' WHERE player IN (\''+ player_name +'\');'
    player_frame = pd.read_sql(cmd_target, con=conn)
    return player_frame

##########


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







#############

def create_player_dict_from1(player_name,this_game):
    current_streak_dict = {}
    print player_name
    this_game.head()
    player_frame = frame_from_player(player_name,this_game)
    plays = [recent_performance(player_name,player_frame,1,rowIndex,stats_weights) for rowIndex in player_frame.index]
    performance_list =[event[1] for event in plays]
    streak_list = streak_counter_from1(performance_list)
    game_id = this_game.gameID.values[0]
    current_streak_dict = {'gameID': game_id, 'player': player_name,
                           'pos_streak_list': streak_list[0], 'neg_streak_list': streak_list[1],
                           'performance_play_list': performance_list}
    return current_streak_dict



def create_streak_frame_sql_from1(database,table):
    df_gameIDs = gameIDs_sql(database,table)
    conn = MySQLdb.connect(user="root",passwd="xxxx",db=database,
                           cursorclass=MySQLdb.cursors.DictCursor)
    games_streak_list = []
    for game_id in df_gameIDs.values[:-1]:
        print game_id[0]
        cmd_target = 'SELECT * FROM '+ table + ' WHERE gameID IN (\''+ game_id[0] +'\');'
        this_game = pd.read_sql(cmd_target, con=conn)
        starting_five = this_game.iloc[0][["a1","a2","a3","a4","a5","h1","h2","h3","h4","h5"]]
        for player_name in starting_five:
            current_streak_dict = create_player_dict_from1(player_name,this_game)
            games_streak_list.append(current_streak_dict)
    game_streak_frame = pd.DataFrame(games_streak_list)
    conn.close()
    return game_streak_frame




def streak_counter_from1(performance_list):
    pos_streak_list = []
    neg_streak_list = []
    pos_streak = 0
    neg_streak = 0
    for num in performance_list:
        if num > 0:
            pos_streak +=1
            if neg_streak > 0:
                neg_streak_list.append(neg_streak)
            neg_streak = 0
        elif num <0:
            neg_streak +=1
            if pos_streak > 0:
                pos_streak_list.append(pos_streak)
            pos_streak = 0        
    if pos_streak > 0:
        pos_streak_list.append(pos_streak)
    if neg_streak > 0:
        neg_streak_list.append(neg_streak)
    return [pos_streak_list, neg_streak_list]


def exp_func(x,a,b,c):
   return a*np.exp(-b*x)-c


def create_players_streak_dicts(df,player_streak_dict):
    game_id_list = df.gameID.unique()
    for game in game_id_list:
        this_game = df[df["gameID"] == game]
        starting_five = this_game.iloc[0][["a1","a2","a3","a4","a5","h1","h2","h3","h4","h5"]]
        for player_name in starting_five:
            player_streak_dict = create_streak_dict(player_name,this_game,player_streak_dict)
    return player_streak_dict

def game_performance_plots(player_name,sub_frame,N,save,file_name):
    player_frame = frame_from_player(player_name,sub_frame)
    plays = [recent_performance(player_name,player_frame,N,rowIndex,stats_weights) for rowIndex in player_frame.index]
    perf =[event[1] for event in plays]
    x=range(len(perf))
    y=perf
    df = pd.DataFrame(dict(game_event=x, performance=y))
    sns.factorplot("game_event","performance", data=df,kind="bar",palette="Blues",size=6,aspect=2,legend_out=False);
    if save == 'save':
        plt.savefig(file_name, dpi=200)




def create_performance_table(database,table,starting_five):
    player_name_1 = starting_five[0]
    player_frame = player_frame_from_sql(database,table,player_name_1)
    streak_counts_1 = streak_counts_player(player_frame)
    player_name_2 = starting_five[1]
    player_frame = player_frame_from_sql(database,table,player_name_2)
    streak_counts_2 = streak_counts_player(player_frame)   
    player_name_3 = starting_five[2]
    player_frame = player_frame_from_sql(database,table,player_name_3)
    streak_counts_3 = streak_counts_player(player_frame) 
    player_name_4 = starting_five[3]
    ### Error for Shaquille O'neal
    player_frame = player_frame_from_sql(database,table,player_name_4)
    streak_counts_4 = streak_counts_player(player_frame) 
    player_name_5 = starting_five[4]
    player_frame = player_frame_from_sql(database,table,player_name_5)
    streak_counts_5 = streak_counts_player(player_frame)

    current_streak_pos = 1
    target_pos = current_streak_pos + 1
    Next_1_play_1 = target_good_play_from(streak_counts_1,current_streak_pos,target_pos)
    target_pos = current_streak_pos + 2
    Next_2_play_1 = target_good_play_from(streak_counts_1,current_streak_pos,target_pos)
    current_streak_pos = 1
    target_pos = current_streak_pos + 1
    Next_1_play_2 = target_good_play_from(streak_counts_2,current_streak_pos,target_pos)
    target_pos = current_streak_pos + 2
    Next_2_play_2 = target_good_play_from(streak_counts_2,current_streak_pos,target_pos)
    current_streak_pos = 1
    target_pos = current_streak_pos + 1
    Next_1_play_3 = target_good_play_from(streak_counts_3,current_streak_pos,target_pos)
    target_pos = current_streak_pos + 2
    Next_2_play_3 = target_good_play_from(streak_counts_3,current_streak_pos,target_pos)
    current_streak_pos = 1
    target_pos = current_streak_pos + 1
    Next_1_play_4 = target_good_play_from(streak_counts_4,current_streak_pos,target_pos)
    target_pos = current_streak_pos + 2
    Next_2_play_4 = target_good_play_from(streak_counts_4,current_streak_pos,target_pos)
    current_streak_pos = 1
    target_pos = current_streak_pos + 1
    Next_1_play_5 = target_good_play_from(streak_counts_5,current_streak_pos,target_pos)
    target_pos = current_streak_pos + 2
    Next_2_play_5 = target_good_play_from(streak_counts_5,current_streak_pos,target_pos)    

    str(round(100*Next_1_play_1,2))

    player_1_dict = {'player': player_name_1, 'Next_1_play': round(100*Next_1_play_1,2), 'Next_2_play': round(100*Next_2_play_1,2)}
    player_2_dict = {'player': player_name_2, 'Next_1_play': round(100*Next_1_play_2,2), 'Next_2_play': round(100*Next_2_play_2,2)}
    player_3_dict = {'player': player_name_3, 'Next_1_play': round(100*Next_1_play_3,2), 'Next_2_play': round(100*Next_2_play_3,2)}
    player_4_dict = {'player': player_name_4, 'Next_1_play': round(100*Next_1_play_4,2), 'Next_2_play': round(100*Next_2_play_4,2)}
    player_5_dict = {'player': player_name_5, 'Next_1_play': round(100*Next_1_play_5,2), 'Next_2_play': round(100*Next_2_play_5,2)}
    ### can do this better:
    performance_list_table = [player_1_dict, player_2_dict, player_3_dict, player_4_dict, player_5_dict]
    return performance_list_table


def streak_counts_pos_neg(player_frame,pos_or_neg):
    # pos_or_neg = 'pos_streak_list' or 'neg_streak_list'
    player_values = player_frame[pos_or_neg].values
    streaks = [ast.literal_eval(x) for x in player_values]
    streak_counts = counts_from_streaks(streaks)
    return streak_counts



def current_play_description(this_game,row):
    return str(this_game.iloc[row].player) + ' with a ' + this_game.iloc[row].etype

def streak_counts_player_dates(player_frame, train_or_test):
    # return list of 4 predictions
    player_values = player_frame['pos_streak_list'].values
    streaks = [ast.literal_eval(x) for x in player_values]
    num = int(len(streaks)/2)
    if train_or_test == 'train':
        streaks_set = streaks[:num]
    else:
        streaks_set = streaks[num:]
    streak_counts = counts_from_streaks(streaks_set)
    return streak_counts


def unique_players_sql(database,table):
    conn = MySQLdb.connect(user="root",passwd="xxxx",db=database,
                           cursorclass=MySQLdb.cursors.DictCursor)
    cmd_target = 'SELECT DISTINCT player FROM streak_frame_with_perf;'
    df_players = pd.read_sql(cmd_target, con=conn)
    conn.close()
    return df_players