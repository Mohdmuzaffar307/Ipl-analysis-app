import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

# app styling
st.set_page_config(layout="wide")
# CSS for changing background color
page_bg_style = """
<style>
    /* Change the background of the main content area */
    [data-testid="stAppViewContainer"] {
        background-color: #3c768c; /* Replace with your desired color */
    }

    /* Optionally change the sidebar background color */
    [data-testid="stSidebar"] {
        background-color: #203940; /* Replace with your desired color */      
    }
    

</style>
"""
# Inject CSS
st.markdown(page_bg_style, unsafe_allow_html=True)

#sidebar styling
import streamlit as st

# Styling buttons and other widgets in the sidebar
st.sidebar.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
        border: none;
        border-radius: 25px;
        padding: 10px 20px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #4a2704;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)



#Importing Dataset
ipl=pd.read_csv('ipl_claened.csv')
### MAIN PAGE
st.markdown("""
    <h1 style="color: #600606; text-align: center;font-size: 60px;"> Welcome to IPL League</h1>
""",unsafe_allow_html=True)

image = Image.open("teams.jpg")
st.image(image,  use_container_width=True)
### INDIVIDUAL BATTERS

batter=sorted(list(ipl['batter'].unique()))

st.sidebar.header("IPL Analysis")
st.sidebar.title('Choose Section')

# Choosing Batsman name
batsman_name=st.sidebar.selectbox("Batsman",batter)

# making Summery data for batsman run
runs=ipl.groupby(['match_id','batter','batting_team','bowling_team'])["batsman_runs"].sum().reset_index()
ball=ipl.groupby(['match_id','batter','batting_team'])["ball"].count().reset_index()
fours=ipl.query('batsman_runs==4').groupby(['match_id','batter','batting_team'])['batsman_runs'].count().reset_index()
sixs=ipl.query('batsman_runs==6').groupby(['match_id','batter','batting_team'])['batsman_runs'].count().reset_index()
batsman_rec=runs.merge(ball,left_on=['match_id','batter'],right_on=['match_id','batter']).merge(sixs,left_on=['match_id','batter'],right_on=['match_id','batter'],how='left').drop(columns=['batting_team_y','batting_team']).merge(fours,left_on=['match_id','batter'],right_on=['match_id','batter'],how='left').drop(columns=['batting_team']).rename(columns={'batsman_runs_x':'Batsman_runs','batsman_runs_y':'six','batsman_runs':'fours','batting_team_x':"batting_team"})
batsman_rec.fillna(0,inplace=True)
batsman_rec['Sr']=round((batsman_rec['Batsman_runs']/batsman_rec['ball'])*100,2)
batsman_rec.set_index('match_id',inplace=True)

##############################################
#Total match Played
total_match=len(batsman_rec[batsman_rec['batter']==batsman_name])

# Total Run Calculation
batsman_total_runs=ipl.groupby(['batter'])['batsman_runs'].sum().reset_index()
total_runs=batsman_rec[batsman_rec['batter']==batsman_name]["Batsman_runs"].sum()
btn1=st.sidebar.button('fetch Details')
# player of the match
total_mom=len(ipl[ipl['player_of_match']==batsman_name].groupby('match_id').size().values)

#Dismissle type
playes_diss=ipl.groupby(['player_dismissed','dismissal_kind']).size().reset_index().rename(columns={0:"# of times"})

#Centuries Calculation
centuries=batsman_rec[batsman_rec['Batsman_runs']>=100].groupby('batter').size().reset_index().rename(columns={0:"# of Centuries"})

result=0
if len(list(centuries[centuries['batter']==batsman_name]['# of Centuries'].values))<1:
     result=0
else:
    result=centuries[centuries['batter']==batsman_name]['# of Centuries'].values[0]

