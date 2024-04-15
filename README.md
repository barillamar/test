# Baseball Analysis Python Package

This Python package provides functionalities to analyze baseball player metrics such as called strike rate, swing and miss rate, slugging percentage, on-base percentage, and batting average in each part of the strike zone for players in a lineup. Additionally, it offers tools to visualize strike zone data.

## Installation

You can install the package via pip directly from GitHub:

```bash
pip install git+https://github.com/barillamar/baseball-analysis.git
```

## Usage

Import the package and its modules:

```python
import baseball_analysis
from baseball_analysis import fetch_gamepks
from baseball_analysis import get_batting_order_of_game
from baseball_analysis import convert_names_to_mlb_ids
from baseball_analysis import get_swing_and_miss_rate_by_zone
from baseball_analysis import get_called_strike_rate_by_zone
from baseball_analysis import get_slugging_percentage_by_zone
from baseball_analysis import get_on_base_percentage_by_zone
from baseball_analysis import get_batting_average_by_zone
```

### Fetching Game Information

You can fetch game information by date using `fetch_gamepks`:

```python
games = fetch_gamepks('2023-06-16')
print(games)
```

This will return a list of `ScheduleGames` objects with game details.

### Getting Batting Order of a Game

Retrieve the batting order of a game using `get_batting_order_of_game`:

```python
batting_order = get_batting_order_of_game(717736)
print(batting_order)
```

This will return a list of player IDs representing the batting order.

### Converting Names to MLB IDs

Convert player names to MLB IDs using `convert_names_to_mlb_ids`:

```python
lineup = ['Mickey Moniak', 'Shohei Ohtani', 'Mike Trout', 'Brandon Drury', 'Matt Thaiss',
             'Hunter Renfroe', 'Jared Walsh', 'Luis Rengifo', 'Andrew Velazquez']

mlb_ids = convert_names_to_mlb_ids(lineup)
print(mlb_ids)
```

This will return a list of MLB IDs corresponding to the input player names.

### Analyzing Player Metrics by Zone

You can analyze various player metrics by zone, such as swing and miss rate, called strike rate, slugging percentage, on-base percentage, and batting average, using respective functions like `get_swing_and_miss_rate_by_zone`, `get_called_strike_rate_by_zone`, `get_slugging_percentage_by_zone`, `get_on_base_percentage_by_zone`, and `get_batting_average_by_zone`.

For example:

```python
swing_miss_rate = get_swing_and_miss_rate_by_zone(batting_order, last_n_days=20, from_date='2023-06-16')
print(swing_miss_rate)
```

This will return swing and miss rates by zone for the specified batting order.

### Visualizing Strike Zone

You can visualize strike zone data using appropriate plotting libraries such as Matplotlib or Seaborn. Here's an example of how you can visualize strike zone data:

*(Provide example code for visualization here)*

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, feel free to open an issue or submit a pull request on [GitHub](https://github.com/barillamar/baseball-analysis).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

