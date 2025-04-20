import matplotlib.pyplot as plt
from nba_api.stats.static import players
from nba_api.stats.endpoints import shotchartdetail
import pandas as pd
import seaborn as sns

# Fonction pour récupérer l'ID du joueur
def get_player_id(player_name):
    player_dict = players.find_players_by_full_name(player_name)
    if player_dict:
        return player_dict[0]['id']
    else:
        raise Exception(f"Joueur {player_name} introuvable")

# Fonction pour récupérer les tirs
def get_shot_data(player_id, season='2023-24'):
    shots = shotchartdetail.ShotChartDetail(
        team_id=0,
        player_id=player_id,
        season_type_all_star='Regular Season',
        season_nullable=season,
        context_measure_simple='FGA'
    )
    shot_df = shots.get_data_frames()[0]
    return shot_df

# Fonction pour dessiner un demi-terrain NBA
def draw_court(ax=None, color='white', lw=2, outer_lines=False):
    if ax is None:
        ax = plt.gca()

    # Eléments du terrain
    hoop = plt.Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)
    backboard = plt.Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)
    paint = plt.Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color, fill=False)
    free_throw = plt.Circle((0, 142.5), 60, linewidth=lw, color=color, fill=False)
    restricted = plt.Circle((0, 0), 40, linewidth=lw, color=color, fill=False)
    three_arc = plt.Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw, color=color)
    corner_three_left = plt.Rectangle((-220, -47.5), 0, 140, linewidth=lw, color=color)
    corner_three_right = plt.Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)

    court_elements = [hoop, backboard, paint, free_throw, restricted,
                      three_arc, corner_three_left, corner_three_right]

    if outer_lines:
        outer = plt.Rectangle((-250, -47.5), 500, 470, linewidth=lw, color=color, fill=False)
        court_elements.append(outer)

    for element in court_elements:
        ax.add_patch(element)

    return ax

# 🔧 Main
player_name = "Stephen Curry"
player_id = get_player_id(player_name)
df_shots = get_shot_data(player_id)

# 🎯 Affichage
plt.figure(figsize=(12,11))
plt.style.use('dark_background')
ax = plt.gca()
draw_court(ax, outer_lines=True)
sns.scatterplot(data=df_shots, x='LOC_X', y='LOC_Y', hue='SHOT_MADE_FLAG', palette={1: 'green', 0: 'red'}, alpha=0.6)
plt.xlim(-250, 250)
plt.ylim(-47.5, 422.5)
plt.title(f'{player_name} Shot Chart - {df_shots["SEASON"][0]} Season')
plt.legend(title="Shot Made")
plt.axis('off')
plt.show()