# Fiftees Calculatiion
fiftees=batsman_rec[(batsman_rec['Batsman_runs']<100) & (batsman_rec['Batsman_runs']>=50) ].groupby('batter').size().reset_index().rename(columns={0:"# of Fiftees"})
result2=0
if len(list(fiftees[fiftees['batter']==batsman_name]['# of Fiftees'].values))<1:
     result2=0
else:
    result2=fiftees[fiftees['batter']==batsman_name]['# of Fiftees'].values[0]

##Average Calculation
ipldiss=ipl.query('batter==@batsman_name').groupby('match_id')['player_dismissed'].count().reset_index()
avg=round(ipl.query('batter==@batsman_name').groupby('batter')['batsman_runs'].sum().values[0]/len(ipl.query('player_dismissed==@batsman_name')),2)

## Max Score
max_score=batsman_rec[batsman_rec['batter']==batsman_name]["Batsman_runs"].max()

# ##  dissmissel kind
bowler=ipl.query("player_dismissed.notna()")[['match_id','bowler','batter']]
batsman_rec=batsman_rec.merge(bowler,left_on=['match_id','batter'],right_on=['match_id','batter'])

#Big matches
big_match=ipl.query("batter==@batsman_name and match_type in ['Final', 'Semi Final']").groupby(['match_type','season']).agg({'batsman_runs': 'sum'}).reset_index()

##Seasion reco
ipl['season']=ipl['season'].astype(str)
ipl['season']=ipl['season'].str.strip()
season_rec=ipl.groupby(['season','batter'])['batsman_runs'].sum().reset_index()
season_rec['season']=season_rec['season'].astype(str)
ball_played=ipl.groupby(['season','batter'])['ball'].count().reset_index()
season_rec=season_rec.merge(ball_played,left_on=['season','batter'],right_on=['season','batter'])
season_rec["Strike Rate"]=round(((season_rec['batsman_runs']/season_rec['ball'])*100),2)
seas0n_sixes=ipl.query('batsman_runs==6').groupby(['season','batter'])['batsman_runs'].count().reset_index()
seas0n_fours=ipl.query('batsman_runs==4').groupby(['season','batter'])['batsman_runs'].count().reset_index()
sixes_and_fours=seas0n_sixes.merge(seas0n_fours,left_on=['season','batter'],right_on=['season','batter']).rename(columns={"batsman_runs_x":"Sixes","batsman_runs_y":"Fours"})
season_rec=season_rec.merge(sixes_and_fours,left_on=['season','batter'],right_on=['season','batter'])

## Carrer line chart
season_rec['season']=season_rec['season'].str.replace('2020/21','2020')
season_rec['season']=season_rec['season'].str.replace('2009/10','2010')
season_rec['season']=season_rec['season'].str.replace('2007/08','2008')

#Fetch batter Details
if btn1:
    st.header("{} IPL Perforamnce".format(batsman_name))
    st.markdown("""
    <h1 style="color: #084704; text-align: center;"> Overall Performance </h1>
    """,unsafe_allow_html=True)
    st.subheader("Total Match Played: {}".format(total_match))
    st.subheader("Total Scored: {}".format(total_runs))
    st.subheader("Average: {}".format(avg))
    st.subheader("Total Centuries: {}".format(result))
    st.subheader("Total Fiftees : {}".format(result2))
    st.subheader("Max Score : {}".format(max_score))
    st.subheader("Total Player of the match award: {}".format(total_mom))
    #Individual matches
    st.table(batsman_rec[batsman_rec['batter']==batsman_name].set_index("match_id"))
    ## Per Season
    st.markdown("""
       <h1 style="color: #084704; text-align: center;"> Season Performance </h1>
       """, unsafe_allow_html=True)
    st.table(season_rec[season_rec['batter']==batsman_name].set_index("season"))
    st.markdown("""
          <h1 style="color: #084704; text-align: center;"> Big Match Performance </h1>
          """, unsafe_allow_html=True)
    st.table(big_match)

    st.markdown("""
             <h1 style="color: #084704; text-align: center;"> Season Trends </h1>
             """, unsafe_allow_html=True)
    # season line chart
    st.plotly_chart(px.line(season_rec[season_rec['batter'] == batsman_name], x='season', y='batsman_runs',title="Performance By Season"))

    #Dissmissile chart
    st.markdown("""
             <h1 style="color: #084704; text-align: center;"> Dismissle Types </h1>
             """, unsafe_allow_html=True)
    temp_df=playes_diss[playes_diss['player_dismissed']==batsman_name]
    st.plotly_chart(px.pie(temp_df, values='# of times', names='dismissal_kind',title="Dismissle Kind"))



    st.balloons()




