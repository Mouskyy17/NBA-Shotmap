import streamlit as st
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.static import players
import matplotlib.pyplot as plt
from mplbasketball import Court
import pandas as pd
import zipfile


st.title("NBA Shot Charts")
st.subheader("Filter on any team and player to get their shot chart data")

# Chemin du fichier zip
zip_file = 'all_shots_df_2024-2025.zip'

# Extraire le fichier zip
with zipfile.ZipFile(zip_file, 'r') as zip_ref:
    # Liste des fichiers dans le zip
    zip_ref.printdir()
    
    # Extraire le fichier CSV
    zip_ref.extract('all_shots_df_2024-2025.csv', path='.')



df = pd.read_csv("all_shots_df_2024-2025.csv")

# Convert inches to feet
df["LOC_X"] = df["LOC_X"] / 12
df["LOC_Y"] = df["LOC_Y"] / 12

# Flip the Y-axis to match the vertical "vu" court
df["LOC_X"] = -df["LOC_X"] * 1.2
df["LOC_Y"] = -df["LOC_Y"] + 39


team_names = df["TEAM_NAME"]

team = st.selectbox(
    "Select a team",
    df["TEAM_NAME"]
    .loc[
        team_names.apply(
            lambda x: (x.split()[-1] if x != "Portland Trail Blazers" else x.split()[1])
        )
        .sort_values()
        .index
    ]
    .unique(),
)
player = st.selectbox(
    "Select a player",
    df[df["TEAM_NAME"] == team]["PLAYER_NAME"].unique(),
    index=None,
)


def filter_data(df, team, player):
    if team:
        df = df[df["TEAM_NAME"] == team]

    if player:
        df = df[df["PLAYER_NAME"] == player]

        court = Court(court_type="nba", origin="center", units="ft")
        fig, ax = court.draw(orientation="vu")

        def plot_shots(df, ax, court):

            # Plotting the heat map using hexbin
            hb = ax.hexbin(
                df["LOC_X"],
                df["LOC_Y"],
                gridsize=30,
                cmap="cividis",
                zorder=0,
                extent=(-50, 70, -50, 70),
            )

            # Adding color bar to show shot frequency
            plt.colorbar(hb, ax=ax, label="Shot Frequency")

        plot_shots(df, ax, court)

        st.pyplot(fig)

    return df


filtered_df = filter_data(df, team, player)