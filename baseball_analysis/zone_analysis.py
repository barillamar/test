import mlbstatsapi
import pybaseball

mlb = mlbstatsapi.Mlb()

def fetch_gamepks(date=None):
    """
      Fetches gamepks for the specified date.
  
      Parameters:
      - date (str, optional): The date for which gamepks are to be fetched.
        Should be in the format 'YYYY-MM-DD'. If not provided, defaults to today's date.
  
      Returns:
      - list: List of gamepks scheduled for the specified date.
  
      Raises:
      - ValueError: If no gamepks are found for the specified date.
      """
  
    if date is None:
      date = datetime.date.today()
  
    gamepks = mlb.get_scheduled_games_by_date(date=date)
  
    if not gamepks:
      raise ValueError('No gamepks found for the specified date.')
  
    return gamepks

def get_batting_order_of_game(gamepk, team='away'):
    """
    Retrieve the batting order of a specified team in a baseball game.

    Parameters:
    - gamepk (int): The unique identifier for the game.
    - team (str): The team whose batting order you want to retrieve.
                  Should be either 'home' or 'away'. Default is 'away'.

    Returns:
    - list: A list representing the batting order of the specified team.
            Returns None if the retrieval fails.
    """
    try:
        game = statsapi.get('game', {'gamePk': gamepk})
        return game['liveData']['boxscore']['teams'][team]['battingOrder']
    except Exception as e:
        print(f"Error in get_batting_order_of_game: {e}")
        return None

def convert_names_to_mlb_ids(names=[]):
    """
    Convert a list of player names to their corresponding MLB IDs.

    Parameters:
    - names (list): A list of player names in the format 'First Last'.

    Returns:
    - list: A list of MLB IDs corresponding to the input player names.

    Example:
    >>> convert_names_to_mlb_ids(['Mike Trout', 'Shohei Ohtani'])
    ['545361', '660271']
    """
    ids = []

    for player in names:
        try:
            first, last = player.split(' ')
            look_player = pybaseball.playerid_lookup(str(last), str(first))
            mlbam_id = look_player['key_mlbam'].iloc[0]
            ids.append(mlbam_id)
        except Exception as e:
            print(f"Error in convert_names_to_mlb_ids for player {player}: {e}")

    return ids

def get_swing_and_miss_rate_by_zone(lineup_ids, last_n_days=10, from_date=None, last_n_pks=5):
    """
    Calculate and visualize the swing-and-miss rate for each zone of a baseball strike zone for a given lineup of players.

    Parameters:
    - lineup_ids (list): A list of MLB player IDs representing the lineup.
    - last_n_days (int): Number of days back from 'from_date' param to consider for games. Default is 10 days.
    - from_date (str): Optional. Start date in 'YYYY-MM-DD' format. If not provided, defaults to today's date.
    - last_n_pks (int): Number of recent games to consider for each player. Default is 5 games.

    Returns:
    - Matplotlib plot: A visualization of the strike zone, where each part of the strike zone contains the calculated
      swing-and-miss rate for the corresponding zone.

    """
    player_games = get_last_n_gamepks_of_lineup(lineup_ids, last_n_days, from_date, last_n_pks)
    all_swing_and_miss_rates = {}

    for player_id, games in player_games.items():
        player_zone_counts = {1: {'swings': 0, 'misses': 0},
                              2: {'swings': 0, 'misses': 0},
                              3: {'swings': 0, 'misses': 0},
                              4: {'swings': 0, 'misses': 0},
                              5: {'swings': 0, 'misses': 0},
                              6: {'swings': 0, 'misses': 0},
                              7: {'swings': 0, 'misses': 0},
                              8: {'swings': 0, 'misses': 0},
                              9: {'swings': 0, 'misses': 0},
                              11: {'swings': 0, 'misses': 0},
                              12: {'swings': 0, 'misses': 0},
                              13: {'swings': 0, 'misses': 0},
                              14: {'swings': 0, 'misses': 0}}

        for gamepk in games:
            try:
                game_data = statsapi.get('game_playByPlay', {'gamePk': gamepk})
            except Exception as e:
                print(f"Error fetching data for game {gamepk}: {str(e)}")
                continue

            if 'allPlays' not in game_data:
                print(f"No play data found for game {gamepk}")
                continue

            for play in game_data['allPlays']:
                if 'playEvents' not in play:
                    print(f"No play events found for play in game {gamepk}")
                    continue
                for event in play['playEvents']:
                    if event.get('isPitch') and play['matchup']['batter']['id'] == player_id:
                        zone = event['pitchData']['zone']

                        # Check if it's a swing
                        if 'details' in event and 'call' in event['details'] and 'description' in event['details']['call']:
                            if event['details']['call']['description'] in ['Swinging Strike', 'Swinging Strike (Blocked)', "In play, out(s)",
                                                                            'Foul Tip', 'In play, run(s)', 'In play, no out', 'Foul']:
                                player_zone_counts[zone]['swings'] += 1

                                # Check if it's a miss
                                if event['details']['description'] in ['Swinging Strike', 'Swinging Strike (Blocked)']:
                                    player_zone_counts[zone]['misses'] += 1

        # Calculate swing-and-miss rate for each zone for this player
        player_swing_and_miss_rates = {}
        for zone, counts in player_zone_counts.items():
            if counts['swings'] > 0:
                player_swing_and_miss_rates[zone] = round(counts['misses'] / counts['swings'], 3)
            else:
                player_swing_and_miss_rates[zone] = 0.0  # No swings in this zone

        all_swing_and_miss_rates[player_id] = player_swing_and_miss_rates
        remapped_swing_and_miss_rate = remap_zone_for_pitchers_pov(all_swing_and_miss_rates)
        remap_to_coor = remap_zone_number_to_coordinates(remapped_swing_and_miss_rate)

    return visualize_strike_zone(remap_to_coor)

