import random

from data_manager import load_players


REQUIRED_FORMATION = {"GK": 1, "DEF": 1, "MID": 2, "ATT": 1}

EVENT_MINUTES = [
    5, 11, 17, 23, 29, 35, 41, 45,
    50, 56, 62, 68, 74, 80, 86, 90,
]


def validate_team(team):
    """Return readable formation problems for one drafted team."""

    problems = []

    if len(team) != 5:
        problems.append("A team must contain exactly five players.")

    player_ids = [int(player["id"]) for player in team]
    if len(player_ids) != len(set(player_ids)):
        problems.append("A team cannot contain the same player twice.")

    for position, required_count in REQUIRED_FORMATION.items():
        actual_count = sum(
            1 for player in team if player["position"] == position
        )

        if actual_count != required_count:
            problems.append(
                f"A team needs {required_count} {position} player(s), "
                f"but has {actual_count}."
            )

    return problems


def calculate_team_metrics(team):
    """Calculate attack, passing, defence, goalkeeper, and overall values."""

    problems = validate_team(team)
    if problems:
        raise ValueError(" ".join(problems))

    outfield_players = [
        player for player in team if player["position"] != "GK"
    ]
    goalkeeper = next(
        player for player in team if player["position"] == "GK"
    )

    attack_values = [
        player["shooting"] * 0.35
        + player["pace"] * 0.20
        + player["dribbling"] * 0.20
        + player["passing"] * 0.25
        for player in outfield_players
    ]
    passing_values = [
        player["passing"] * 0.70
        + player["dribbling"] * 0.30
        for player in outfield_players
    ]
    defence_values = [
        player["defending"] * 0.55
        + player["physical"] * 0.25
        + player["pace"] * 0.20
        for player in outfield_players
    ]
    goalkeeper_value = (
        goalkeeper["diving"] * 0.24
        + goalkeeper["handling"] * 0.18
        + goalkeeper["kicking"] * 0.10
        + goalkeeper["reflexes"] * 0.28
        + goalkeeper["speed"] * 0.05
        + goalkeeper["positioning"] * 0.15
    )

    return {
        "attack": sum(attack_values) / len(attack_values),
        "passing": sum(passing_values) / len(passing_values),
        "defence": sum(defence_values) / len(defence_values),
        "goalkeeper": goalkeeper_value,
        "overall": sum(player["overall"] for player in team) / len(team),
    }


def calculate_team_strength(team):
    """Return one simple combined team-strength number."""

    metrics = calculate_team_metrics(team)
    return (
        metrics["attack"] * 0.32
        + metrics["passing"] * 0.18
        + metrics["defence"] * 0.25
        + metrics["goalkeeper"] * 0.15
        + metrics["overall"] * 0.10
    )


def _attacking_rating(player):
    return (
        player["shooting"] * 0.42
        + player["pace"] * 0.18
        + player["dribbling"] * 0.18
        + player["passing"] * 0.22
    )


def choose_event_player(team, rng=None):
    """Choose a likely attacker, weighting better attackers more highly."""

    rng = rng or random.Random()
    candidates = [
        player
        for player in team
        if player["position"] in {"ATT", "MID"}
    ]
    weights = [max(1, _attacking_rating(player)) for player in candidates]
    return rng.choices(candidates, weights=weights, k=1)[0]


def _goalkeeper(team):
    return next(player for player in team if player["position"] == "GK")


def _bounded(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def simulate_match(team_one, team_two, rng=None):
    """Generate a controlled ratings-based 90-minute event timeline."""

    rng = rng or random.Random()
    team_one_problems = validate_team(team_one)
    team_two_problems = validate_team(team_two)

    if team_one_problems or team_two_problems:
        raise ValueError(
            "Invalid team formation. "
            + " ".join(team_one_problems + team_two_problems)
        )

    teams = [team_one, team_two]
    metrics = [
        calculate_team_metrics(team_one),
        calculate_team_metrics(team_two),
    ]
    score = [0, 0]
    events = []

    team_one_control = (
        metrics[0]["attack"]
        + metrics[0]["passing"]
        + metrics[0]["overall"]
    )
    team_two_control = (
        metrics[1]["attack"]
        + metrics[1]["passing"]
        + metrics[1]["overall"]
    )
    team_one_attack_chance = _bounded(
        team_one_control / (team_one_control + team_two_control),
        0.35,
        0.65,
    )

    for minute in EVENT_MINUTES:
        attacking_team = (
            0 if rng.random() < team_one_attack_chance else 1
        )
        defending_team = 1 - attacking_team
        attacker = choose_event_player(teams[attacking_team], rng)
        goalkeeper = _goalkeeper(teams[defending_team])

        attacker_quality = _attacking_rating(attacker)
        defensive_quality = (
            metrics[defending_team]["defence"] * 0.45
            + metrics[defending_team]["goalkeeper"] * 0.55
        )
        goal_probability = _bounded(
            0.16 + (attacker_quality - defensive_quality) / 240,
            0.08,
            0.30,
        )
        outcome_roll = rng.random()

        if outcome_roll < goal_probability:
            score[attacking_team] += 1
            event_type = "goal"
            event_text = f"GOAL! {attacker['name']} scores!"
        elif outcome_roll < goal_probability + 0.22:
            event_type = "save"
            event_text = (
                f"{goalkeeper['name']} saves "
                f"{attacker['name']}'s shot!"
            )
        elif outcome_roll < goal_probability + 0.52:
            event_type = "shot"
            event_text = f"{attacker['name']} shoots wide."
        else:
            event_type = "pass"
            event_text = f"{attacker['name']} moves the ball forward."

        events.append(
            {
                "minute": minute,
                "type": event_type,
                "team": attacking_team + 1,
                "attacking_team": attacking_team + 1,
                "defending_team": defending_team + 1,
                "player": attacker["name"],
                "goalkeeper": goalkeeper["name"],
                "text": event_text,
                "score_one": score[0],
                "score_two": score[1],
            }
        )

    return score[0], score[1], events


def goal_events(events):
    """Return only the goals from an event timeline."""

    return [event for event in events if event["type"] == "goal"]


def create_test_teams():
    """Create two valid 1-1-2-1 teams for demonstrations and tests."""

    players = load_players()
    positions = {
        position: [
            player
            for player in players
            if player["position"] == position
        ]
        for position in REQUIRED_FORMATION
    }

    team_one = [
        positions["GK"][0],
        positions["DEF"][0],
        positions["MID"][0],
        positions["MID"][1],
        positions["ATT"][0],
    ]
    team_two = [
        positions["GK"][1],
        positions["DEF"][1],
        positions["MID"][2],
        positions["MID"][3],
        positions["ATT"][1],
    ]
    return team_one, team_two


if __name__ == "__main__":
    test_team_one, test_team_two = create_test_teams()
    score_one, score_two, match_events = simulate_match(
        test_team_one,
        test_team_two,
        random.Random(90),
    )

    print("MATCH EVENTS")
    print("-" * 60)
    for event in match_events:
        print(
            f"{event['minute']:>2}'  {event['text']}  "
            f"({event['score_one']}-{event['score_two']})"
        )
    print("-" * 60)
    print(f"FULL TIME: Team 1 {score_one} - {score_two} Team 2")
