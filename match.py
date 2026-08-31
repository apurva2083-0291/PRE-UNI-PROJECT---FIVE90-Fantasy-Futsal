import random
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).parent
CSV_PATH = BASE_DIR / "data" / "players.csv"


def calculate_team_strength(team):
    """Calculate the average overall rating of a team."""

    if not team:
        return 0

    total_rating = 0

    for player in team:
        total_rating += int(player["overall"])

    return total_rating / len(team)


def choose_event_player(team):
    """Choose a midfielder or attacker for a match event."""

    attacking_players = [
        player
        for player in team
        if player["position"] in ["ATT", "MID"]
    ]

    if attacking_players:
        return random.choice(attacking_players)

    return random.choice(team)


def simulate_match(team_one, team_two):
    """Simulate a match and return both scores and the event list."""

    if len(team_one) != 5 or len(team_two) != 5:
        raise ValueError("Both teams must contain exactly 5 players.")

    strength_one = calculate_team_strength(team_one)
    strength_two = calculate_team_strength(team_two)

    score_one = 0
    score_two = 0
    events = []

    event_minutes = [8, 17, 29, 41, 55, 68, 79, 88]

    for minute in event_minutes:
        total_strength = strength_one + strength_two

        if total_strength == 0:
            team_one_chance = 0.5
        else:
            team_one_chance = strength_one / total_strength

        if random.random() < team_one_chance:
            attacking_team = 1
            selected_player = choose_event_player(team_one)
        else:
            attacking_team = 2
            selected_player = choose_event_player(team_two)

        is_goal = random.random() < 0.32

        if is_goal:
            if attacking_team == 1:
                score_one += 1
            else:
                score_two += 1

            event_type = "goal"
            event_text = f"GOAL! {selected_player['name']} scores!"
        else:
            event_type = "chance"
            event_text = f"{selected_player['name']} takes a shot!"

        events.append(
            {
                "minute": minute,
                "type": event_type,
                "team": attacking_team,
                "player": selected_player["name"],
                "text": event_text,
                "score_one": score_one,
                "score_two": score_two,
            }
        )

    return score_one, score_two, events


def create_test_teams():
    """Create two valid temporary teams for testing."""

    players = pd.read_csv(CSV_PATH).to_dict("records")

    goalkeepers = [
        player for player in players if player["position"] == "GK"
    ]
    defenders = [
        player for player in players if player["position"] == "DEF"
    ]
    midfielders = [
        player for player in players if player["position"] == "MID"
    ]
    attackers = [
        player for player in players if player["position"] == "ATT"
    ]

    team_one = [
        goalkeepers[0],
        defenders[0],
        midfielders[0],
        midfielders[1],
        attackers[0],
    ]

    team_two = [
        goalkeepers[1],
        defenders[1],
        midfielders[2],
        midfielders[3],
        attackers[1],
    ]

    return team_one, team_two


if __name__ == "__main__":
    test_team_one, test_team_two = create_test_teams()

    final_score_one, final_score_two, match_events = simulate_match(
        test_team_one,
        test_team_two,
    )

    print("MATCH EVENTS")
    print("-" * 40)

    for event in match_events:
        print(
            f"{event['minute']}' "
            f"{event['text']} "
            f"({event['score_one']}-{event['score_two']})"
        )

    print("-" * 40)
    print("FULL TIME")
    print(f"Team 1 {final_score_one} - {final_score_two} Team 2")
