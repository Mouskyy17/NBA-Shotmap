import streamlit as st
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.static import players
import matplotlib.pyplot as plt
from mplbasketball import Court
import pandas as pd
import zipfile
import seaborn as sns
import numpy as np

st.set_page_config(layout="wide")
st.title("NBA Shot Charts")
st.subheader("Compare FG% vs League Average")

# Chemin du fichier zip
zip_file = 'all_shots_df_2024-2025.zip'

# Extraire le fichier zip
with zipfile.ZipFile(zip_file, 'r') as zip_ref:
    zip_ref.extract('all_shots_df_2024-2025.csv', path='.')

df = pd.read_csv("all_shots_df_2024-2025.csv")

# Convert inches to feet
df["LOC_X"] = df["LOC_X"] / 12
df["LOC_Y"] = df["LOC_Y"] / 12

# Flip the Y-axis to match the vertical "vu" court
df["LOC_X"] = -df["LOC_X"] * 1.2
df["LOC_Y"] = -df["LOC_Y"] + 39

team = st.selectbox("Select a team", df["TEAM_NAME"].unique())
player = st.selectbox("Select a player", df[df["TEAM_NAME"] == team]["PLAYER_NAME"].unique(), index=None)

def calculate_hexbin_stats(data, gridsize=30):
    hb = plt.hexbin(
        data["LOC_X"], data["LOC_Y"],
        gridsize=gridsize, extent=(-50, 50, -10, 60),
        reduce_C_function=np.count_nonzero, mincnt=1
    )
    x, y = hb.get_offsets().T
    coords = pd.DataFrame({"x": x, "y": y})

    coords["total_shots"] = hb.get_array()
    made = []
    for xi, yi in zip(x, y):
        mask = (
            (data["LOC_X"] >= xi - 1) & (data["LOC_X"] <= xi + 1) &
            (data["LOC_Y"] >= yi - 1) & (data["LOC_Y"] <= yi + 1)
        )
        made.append(data.loc[mask, "SHOT_MADE_FLAG"].sum())
    coords["fg_pct"] = coords["total_shots"].where(coords["total_shots"] > 0, np.nan)
    coords["fg_pct"] = [m/t if t > 0 else np.nan for m, t in zip(made, coords["total_shots"])]
    return coords

def filter_data(df, team, player):
    if team:
        df_team = df[df["TEAM_NAME"] == team]
    else:
        df_team = df.copy()

    if player:
        df_player = df_team[df_team["PLAYER_NAME"] == player]
        court = Court(court_type="nba", origin="center", units="ft")
        fig, ax = court.draw(orientation="vu")

        fig.patch.set_facecolor('black')
        ax.set_facecolor("black")

        # League FG% par hexagone
        league_stats = calculate_hexbin_stats(df)

        # FG% du joueur
        player_stats = calculate_hexbin_stats(df_player)

        # Merge
        merged = pd.merge(player_stats, league_stats, on=['x', 'y'], suffixes=('_player', '_league'))
        merged["fg_diff"] = merged["fg_pct_player"] - merged["fg_pct_league"]

        # Plot
        cmap = sns.color_palette("coolwarm", as_cmap=True)
        sc = ax.scatter(
            merged["x"], merged["y"],
            s=merged["total_shots_player"] * 5,
            c=merged["fg_diff"],
            cmap=cmap,
            vmin=-0.1, vmax=0.1,
            edgecolors='none'
        )

        cbar = plt.colorbar(sc, ax=ax, shrink=0.7, pad=0.02)
        cbar.set_label('FG% vs. League Avg', color='white')
        cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')

        ax.set_title(f"{player} Shot Chart vs League Avg", color="white", fontsize=14)
        ax.tick_params(colors='white')

        st.pyplot(fig)

    return df

filtered_df = filter_data(df, team, player)
