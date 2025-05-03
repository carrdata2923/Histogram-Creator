#!/usr/bin/env python
# coding: utf-8

# # Redes de pases antes del primer cambio
# match_id=18245

# In[2]:


import matplotlib.pyplot as plt
import numpy as np
from mplsoccer import Pitch, Sbopen
import pandas as pd


# In[3]:


parser = Sbopen()
df, related, freeze, tactics = parser.event(18245)


# In[4]:


df.head(2)


# In[5]:


#avisamos a python de dónde empiezan los substitutos para que no los añada al gráfico de pases
sub = df.loc[df["type_name"] == "Substitution"].loc[df["team_name"] == "Real Madrid"].iloc[0]["index"]

#convertimos el archivo al dato de pases correctos de Real Madrid antes de los cambios
mask_cdm = (df["type_name"] == 'Pass') & (df["team_name"] == "Real Madrid") & (df.index < sub) & (df["outcome_name"].isnull())

#añadimos las columnas que son necesarias para crear la red de pases
df_pass = df.loc[mask_cdm, ['x', 'y', 'end_x', 'end_y', "player_name", "pass_recipient_name"]]

#hacemos que sólo aparezcan los apellidos de los jugadores
df_pass["player_name"] = df_pass["player_name"].apply(lambda x: str(x).split()[-1])
df_pass["pass_recipient_name"] = df_pass["pass_recipient_name"].apply(lambda x: str(x).split()[-1])


# In[6]:


players11_rm = df_pass['player_name'].unique()
players11_rm


# In[7]:


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


# In[8]:


scatter_df = pd.DataFrame()
for i, name in enumerate(df_pass["player_name"].unique()):
    passx = df_pass.loc[df_pass["player_name"] == name]["x"].to_numpy()
    recx = df_pass.loc[df_pass["pass_recipient_name"] == name]["end_x"].to_numpy()
    passy = df_pass.loc[df_pass["player_name"] == name]["y"].to_numpy()
    recy = df_pass.loc[df_pass["pass_recipient_name"] == name]["end_y"].to_numpy()
    scatter_df.at[i, "player_name"] = name

    # nos aseguramos de que la localización de cada jugador, es su media de pases y de recepciones
    scatter_df.at[i, "x"] = np.mean(np.concatenate([passx, recx]))
    scatter_df.at[i, "y"] = np.mean(np.concatenate([passy, recy]))

    scatter_df.at[i, "no"] = df_pass.loc[df_pass["player_name"] == name].count().iloc[0]

# ajustamos el tamaño del círculo para que sea más grande cuando más pases da ese jugador
scatter_df['marker_size'] = (scatter_df['no'] / scatter_df['no'].max()) * 1500


# In[9]:


#contar los pases entre un jugador y otro

df_pass["pair_key"] = df_pass.apply(lambda x: "_".join(sorted([x["player_name"], x["pass_recipient_name"]])), axis=1)
lines_df = df_pass.groupby(["pair_key"]).x.count().reset_index()
lines_df.rename({'x': 'pass_count'}, axis='columns', inplace=True)

lines_df = lines_df[lines_df['pass_count'] > 2]


# In[10]:


#dibujo del terreno de juego

pitch = Pitch(line_color='black')
fig, ax = pitch.grid(grid_height=0.6, title_height=0.06, axis=False,
                    endnote_height=0.04, title_space=-0.3, endnote_space=0)

pitch.scatter(scatter_df.x, scatter_df.y, s=scatter_df.marker_size, color='red', edgecolors='grey', linewidth=1, alpha=1, ax=ax["pitch"], zorder = 3)

# diseño del tipo de letra del jugador

for i, row in scatter_df.iterrows():
    pitch.annotate(row.player_name, xy=(row.x, row.y), c='black', va='center', ha='center', weight="bold", size=12, ax=ax["pitch"], zorder = 4)

fig.suptitle("Redes de pases - Real Madrid", fontsize=15)
fig.text(0.5, 0.94, "Antes del primer cambio", ha='center', fontsize=10, color='gray') # Change X and Y.

plt.show()


# In[11]:


#generar las líneas de los pases

pitch = Pitch(line_color='grey')
fig, ax = pitch.grid(grid_height=0.6, title_height=0.06, axis=False,
                    endnote_height=0.04, title_space=-0.3, endnote_space=0)

pitch.scatter(scatter_df.x, scatter_df.y, s=scatter_df.marker_size, color='red', edgecolors='grey', linewidth=1, alpha=1, ax=ax["pitch"], zorder = 3)

for i, row in scatter_df.iterrows():
    pitch.annotate(row.player_name, xy=(row.x, row.y), c='black', va='center', ha='center', weight="bold", size=12, ax=ax["pitch"], zorder = 4 )

for i, row in lines_df.iterrows():
    player1 = row["pair_key"].split("_")[0]
    player2 = row["pair_key"].split("_")[1]

    player1_x = scatter_df.loc[scatter_df["player_name"] == player1]["x"].iloc[0]
    player1_y = scatter_df.loc[scatter_df["player_name"] == player1]["y"].iloc[0]
    player2_x = scatter_df.loc[scatter_df["player_name"] == player2]["x"].iloc[0]
    player2_y = scatter_df.loc[scatter_df["player_name"] == player2]["y"].iloc[0]
    num_passes = row["pass_count"]

    line_width = (num_passes / lines_df['pass_count'].max()) * 10

    pitch.lines(player1_x, player1_y, player2_x, player2_y,
                alpha=1, lw=line_width, zorder=2, color="red", ax=ax["pitch"])

fig.suptitle("Redes de pases Real Madrid vs Liverpool", fontsize=15)
# Subtitle
fig.text(0.5, 0.94, "Antes de lesionarse Carvajal", ha='center', fontsize=10, color='gray') # Change X and Y.
plt.show()


# In[12]:


# Count passes made by Keylor Navas
navas_passes_count = len(df_pass[df_pass['player_name'] == 'Keylor Navas'])

# Print the result
print(f"Keylor Navas made {navas_passes_count} passes.")

#If you want to count the passes where he was the recipient.
navas_received_passes_count = len(df_pass[df_pass['pass_recipient_name'] == 'Keylor Navas'])

print(f"Keylor Navas received {navas_received_passes_count} passes.")

#If you want to count the total of passes where he was involved.
navas_total_passes_involved = navas_passes_count + navas_received_passes_count

print(f"Keylor Navas was involved in {navas_total_passes_involved} passes.")







