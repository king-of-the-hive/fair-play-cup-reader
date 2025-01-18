import yaml, csv
from hg_group_creator_helper import (
    login_to_hg,
    create_tournament,
    find_tournament_link,
    send_invites_to_players,
)

SETTINGS = "HFPC.yml"

with open(SETTINGS, 'r') as settings:
    tournament_params = yaml.safe_load(settings)

players = []
with open("hfpc_player_pairs.csv", "r", encoding="utf-8") as playerpairsfile:
    reader = csv.DictReader(playerpairsfile)
    for row in reader:
        player1 = row["player1"]
        player2 = row["player2"]
        players.append((player1, player2))

driver = login_to_hg()

for player_pair in players:
    pair_str = f"{player_pair[0]} v {player_pair[1]}" 
    groupname = create_tournament(driver, pair_str, **tournament_params)
    grouplink = find_tournament_link(driver, groupname)

    send_invites_to_players(driver, grouplink, player_pair, **tournament_params)

driver.close()
