import matplotlib.pyplot as plt
from .data_fetch import convert_id_to_mlb_id

def visualize_strike_zone(player_data):
  converted_player_data = convert_id_to_mlb_id(player_data)
  for batter, metrics in converted_player_data.items():

    # Define strike zone dimensions
    strike_zone = {
        'x': [2, 6, 8, 8, 4, 2, 2],
        'y': [4, 4, 4, -2, -2, -2, 4]
    }

    # Define areas outside the strike zone
    outside_zone = {
        'x': [0, 6, 10, 10, 0, 0],
        'y': [6, 6, 6, -4, -4, 6]
    }

    # Plot the strike zone
    plt.plot(strike_zone['x'], strike_zone['y'], 'k-')
    for zone, metric in metrics.items():
        plt.text(zone[0], zone[1], str(metric), ha='center')

    # Plot the areas outside the strike zone
    plt.plot(outside_zone['x'], outside_zone['y'], 'k-')

    # inside lines
    # vertical lines
    x1_v = [4, 4]
    y1_v = [4, -2]

    x2_v = [6, 6]
    y2_v = [4, -2]

    # horizontal lines
    x1_h = [2, 8]
    y1_h = [2, 2]

    x2_h = [2, 8]
    y2_h = [0, 0]

    # outside lines
    x1_o = [5, 5]
    y1_o = [6, 4]

    x2_o = [5, 5]
    y2_o = [-2, -4]

    x3_o = [0, 2]
    y3_o = [1, 1]

    x4_o = [8, 10]
    y4_o = [1, 1]

    plt.plot(x1_v, y1_v, 'k-')
    plt.plot(x2_v, y2_v, 'k-')
    plt.plot(x1_h, y1_h, 'k-')
    plt.plot(x2_h, y2_h, 'k-')

    plt.plot(x1_o, y1_o, 'k-')
    plt.plot(x2_o, y2_o, 'k-')
    plt.plot(x3_o, y3_o, 'k-')
    plt.plot(x4_o, y4_o, 'k-')

    # Define coordinates for each part of the strike zone
    zone_coordinates = {
        (3, 3): [(2, 4), (4, 4), (4, 2), (2, 2)],
        (5, 3): [(4, 4), (6, 4), (6, 2), (4, 2)],
        (7, 3): [(6, 4), (8, 4), (8, 2), (6, 2)],
        (3, 1): [(2, 2), (4, 2), (4, 0), (2, 0)],
        (5, 1): [(4, 2), (6, 2), (6, 0), (4, 0)],
        (7, 1): [(6, 2), (8, 2), (8, 0), (6, 0)],
        (3, -1): [(2, 0), (4, 0), (4, -2), (2, -2)],
        (5, -1): [(4, 0), (6, 0), (6, -2), (4, -2)],
        (7, -1): [(6, 0), (8, 0), (8, -2), (6, -2)],
        (1, 5): [(0, 6), (5, 6), (5, 4), (2, 4), (2, 1), (0, 1)],
        (9, 5): [(5, 6), (10, 6), (10, 1), (8, 1), (8, 4), (5, 4)],
        (1, -3): [(0, 1), (2, 1), (2, -2), (5, -2), (5, -4), (0, -4)],
        (9, -3): [(8, 1), (10, 1), (10, -4), (5, -4), (5, -2), (8, -2)]
    }

    # Fill color of the zones
    for zone, coordinates in zone_coordinates.items():
        metric = metrics.get(zone, None)
        if metric is not None:

            if metric <= 0.0:
              color = 'grey'
              alpha = 0.3
            elif metric > 0.25:
              color = 'red'
              alpha = 0.3
            else:
              color = 'blue'
              alpha = 0.3
            plt.fill([x[0] for x in coordinates], [y[1] for y in coordinates], color=color, alpha=alpha)

    # Set plot limits and labels
    plt.title(f'{batter}', ha='center')

    # Show the plot
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()
