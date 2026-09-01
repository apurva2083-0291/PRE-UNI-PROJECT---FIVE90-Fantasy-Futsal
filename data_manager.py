from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).parent
CSV_PATH = BASE_DIR / "data" / "players.csv"

VALID_POSITIONS = {"GK", "DEF", "MID", "ATT"}
REQUIRED_COLUMNS = {
    "id",
    "name",
    "position",
    "overall",
    "pace",
    "shooting",
    "passing",
    "dribbling",
    "defending",
    "physical",
    "diving",
    "handling",
    "kicking",
    "reflexes",
    "speed",
    "positioning",
}

RATING_COLUMNS = REQUIRED_COLUMNS - {"id", "name", "position"}


def validate_players(players):
    """Return a list of readable data problems. An empty list means valid."""

    problems = []

    if not players:
        return ["The player CSV contains no players."]

    found_columns = set(players[0])
    missing_columns = sorted(REQUIRED_COLUMNS - found_columns)

    if missing_columns:
        problems.append(
            "Missing CSV columns: " + ", ".join(missing_columns)
        )
        return problems

    ids = [int(player["id"]) for player in players]
    names = [str(player["name"]).strip() for player in players]

    if len(ids) != len(set(ids)):
        problems.append("Every player ID must be unique.")

    lowered_names = [name.casefold() for name in names]
    if len(lowered_names) != len(set(lowered_names)):
        problems.append("Every player name must be unique.")

    for player in players:
        player_name = str(player["name"]).strip()
        position = str(player["position"]).upper()

        if not player_name:
            problems.append(f"Player ID {player['id']} has no name.")

        if position not in VALID_POSITIONS:
            problems.append(
                f"{player_name} has invalid position '{position}'."
            )

        for column in RATING_COLUMNS:
            try:
                value = int(player[column])
            except (TypeError, ValueError):
                problems.append(
                    f"{player_name}'s {column} rating is not a number."
                )
                continue

            if value < 0 or value > 100:
                problems.append(
                    f"{player_name}'s {column} rating must be 0-100."
                )

    position_counts = {
        position: sum(
            1
            for player in players
            if str(player["position"]).upper() == position
        )
        for position in VALID_POSITIONS
    }

    minimums = {"GK": 4, "DEF": 4, "MID": 4, "ATT": 4}
    for position, minimum in minimums.items():
        if position_counts[position] < minimum:
            problems.append(
                f"At least {minimum} {position} players are required."
            )

    return problems


def load_players(csv_path=CSV_PATH):
    """Load and validate the local player CSV as a list of dictionaries."""

    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"Player data was not found: {csv_path}")

    players = pd.read_csv(csv_path).to_dict("records")

    for player in players:
        player["id"] = int(player["id"])
        player["position"] = str(player["position"]).upper()

        for column in RATING_COLUMNS:
            player[column] = int(player[column])

    problems = validate_players(players)

    if problems:
        raise ValueError("\n".join(problems))

    return players


def get_players_by_position(position, players=None):
    """Return all players matching GK, DEF, MID, or ATT."""

    position = str(position).upper()

    if position not in VALID_POSITIONS:
        raise ValueError(f"Unknown player position: {position}")

    if players is None:
        players = load_players()

    return [
        player
        for player in players
        if player["position"] == position
    ]


def get_player_by_id(player_id, players=None):
    """Find one player using the numeric CSV ID."""

    if players is None:
        players = load_players()

    player_id = int(player_id)

    for player in players:
        if int(player["id"]) == player_id:
            return player

    return None


if __name__ == "__main__":
    loaded_players = load_players()
    print(f"Player data valid: {len(loaded_players)} players loaded.")

    for player_position in ["GK", "DEF", "MID", "ATT"]:
        count = len(
            get_players_by_position(player_position, loaded_players)
        )
        print(f"{player_position}: {count}")