def get_called_strike_rate_by_zone(lineup_ids, last_n_days=10, from_date=None, last_n_pks=5):
    """
    Calculate and visualize the called strike rate for each zone of a baseball strike zone for a given lineup of players.

    Parameters:
    - lineup_ids (list): A list of MLB player IDs representing the lineup.
    - last_n_days (int): Number of days back from 'from_date' param to consider for games. Default is 10 days.
    - from_date (str): Optional. Start date in 'YYYY-MM-DD' format. If not provided, defaults to today's date.
    - last_n_pks (int): Number of recent games to consider for each player. Default is 5 games.

    Returns:
    - Matplotlib plot: A visualization of the strike zone, where each part of the strike zone contains the calculated
      called strike rate for the corresponding zone.

    """
    player_games = get_last_n_gamepks_of_lineup(lineup_ids, last_n_days, from_date, last_n_pks)
    all_called_strike_rates = {}

    for player_id, games in player_games.items():
        player_zone_counts = {1: {'called_strikes': 0, 'total_pitches': 0},
                              2: {'called_strikes': 0, 'total_pitches': 0},
                              3: {'called_strikes': 0, 'total_pitches': 0},
                              4: {'called_strikes': 0, 'total_pitches': 0},
                              5: {'called_strikes': 0, 'total_pitches': 0},
                              6: {'called_strikes': 0, 'total_pitches': 0},
                              7: {'called_strikes': 0, 'total_pitches': 0},
                              8: {'called_strikes': 0, 'total_pitches': 0},
                              9: {'called_strikes': 0, 'total_pitches': 0}}

        for gamepk in games:
            try:
                game_data = statsapi.get('game_playByPlay', {'gamePk': gamepk})
            except Exception as e:
                print(f"Error fetching data for game {gamepk}: {str(e)}")
                continue

            if 'allPlays' not in game_data:
                print(f"No play data found for game {gamepk}")
                continue

            for play in game_data['allPlays']:
                if 'playEvents' not in play:
                    print(f"No play events found for play in game {gamepk}")
                    continue
                for event in play['playEvents']:
                    if event.get('isPitch') and play['matchup']['batter']['id'] == player_id:
                        zone = event['pitchData']['zone']

                        # Exclude zones 11, 12, 13, and 14
                        if zone not in [11, 12, 13, 14]:
                            if 'details' in event and 'description' in event['details']:
                                # Check if the pitch was called a strike
                                if event['details']['description'] == 'Called Strike':
                                    player_zone_counts[zone]['called_strikes'] += 1

                            # Count the total number of pitches in the zone
                            player_zone_counts[zone]['total_pitches'] += 1

        # Calculate called strike rate for each zone for this player
        player_called_strike_rates = {}
        for zone, counts in player_zone_counts.items():
            if counts['total_pitches'] > 0:
                player_called_strike_rates[zone] = round(counts['called_strikes'] / counts['total_pitches'], 3)
            else:
                player_called_strike_rates[zone] = 0.0

        all_called_strike_rates[player_id] = player_called_strike_rates
        remapped_called_strike_rates = remap_zone_for_pitchers_pov(all_called_strike_rates)
        remap_to_coor = remap_zone_number_to_coordinates(remapped_called_strike_rates)

    return visualize_strike_zone(remap_to_coor)