#Fetch bowler Details
bowler=sorted(list(ipl['bowler'].unique()))
bowler_name=st.sidebar.selectbox("Bowler",bowler)
btn2=st.sidebar.button('Bowler Statics')

##Bowler stats Calculation
total_over=ipl.query("bowler==@bowler_name").groupby(['match_id','bowler',"bowling_team",'batting_team'])['ball'].count().reset_index()
runs_agains_bowler=ipl.query("bowler==@bowler_name").groupby(['match_id','bowler',"bowling_team",'batting_team'])['batsman_runs'].sum().reset_index()
wicket=ipl.query("bowler==@bowler_name").groupby(['match_id'])['player_dismissed'].count().reset_index()
bowlwer_stats=total_over.merge(runs_agains_bowler,left_on=['match_id','bowler',"bowling_team",'batting_team'],right_on=['match_id','bowler',"bowling_team",'batting_team'])
bowlwer_stats=bowlwer_stats.merge(wicket,left_on=['match_id'],right_on=['match_id'],how='left')
bowlwer_stats['Over']=round((bowlwer_stats['ball']/6),0)
bowlwer_stats['Extra_ball']=bowlwer_stats['ball']-(bowlwer_stats['Over']*6)
bowlwer_stats['Economy']=bowlwer_stats['batsman_runs']/bowlwer_stats['Over']
total_wicket=ipl.query("bowler==@bowler_name")['player_dismissed'].count()
total_match_bowler=len(bowlwer_stats.merge(wicket,left_on=['match_id'],right_on=['match_id'],how='left'))
econmy=bowlwer_stats['batsman_runs'].sum()/bowlwer_stats['Over'].sum()
total_over=bowlwer_stats['Over'].sum()


#season by season calculation
seson_diss=ipl.groupby(['season','bowler'])['player_dismissed'].count().reset_index()
season_runs=ipl.groupby(['season','bowler'])['batsman_runs'].sum().reset_index()
season_balls=ipl.groupby(['season','bowler'])['ball'].count().reset_index()
season_balls["Overs"]=round((season_balls['ball']/6),0).astype(int)

bowler_season_stats=season_balls.merge(seson_diss,left_on=['season','bowler'],right_on=['season','bowler']).merge(season_runs,left_on=['season','bowler'],right_on=['season','bowler'])
bowler_season_stats['Economy']=bowler_season_stats['batsman_runs']/bowler_season_stats['Overs']

bowler_season_stats=bowler_season_stats[['season','bowler','Overs','batsman_runs','player_dismissed','Economy']].rename(columns={'batsman_runs':'runs','player_dismissed':'wickets'})

bowler_season_stats['season']=bowler_season_stats['season'].str.replace('2020/21','2020')
bowler_season_stats['season']=bowler_season_stats['season'].str.replace('2009/10','2010')
bowler_season_stats['season']=bowler_season_stats['season'].str.replace('2007/08','2008')
bowler_season_stats['season']=bowler_season_stats['season'].astype('int')



