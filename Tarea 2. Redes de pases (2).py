#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from mplsoccer import Pitch, Sbopen
import pandas as pd

# --- Data Loading and Processing ---
@st.cache_data  # Cache the data to avoid reloading on every interaction
def load_and_process_data(match_id):
    parser = Sbopen()
    df, related, freeze, tactics = parser.event(match_id)

    # Avisamos a python de dónde empiezan los substitutos para que no los añada al gráfico de pases
    sub = df.loc[df["type_name"] == "Substitution"].loc[df["team_name"] == "Real Madrid"].iloc[0]["index"]

    # Convertimos el archivo al dato de pases correctos de Real Madrid antes de los cambios
    mask_cdm = (df["type_name"] == 'Pass') & (df["team_name"] == "Real Madrid") & (df.index < sub) & (df["outcome_name"].isnull())

    # Añadimos las columnas que son necesarias para crear la red de pases
    df_pass = df.loc[mask_cdm, ['x', 'y', 'end_x', 'end_y', "player_name", "pass_recipient_name"]]

    # Hacemos que sólo aparezcan los apellidos de los jugadores
    df_pass["player_name"] = df_pass["player_name"].apply(lambda x: str(x).split()[-1])
    df_pass["pass_recipient_name"] = df_pass["pass_recipient_name"].apply(lambda x: str(x).split()[-1])

    # Name mapping dictionary
    nombre_mapeo = {
        'Varane': 'Varane',
        'Modrić': 'Modric',
        'Júnior': 'Marcelo',
        'Ramos': 'Carvajal',
        'Casimiro': 'Casemiro',
        'García': 'Ramos',
        'Aveiro': 'Cristiano Ronaldo',
        'Benzema': 'Benzema',
        'Gamboa': 'Keylor Navas',
        'Suárez': 'Isco',
        # Add more mappings as needed
    }

    # Apply the mapping to both columns
    df_pass["player_name"] = df_pass["player_name"].map(nombre_mapeo).fillna(df_pass["player_name"])
    df_pass["pass_recipient_name"] = df_pass["pass_recipient_name"].map(nombre_mapeo).fillna(df_pass["pass_recipient_name"])

    return df_pass

@st.cache_data
def create_scatter_df(df_pass):
    scatter_df = pd.DataFrame()
    for i, name in enumerate(df_pass["player_name"].unique()):
        passx = df_pass.loc[df_pass["player_name"] == name]["x"].to_numpy()
        recx = df_pass.loc[df_pass["pass_recipient_name"] == name]["end_x"].to_numpy()
        passy = df_pass.loc[df_pass["player_name"] == name]["y"].to_numpy()
        recy = df_pass.loc[df_pass["pass_recipient_name"] == name]["end_y"].to_numpy()
        scatter_df.at[i, "player_name"] = name

        # Nos aseguramos de que la localización de cada jugador, es su media de pases y de recepciones
        scatter_df.at[i, "x"] = np.mean(np.concatenate([passx, recx]))
        scatter_df.at[i, "y"] = np.mean(np.concatenate([passy, recy]))

        scatter_df.at[i, "no"] = df_pass.loc[df_pass["player_name"] == name].count().iloc[0]

    # Ajustamos el tamaño del círculo para que sea más grande cuando más pases da ese jugador
    scatter_df['marker_size'] = (scatter_df['no'] / scatter_df['no'].max()) * 1500
    return scatter_df

@st.cache_data
def create_lines_df(df_pass):
    # Contar los pases entre un jugador y otro
    df_pass["pair_key"] = df_pass.apply(lambda x: "_".join(sorted([x["player_name"], x["pass_recipient_name"]])), axis=1)
    lines_df = df_pass.groupby(["pair_key"]).x.count().reset_index()
    lines_df.rename({'x': 'pass_count'}, axis='columns', inplace=True)
    lines_df = lines_df[lines_df['pass_count'] > 2]
    return lines_df

# --- Streamlit App ---
st.title("Real Madrid Pass Networks (Before First Substitution)")
match_id = st.sidebar.number_input("Enter Match ID:", value=18245)

df_pass = load_and_process_data(match_id)
scatter_df = create_scatter_df(df_pass)
lines_df = create_lines_df(df_pass)

# --- Plot 1: Player Positions ---
st.subheader("Player Positions and Pass Frequency")
pitch = Pitch(line_color='black')
fig1, ax1 = pitch.grid(grid_height=0.6, title_height=0.06, axis=False,
                        endnote_height=0.04, title_space=-0.3, endnote_space=0)

pitch.scatter(scatter_df.x, scatter_df.y, s=scatter_df.marker_size, color='red', edgecolors='grey', linewidth=1, alpha=1, ax=ax1["pitch"], zorder = 3)

# Diseño del tipo de letra del jugador
for i, row in scatter_df.iterrows():
    pitch.annotate(row.player_name, xy=(row.x, row.y), c='black', va='center', ha='center', weight="bold", size=12, ax=ax1["pitch"], zorder = 4)

fig1.suptitle(f"Pass Networks - Real Madrid (Match ID: {match_id})", fontsize=15)
fig1.text(0.5, 0.94, "Before the first substitution", ha='center', fontsize=10, color='gray')

st.pyplot(fig1)

