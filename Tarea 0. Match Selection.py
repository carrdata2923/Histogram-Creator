#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
from statsbombpy import sb
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.title("StatsBomb Shot Map")

st.write("Loading competition data...")
competitions_df = sb.competitions()
st.dataframe(competitions_df)

# Sidebar for user selections
st.sidebar.header("Select Competition and Match")
selected_competition = st.sidebar.selectbox("Select Competition:", competitions_df['competition_name'].unique())

# Filter seasons based on selected competition
available_seasons = competitions_df[competitions_df['competition_name'] == selected_competition]['season_name'].unique()
selected_season = st.sidebar.selectbox("Select Season:", available_seasons)

# Get competition and season IDs
competition_id = competitions_df.loc[competitions_df['competition_name'] == selected_competition, 'competition_id'].iloc[0]
season_id = competitions_df.loc[(competitions_df['competition_name'] == selected_competition) & (competitions_df['season_name'] == selected_season), 'season_id'].iloc[0]

st.write(f"Loading matches for {selected_competition} - {selected_season}...")
matches_df = sb.matches(competition_id=competition_id, season_id=season_id)
st.dataframe(matches_df)

selected_match = st.sidebar.selectbox("Select Match:", matches_df['home_team_name'] + ' vs ' + matches_df['away_team_name'])
match_id = matches_df.loc[matches_df['home_team_name'] + ' vs ' + matches_df['away_team_name'] == selected_match, 'match_id'].iloc[0]

st.write(f"Loading event data for match ID: {match_id}...")
events_df = sb.events(match_id=match_id)
st.dataframe(events_df.head())

# Filter for shot events
shots_df = events_df[events_df['type_name'] == 'Shot'].copy()

if not shots_df.empty:
    st.subheader("Shot Map")

    # Prepare pitch
    pitch = Pitch(pitch_type='statsbomb', line_color='black', goal_type='box')
    fig, ax = pitch.draw(figsize=(12, 8))

    # Plot shots
    for i, row in shots_df.iterrows():
        x = row['location'][0]
        y = row['location'][1]
        goal = row['shot_outcome_name'] == 'Goal'
        circle_size = 2  # Adjust as needed
        if goal:
            pitch.scatter(x, y, color='lime', s=circle_size * 100, marker='o', edgecolors='black', linewidth=1, alpha=0.7, ax=ax)
        else:
            pitch.scatter(x, y, color='red', s=circle_size * 100, marker='o', edgecolors='black', linewidth=1, alpha=0.7, ax=ax)

        # Annotate player name for each shot (optional)
        ax.annotate(row['player_name'].split()[-1], (x + 1, y + 1), textcoords="offset points", xytext=(0,5), ha='left', color='black', fontsize=8)

    st.pyplot(fig)

    st.subheader("Shot Data")
    st.dataframe(shots_df[['player_name', 'team_name', 'location', 'shot_outcome_name']])

else:
    st.warning("No shot events found for the selected match.")