if btn2:
    st.subheader("Total Match Played: {}".format(total_match_bowler))
    st.subheader("Total Overs: {}".format(total_over))
    st.subheader("Overall Economy: {}".format(round(econmy),2))
    st.subheader("Total Wicket: {}".format(round(total_wicket), 2))
    st.markdown("""
             <h1 style="color: #084704; text-align: center;"> Overall Performance </h1>
             """, unsafe_allow_html=True)
    st.table(bowlwer_stats[bowlwer_stats['bowler'] == bowler_name].set_index('match_id'))
    st.markdown("""
          <h1 style="color: #084704; text-align: center;"> Season Performance </h1>
          """, unsafe_allow_html=True)
    st.table(bowler_season_stats[bowler_season_stats['bowler'] == bowler_name].set_index('season'))

    #bowler wickets pie chart
    temp = ipl.groupby(['season', 'bowler', 'dismissal_kind']).size().reset_index().rename(columns={0: "count"})
    st.plotly_chart(px.pie(temp.query('bowler==@bowler_name'),values='count',names='dismissal_kind',title="Dismissle Kind"))

    #economy graphs
    st.plotly_chart(px.line(bowler_season_stats.query('bowler==@bowler_name'), x='season', y='Economy',title='Economy Per Showing'))
    st.balloons()


#Teams Performance
bt=ipl[['bowling_team']]
bat=ipl[['batting_team']]
team_name=sorted(pd.concat([bt, bat], ignore_index=True,axis=1)[0].unique())


#Fetch team Details

teams=st.sidebar.selectbox("Teams Performance",team_name)
btn3=st.sidebar.button('Team Statics')


#total Matches
team_total_match=len(ipl.query('(bowling_team == @teams and batting_team != @teams) or (batting_team == @teams and bowling_team != @teams ) ').groupby('match_id').size().reset_index())
#total win
team_total_match_won=len(ipl.query('winner==@teams ').groupby('match_id').size().reset_index())
## calc
total_trophy=len(ipl.query('match_type=="Final" and winner== @teams').groupby(['season','winner']).size())


# Using numpy.where() to assign 'runner' column based on condition
ipl['runner'] = np.where(ipl['winner'] == ipl['batting_team'], ipl['bowling_team'], ipl['batting_team'])

final_match=ipl.query('match_type=="Final" and winner== @teams').groupby(['season','winner','runner','player_of_match']).size().reset_index().drop(columns=0,axis=1)

#top batters
top_10_batter=ipl.query('batting_team== @teams or bowling_team ==@teams').groupby(['batter'])['batsman_runs'].sum().reset_index().sort_values('batsman_runs',ascending=False).head(10)

#top bowlers
bowler_wickets=ipl.query("dismissal_kind not in ['run out','retired hurt','retired out']")
bowler_wicket_rec=bowler_wickets.groupby(['bowler','bowling_team'])['player_dismissed'].count().reset_index().sort_values('player_dismissed',ascending=False)
top_10_bowler=bowler_wicket_rec.query('bowling_team==@teams').head(10)

if btn3:
    st.header(teams)
    st.subheader(f'{teams} played total {team_total_match} Matches and Won {team_total_match_won} Matches')
    st.subheader(f'{teams} winning percentage is {round((team_total_match_won/team_total_match)*100)}%')
    if total_trophy >=1:
        st.subheader("Total Trophy 😎 : {}".format(total_trophy))
    else:
        st.subheader("Total Trophy 🥹😭 : {}".format(total_trophy))
    st.markdown("""
             <h1 style="color: #084704; text-align: center;"> Final Records </h1>
             """, unsafe_allow_html=True)
    st.table(final_match)

    st.markdown("""
             <h1 style="color: #084704; text-align: center;"> Top Batters </h1>
             """, unsafe_allow_html=True)
    st.table(top_10_batter)
    st.markdown("""
             <h1 style="color: #084704; text-align: center;"> Top Bowlers </h1>
             """, unsafe_allow_html=True)
    st.table(top_10_bowler)
    st.balloons()


