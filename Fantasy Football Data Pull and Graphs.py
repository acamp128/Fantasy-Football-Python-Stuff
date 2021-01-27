# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 23:09:11 2021

@author: Alex Campbell
This set of code will pull data from ESPN's fantasy football website using
methods described by researcher Steven Morse (github.com/stmorse) and use
the data to create interesting and hopefully insightful graphs.
"""
import requests
import pandas as pd
import matplotlib.pyplot as plt

league_id = 13260
year = 2019

#the base URL for the league from which we can add params to access
#different types of data
url = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/" + \
      str(league_id) + "?seasonId=" + str(year)
    
#pulls the mMatchups view of every matchup throughout the season (n=128)
#and puts them in JSON format. For some reason for non-current
#seasons this gets placed in a list of length 1. r.json() converts this
#unwieldy JSON text into a set of nested  data structure of Python data types
r = requests.get(url, params={"view": "mMatchup"})
d = r.json()[0]

#puts the scores for every week in a pandas dataframe for the sake of ease of 
#use and adds a "type" to distinguish whether this matchup occurred in the 
#regular season or in the playoffs.
df = [[
        game['matchupPeriodId'],
        game['home']['teamId'], game['home']['totalPoints'],
        game['away']['teamId'], game['away']['totalPoints']
    ] for game in d['schedule']]
df = pd.DataFrame(df, columns=['Week', 'Team1', 'Score1', 'Team2', 'Score2'])
df['Type'] = ['Regular' if w<=14 else 'Playoff' for w in df['Week']]

#print(df.head(5))
#print(df)


avgs = (df
        .filter(['Week', 'Score1', 'Score2'])
        .melt(id_vars = ['Week'], value_name = 'Score')
        .groupby('Week')
        .mean()
        .reset_index()
)
#print(avgs)

tm = 26

# grab all games with this team
df2 = df.query('Team1 == @tm | Team2 == @tm').reset_index(drop=True)

# move the team of interest to "Team1" column
ix = list(df2['Team2'] == tm)
df2.loc[ix, ['Team1','Score1','Team2','Score2']] = \
    df2.loc[ix, ['Team2','Score2','Team1','Score1']].values

# add new score and win cols
df2 = (df2
 .assign(Chg1 = df2['Score1'] - avgs['Score'],
         Chg2 = df2['Score2'] - avgs['Score'],
         Win  = df2['Score1'] > df2['Score2'])
)


# VISUALIZATION

fig, ax = plt.subplots(1,1, figsize=(8,8))

z = 60

ax.fill_between([0,z], 0, [0,z], facecolor='b', alpha=0.1)
ax.fill_between([-z,0], -z, [-z,0], facecolor='b', alpha=0.1)
ax.fill_between([0,z], [0,z], z, facecolor='r', alpha=0.1)
ax.fill_between([-z,0], [-z,0], 0, facecolor='r', alpha=0.1)

ax.scatter(data=df2.query('Win'), x='Chg1', y='Chg2', 
           c=['b' if t=='Regular' else 'y' for t in df2.query('Win')['Type']], 
           s=100,
           marker='o',
           label='Win')
ax.scatter(data=df2.query('not Win'), x='Chg1', y='Chg2', 
           c=['b' if t=='Regular' else 'r' for t in df2.query('not Win')['Type']], 
           s=100,
           marker='x',
           label='Loss')
ax.plot([-z,z],[-z,z], 'k--')

# ax.legend()

# center x/y axes on origin
ax.spines['left'].set_position('zero')
ax.spines['right'].set_color('none')
ax.spines['bottom'].set_position('zero')
ax.spines['top'].set_color('none')
ax.yaxis.tick_left()
ax.xaxis.tick_bottom()

# remove origin ticklabels
tx = list(range(-z,z+1,10))
tx.remove(0)
ax.yaxis.set(ticks=tx, ticklabels=tx)
ax.xaxis.set(ticks=tx, ticklabels=tx)

ax.tick_params(axis='x', colors='gray')
ax.tick_params(axis='y', colors='gray')

ax.text(z-10, -12, 'Points \n  for', style='italic')
ax.text(-18, z-10, ' Points \nagainst', style='italic')
ax.text(z/2-5, z-8, 'UNLUCKY\n   LOSS', style='italic', color='red')
ax.text(z-12, z/2-5, 'LUCKY\n WIN', style='italic', color='blue')

#ax.set(title='Team #%d scores (centered at league average)' % tm)
ax.set(title = 'Gerber Baby Food Championship Season Scores')

plt.show()