def get_slugging_percentage_by_zone(lineup_ids, last_n_days=10, from_date=None, last_n_pks=5):
    """
    Calculate and visualize the slugging percentage for each zone of a baseball strike zone for a given lineup of players.

    Parameters:
    - lineup_ids (list): A list of MLB player IDs representing the lineup.
    - last_n_days (int): Number of days back from 'from_date' param to consider for games. Default is 10 days.
    - from_date (str): Optional. Start date in 'YYYY-MM-DD' format. If not provided, defaults to today's date.
    - last_n_pks (int): Number of recent games to consider for each player. Default is 5 games.

    Returns:
    - Matplotlib plot: A visualization of the strike zone, where each part of the strike zone contains the calculated
      slugging percentage for the corresponding zone.

    """
    player_games = get_last_n_gamepks_of_lineup(lineup_ids, last_n_days, from_date, last_n_pks)
    all_slugging_percentages = {}

    for player_id, games in player_games.items():
        player_zone_counts = {1: {'total_bases': 0, 'at_bats': 0},
                              2: {'total_bases': 0, 'at_bats': 0},
                              3: {'total_bases': 0, 'at_bats': 0},
                              4: {'total_bases': 0, 'at_bats': 0},
                              5: {'total_bases': 0, 'at_bats': 0},
                              6: {'total_bases': 0, 'at_bats': 0},
                              7: {'total_bases': 0, 'at_bats': 0},
                              8: {'total_bases': 0, 'at_bats': 0},
                              9: {'total_bases': 0, 'at_bats': 0},
                              11: {'total_bases': 0, 'at_bats': 0},
                              12: {'total_bases': 0, 'at_bats': 0},
                              13: {'total_bases': 0, 'at_bats': 0},
                              14: {'total_bases': 0, 'at_bats': 0}}

        for gamepk in games:
            try:
                data = statsapi.get('game_playByPlay', {'gamePk': gamepk})
            except Exception as e:
                print(f"Error fetching data for game {gamepk}: {str(e)}")
                continue

            if 'allPlays' not in data:
                print(f"No play data found for game {gamepk}")
                continue

            for play in data['allPlays']:
                for event in play['playEvents']:
                    if event['isPitch'] and play['matchup']['batter']['id'] == player_id:
                        zone = event['pitchData']['zone']

                        if zone:
                            # Calculate at bats in each zone
                            if play['result']['type'] == 'atBat':
                                player_zone_counts[zone]['at_bats'] += 1

                                # Calculate the value of different hits (Single, Double...)
                                if 'In play, no out' in event['details']['description'] or 'In play, run(s)' in event['details']['description']:
                                    if play['result']['event'] == 'Single':
                                        player_zone_counts[zone]['total_bases'] += 1
                                    elif play['result']['event'] == 'Double':
                                        player_zone_counts[zone]['total_bases'] += 2
                                    elif play['result']['event'] == 'Triple':
                                        player_zone_counts[zone]['total_bases'] += 3
                                    elif play['result']['event'] == 'Home Run':
                                        player_zone_counts[zone]['total_bases'] += 4

        # Calculate slugging percentage for each zone for this player
        player_slugging_percentages = {}
        for zone, count in player_zone_counts.items():
            if count['at_bats'] > 0:
                player_slugging_percentages[zone] = round(count['total_bases'] / count['at_bats'], 3)
            else:
                player_slugging_percentages[zone] = 0.0

        all_slugging_percentages[player_id] = player_slugging_percentages
        remapped_slg = remap_zone_for_pitchers_pov(all_slugging_percentages)
        remap_to_coor = remap_zone_number_to_coordinates(remapped_slg)

    return visualize_strike_zone(remap_to_coor)