player_vs_team=st.sidebar.button('Batter Vs Team')
total_match_against=len(batsman_rec.query("batter==@batsman_name and bowling_team==@teams"))
batsman_run_against = batsman_rec.query("batter==@batsman_name and bowling_team== @teams")['Batsman_runs'].sum()

batsman_sixes_against= batsman_rec.query("batter==@batsman_name and bowling_team==@teams")['six'].sum()
batsman_fours_against=batsman_rec.query("batter==@batsman_name and bowling_team==@teams")['fours'].sum()

average_against_team=ipl.query("batter=='V Kohli' and bowling_team=='Sunrisers Hyderabad'").groupby('match_id').agg({'batsman_runs':'sum','player_dismissed':'count'}).reset_index()
average=round(average_against_team['batsman_runs'].sum()/average_against_team['player_dismissed'].sum(),2)
if player_vs_team:

    st.subheader("{} Total Match Played {} : {}".format(batsman_name, teams, total_match_against))
    st.subheader("{} score aginst {} : {}".format(batsman_name,teams,batsman_run_against))
    st.subheader("{} average aginst {} is {}".format(batsman_name,teams,average))
    st.subheader("Sixes:  {} :".format(batsman_sixes_against))
    st.subheader("Fours: {}".format(batsman_fours_against))
    st.table(batsman_rec.query("batter==@batsman_name and bowling_team== @teams"))
    st.balloons()


team1_name=sorted(pd.concat([bt, bat], ignore_index=True,axis=1)[0].unique())
team2_name=sorted(pd.concat([bt, bat], ignore_index=True,axis=1)[0].unique())
team1_name_selected=st.sidebar.selectbox("Choose team 1",team1_name)
team2_name_selected=st.sidebar.selectbox("Choose team 2",team2_name)
total_match=len(ipl.query("batting_team==@team1_name_selected and bowling_team== @team2_name_selected ").groupby(['match_id','batting_team','bowling_team','winner']).size())
team1_won=len(ipl.query("batting_team==@team1_name_selected and bowling_team==@team2_name_selected and winner==@team1_name_selected ").groupby(['match_id','batting_team','bowling_team','winner']).size())
team2_won=len(ipl.query("batting_team==@team1_name_selected and bowling_team==@team2_name_selected and winner==@team2_name_selected ").groupby(['match_id','batting_team','bowling_team','winner']).size())

team1won_during_bat=len(ipl.query("batting_team==@team1_name_selected and bowling_team==@team2_name_selected and winner==@team1_name_selected and toss_decision=='bat' ").groupby(['match_id','batting_team','bowling_team','winner','toss_decision']).size())
team2won_during_bat=len(ipl.query("batting_team==@team1_name_selected and bowling_team==@team2_name_selected and winner==@team2_name_selected and toss_decision=='bat' ").groupby(['match_id','batting_team','bowling_team','winner','toss_decision']).size())

team1_field=len(ipl.query("batting_team==@team1_name_selected and bowling_team==@team2_name_selected and winner==@team1_name_selected and toss_decision=='field' ").groupby(['match_id','batting_team','bowling_team','winner','toss_decision']).size())
team2_field=len(ipl.query("batting_team==@team1_name_selected and bowling_team==@team2_name_selected and winner==@team2_name_selected and toss_decision=='field' ").groupby(['match_id','batting_team','bowling_team','winner','toss_decision']).size())
btn4=st.sidebar.button('Campare')
if btn4:
    st.subheader(f'Toatal Matches B/W {team1_name_selected} and {team2_name_selected} is {total_match}')
    st.subheader(f'{team1_name_selected} won {team1_won} and {team2_name_selected} won {team2_won}')
    st.subheader(f'{team1_name_selected} won  during bat first {team1won_during_bat} time  {team2_name_selected} won {team2won_during_bat} times')
    st.subheader( f'{team1_name_selected} won  during field first {team1_field} time  {team2_name_selected} won {team2_field} times')



