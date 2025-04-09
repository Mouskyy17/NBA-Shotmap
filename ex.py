import streamlit as st
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
    zip_ref.extract('all_shots_df_2024-2025.csv', path='.')

# Charger les données
df = pd.read_csv("all_shots_df_2024-2025.csv")

# Convertir les coordonnées en pieds
df["LOC_X"] = df["LOC_X"] / 12
df["LOC_Y"] = df["LOC_Y"] / 12

# Ajuster l'axe Y pour correspondre à la vue verticale
df["LOC_X"] = -df["LOC_X"] * 1.2
df["LOC_Y"] = -df["LOC_Y"] + 39

# Sélection de l'équipe et du joueur
team = st.selectbox("Select a team", df["TEAM_NAME"].unique())
player = st.selectbox("Select a player", df[df["TEAM_NAME"] == team]["PLAYER_NAME"].unique())

def plot_shot_chart(df, player):
    df = df[df["PLAYER_NAME"] == player]

    # Style du terrain : fond noir, lignes blanches
    plt.style.use("dark_background")

    # Création du terrain
    court = Court(court_type="nba", origin="center", units="ft", line_color="white")
    fig, ax = court.draw(orientation="vu")

    # Création de la heatmap avec hexbin
    hb = ax.hexbin(
        df["LOC_X"], df["LOC_Y"],
        gridsize=25,  # Densité similaire à l'image
        cmap="viridis",  # Bleu -> Vert -> Jaune
        mincnt=1,  # Ne pas afficher les hexagones vides
        edgecolors="none",  # Pas de contour pour un effet lisse
    )

    # Ajout de la barre de couleur
    cbar = plt.colorbar(hb, ax=ax, orientation="horizontal", pad=0.05)
    cbar.set_label("FG% vs. League Avg", color="white")
    cbar.ax.xaxis.set_tick_params(color="white")
    plt.setp(plt.getp(cbar.ax.axes, "xticklabels"), color="white")

    # Ajustements pour ressembler à l'image
    ax.set_xticks([])  # Supprime les ticks X
    ax.set_yticks([])  # Supprime les ticks Y
    ax.set_frame_on(False)  # Enlève le cadre

    # Titre personnalisé
    plt.title(f"{player}\n{team}", fontsize=20, color="white", fontweight="bold")

    st.pyplot(fig)

# Afficher la shot chart
if player:
    plot_shot_chart(df, player)