def get_on_base_percentage_by_zone(lineup_ids, last_n_days=10, from_date=None, last_n_pks=5):
    """
    Calculate and visualize the on-base percentage for each zone of a baseball strike zone for a given lineup of players.

    Parameters:
    - lineup_ids (list): A list of MLB player IDs representing the lineup.
    - last_n_days (int): Number of days back from 'from_date' param to consider for games. Default is 10 days.
    - from_date (str): Optional. Start date in 'YYYY-MM-DD' format. If not provided, defaults to today's date.
    - last_n_pks (int): Number of recent games to consider for each player. Default is 5 games.

    Returns:
    - Matplotlib plot: A visualization of the strike zone, where each part of the strike zone contains the calculated
      on base percentage for the corresponding zone.

    """
    player_games = get_last_n_gamepks_of_lineup(lineup_ids, last_n_days, from_date, last_n_pks)
    all_obp_percentages = {}

    for player_id, games in player_games.items():
        player_zone_counts = {1: {'at_bats': 0, 'hits': 0, 'walks': 0, 'hbp': 0, 'sf': 0},
                              2: {'at_bats': 0, 'hits': 0, 'walks': 0, 'hbp': 0, 'sf': 0},
                              3: {'at_bats': 0, 'hits': 0, 'walks': 0, 'hbp': 0, 'sf': 0},
                              4: {'at_bats': 0, 'hits': 0, 'walks': 0, 'hbp': 0, 'sf': 0},
                              5: {'at_bats': 0, 'hits': 0, 'walks': 0, 'hbp': 0, 'sf': 0},
                              6: {'at_bats': 0, 'hits': 0, 'walks': 0, 'hbp': 0, 'sf': 0},
                              7: {'at_bats': 0, 'hits': 0, 'walks': 0, 'hbp': 0, 'sf': 0},
                              8: {'at_bats': 0, 'hits': 0, 'walks': 0, 'hbp': 0, 'sf': 0},
                              9: {'at_bats': 0, 'hits': 0, 'walks': 0, 'hbp': 0, 'sf': 0},
                              11: {'at_bats': 0, 'hits': 0, 'walks': 0, 'hbp': 0, 'sf': 0},
                              12: {'at_bats': 0, 'hits': 0, 'walks': 0, 'hbp': 0, 'sf': 0},
                              13: {'at_bats': 0, 'hits': 0, 'walks': 0, 'hbp': 0, 'sf': 0},
                              14: {'at_bats': 0, 'hits': 0, 'walks': 0, 'hbp': 0, 'sf': 0}}

        for gamepk in games:
            try:
                data = statsapi.get('game_playByPlay', {'gamePk': gamepk})
            except Exception as e:
                print(f"Error fetching data for game {gamepk}: {str(e)}")
                continue

            if 'allPlays' not in data:
                print(f"No play data found for game {gamepk}")
                continue

            for play in data['allPlays']:
                for event in play['playEvents']:
                    if event['isPitch'] and play['matchup']['batter']['id'] == player_id:
                        zone = event['pitchData']['zone']

                        if zone:
                            # At bats for each zone
                            if play['result']['type'] == 'atBat':
                                player_zone_counts[zone]['at_bats'] += 1

                            # Hits
                            if event['details']['isInPlay'] and not event['details']['isOut']:
                                player_zone_counts[zone]['hits'] += 1

                            # Walks
                            if event['details']['description'] == 'Ball' and event['count']['balls'] == 4:
                                player_zone_counts[zone]['walks'] += 1

                            # Hit by pitch
                            if event['details']['call']['description'] == 'Hit By Pitch':
                                player_zone_counts[zone]['hbp'] += 1

                            # Sacrifice fly
                            if play['result']['event'] == 'Flyout' and 'runner' in event['details']:
                                if event['result']['rbi'] > 0:
                                    player_zone_counts[zone]['sf'] += 1

        # Calculate on-base percentage for each zone for this player
        player_obp_percentages = {}
        for zone, count in player_zone_counts.items():
            denominator = count['at_bats'] + count['walks'] + count['hbp'] + count['sf']
            if denominator != 0:
                player_obp_percentages[zone] = round((count['hits'] + count['walks'] + count['hbp']) / denominator, 3)
            else:
                player_obp_percentages[zone] = 0.0

        all_obp_percentages[player_id] = player_obp_percentages
        remapped_obp = remap_zone_for_pitchers_pov(all_obp_percentages)
        remap_to_coor = remap_zone_number_to_coordinates(remapped_obp)

    return visualize_strike_zone(remap_to_coor)

