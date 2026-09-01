import argparse
import random

from card_generator import generate_team_cards
from data_manager import load_players
from draft import create_automatic_test_draft, start_draft
from match import calculate_team_strength, goal_events, simulate_match
from pitch import show_match
from result_screen import result_text, show_result


def print_team(player_name, team):
    """Print one drafted team in a clear presentation-friendly format."""

    print()
    print(f"{player_name.upper()}'S TEAM")
    print("-" * 45)

    for player in team:
        print(
            f"{player['position']:<3}  "
            f"{player['name']:<22}  "
            f"OVR {player['overall']}"
        )

    print(f"Team strength: {calculate_team_strength(team):.1f}")


def print_match_summary(
    player_one_name,
    player_two_name,
    score_one,
    score_two,
    events,
):
    print()
    print("MATCH EVENTS")
    print("-" * 64)

    for event in events:
        print(
            f"{event['minute']:>2}'  {event['text']}  "
            f"({event['score_one']}-{event['score_two']})"
        )

    print("-" * 64)
    print("FULL TIME")
    print(
        result_text(
            player_one_name,
            player_two_name,
            score_one,
            score_two,
        )
    )
    print(
        f"{player_one_name} {score_one} - {score_two} "
        f"{player_two_name}"
    )

    goals = goal_events(events)
    if goals:
        print("Goals:")
        for event in goals:
            print(f"  {event['player']} {event['minute']}'")
    else:
        print("No goals were scored.")


def play_one_match(
    player_one_name,
    player_two_name,
    team_one,
    team_two,
    use_gui=True,
    rng=None,
    wait_for_replay=True,
):
    """Generate cards, simulate one match, replay it, and show the result."""

    print("Generating the ten selected player cards...")
    generate_team_cards(team_one)
    generate_team_cards(team_two)

    print_team(player_one_name, team_one)
    print_team(player_two_name, team_two)

    print()
    print("Simulating the virtual 90-minute match...")
    score_one, score_two, events = simulate_match(
        team_one,
        team_two,
        rng,
    )

    print_match_summary(
        player_one_name,
        player_two_name,
        score_one,
        score_two,
        events,
    )

    print()
    print("Opening the animated Plotly replay...")
    show_match(
        team_one,
        team_two,
        events,
        player_one_name,
        player_two_name,
    )

    if wait_for_replay:
        try:
            input(
                "Watch the replay, then return here and press Enter "
                "for the full-time screen..."
            )
        except EOFError:
            pass

    return show_result(
        player_one_name,
        player_two_name,
        score_one,
        score_two,
        events,
        use_gui=use_gui,
    )


def run_game(use_gui=True, demo=False, seed=None, wait_for_replay=True):
    """Run drafts and matches until the users choose Exit."""

    print("=" * 64)
    print("FIVE90 — THE 5-A-SIDE FANTASY DRAFT GAME")
    print("DRAFT FIVE. PLAY NINETY.")
    print("=" * 64)

    players = load_players()
    print(f"Player database ready: {len(players)} validated players.")

    rng = random.Random(seed) if seed is not None else random.Random()

    while True:
        if demo:
            session = create_automatic_test_draft(seed or 90)
            player_one_name = "Player 1"
            player_two_name = "Player 2"
            team_one, team_two = session.teams
        else:
            draft_result = start_draft(
                use_gui=use_gui,
                players=players,
                rng=rng,
            )

            if draft_result is None:
                print("Draft closed. Thanks for playing FIVE90!")
                return

            (
                player_one_name,
                player_two_name,
                team_one,
                team_two,
            ) = draft_result

        while True:
            action = play_one_match(
                player_one_name,
                player_two_name,
                team_one,
                team_two,
                use_gui=use_gui,
                rng=rng,
                wait_for_replay=wait_for_replay,
            )

            if action == "rematch":
                continue

            if action == "new_draft":
                demo = False
                break

            print("Thanks for playing FIVE90!")
            return


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="FIVE90 fantasy futsal draft and match simulator"
    )
    parser.add_argument(
        "--console",
        action="store_true",
        help="Use terminal name entry and drafting instead of Tkinter.",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Skip the manual draft and create two automatic test teams.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Use repeatable draft and match randomness for testing.",
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Do not wait for Enter after opening the Plotly replay.",
    )
    return parser.parse_args()


def main():
    arguments = parse_arguments()
    run_game(
        use_gui=not arguments.console,
        demo=arguments.demo,
        seed=arguments.seed,
        wait_for_replay=not arguments.no_wait,
    )


if __name__ == "__main__":
    main()
