import datetime
import mlbstatsapi
import statsapi
from datetime import datetime, timedelta
import pybaseball

mlb = mlbstatsapi.Mlb()

def convert_id_to_mlb_id(player_data):
  converted_data = {}
  for player_id, metrics in player_data.items():
    name_info = pybaseball.playerid_reverse_lookup(player_ids=[player_id], key_type='mlbam')
    if not name_info.empty:
      first_name = name_info['name_first'].iloc[0].capitalize()
      last_name = name_info['name_last'].iloc[0].capitalize()
      full_name = f"{first_name} {last_name}"
      converted_data[full_name] = metrics
  return converted_data

def get_last_n_gamepks_of_lineup(lineup_ids, last_n_days=10, from_date=None, last_n_pks=5):
  last_n_gamepks_dict = {player_id: [] for player_id in lineup_ids}

  try:
    if from_date is None:
      from_date = datetime.now().date()
    else:
      from_date = datetime.strptime(from_date, "%Y-%m-%d").date()

    start_date = from_date - timedelta(days=last_n_days)
    end_date = from_date - timedelta(days=1)

    games = statsapi.schedule(start_date=start_date.strftime("%Y-%m-%d"), end_date=end_date.strftime("%Y-%m-%d"))
    for game in games:
      game_pk = game['game_id']
      game_data = statsapi.get('game_playByPlay', {'gamePk': game_pk})

      for player_id in lineup_ids:
        player_participated = any(
          play['matchup']['batter']['id'] == player_id for play in game_data['allPlays']
                )
        if player_participated:
          last_n_gamepks_dict[player_id].append(game_pk)
          last_n_gamepks_dict[player_id] = last_n_gamepks_dict[player_id][-last_n_days:]

      for player_id, gamepks in last_n_gamepks_dict.items():
        last_n_gamepks_dict[player_id] = gamepks[-last_n_pks:]

  except Exception as e:
    print(f"Error in get_last_n_gamepks_of_lineup: {e}")

  return last_n_gamepks_dict

def remap_zone_for_pitchers_pov(data):
  # Define the mapping from catcher's zones to pitcher's zones
  zone_mapping = {
      1: 3, 2: 2, 3: 1, 4: 6, 5: 5, 6: 4, 7: 9, 8: 8, 9: 7, 11: 12, 12: 11, 13: 14, 14: 13
  }

  remapped_data = {}

  # Remap the data
  for batter_id, zone_data in data.items():
    remapped_zone_data = {zone_mapping[zone]: value for zone, value in zone_data.items()}
    remapped_data[batter_id] = remapped_zone_data

  return remapped_data

def remap_zone_number_to_coordinates(data):
  mapping = {
      1: (3, 3), 2: (5, 3), 3: (7, 3), 4: (3, 1), 5: (5, 1), 6: (7, 1), 7: (3, -1),
      8: (5, -1),9: (7, -1), 11: (1, 5), 12: (9, 5), 13: (1, -3), 14: (9, -3)
  }

  remapped_data = {}

  for batter_id, zone_data in data.items():
    remapped_zone_data = {mapping[zone]: value for zone, value in zone_data.items()}
    remapped_data[batter_id] = remapped_zone_data

  return remapped_data