def get_batting_average_by_zone(lineup_ids, last_n_days=10, from_date=None, last_n_pks=5):
    """
    Calculate and visualize the batting average for each zone of a baseball strike zone for a given lineup of players.

    Parameters:
    - lineup_ids (list): A list of MLB player IDs representing the lineup.
    - last_n_days (int): Number of days back from 'from_date' param to consider for games. Default is 10 days.
    - from_date (str): Optional. Start date in 'YYYY-MM-DD' format. If not provided, defaults to today's date.
    - last_n_pks (int): Number of recent games to consider for each player. Default is 5 games.

    Returns:
    - Matplotlib plot: A visualization of the strike zone, where each part of the strike zone contains the calculated
      batting average for the corresponding zone.

    """
    player_games = get_last_n_gamepks_of_lineup(lineup_ids, last_n_days, from_date, last_n_pks)
    all_ba_averages = {}

    for player_id, games in player_games.items():
        player_zone_counts = {1: {'at_bats': 0, 'hits': 0},
                              2: {'at_bats': 0, 'hits': 0},
                              3: {'at_bats': 0, 'hits': 0},
                              4: {'at_bats': 0, 'hits': 0},
                              5: {'at_bats': 0, 'hits': 0},
                              6: {'at_bats': 0, 'hits': 0},
                              7: {'at_bats': 0, 'hits': 0},
                              8: {'at_bats': 0, 'hits': 0},
                              9: {'at_bats': 0, 'hits': 0},
                              11: {'at_bats': 0, 'hits': 0},
                              12: {'at_bats': 0, 'hits': 0},
                              13: {'at_bats': 0, 'hits': 0},
                              14: {'at_bats': 0, 'hits': 0}}

        for gamepk in games:
            try:
                data = statsapi.get('game_playByPlay', {'gamePk': gamepk})
            except Exception as e:
                print(f"Error fetching data for game {gamepk}: {str(e)}")
                continue

            if 'allPlays' not in data:
                print(f"No play data found for game {gamepk}")
                continue

            for play in data['allPlays']:
                if 'playEvents' not in play:
                    print(f"No play events found for play in game {gamepk}")
                    continue
                for event in play['playEvents']:
                    if event['isPitch'] and play['matchup']['batter']['id'] == player_id:
                        zone = event['pitchData']['zone']

                        if zone:
                            # At bats for each zone
                            if play['result']['type'] == 'atBat':
                                player_zone_counts[zone]['at_bats'] += 1

                            # Hits
                            if event['details']['isInPlay'] and not event['details']['isOut']:
                                player_zone_counts[zone]['hits'] += 1

        # Calculate batting average for each zone for this player
        player_ba_averages = {}
        for zone, count in player_zone_counts.items():
            denominator = count['at_bats']
            try:
                if denominator != 0:
                    player_ba_averages[zone] = round(count['hits'] / denominator, 3)

            except ZeroDivisionError:
                player_ba_averages[zone] = 0.0

        all_ba_averages[player_id] = player_ba_averages
        remapped_ba = remap_zone_for_pitchers_pov(all_ba_averages)
        remap_to_coor = remap_zone_number_to_coordinates(remapped_ba)

    return visualize_strike_zone(remap_to_coor)
