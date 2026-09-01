import random
import unittest

from data_manager import (
    get_player_by_id,
    get_players_by_position,
    load_players,
    validate_players,
)
from draft import (
    DRAFT_POSITIONS,
    create_automatic_test_draft,
    create_balanced_first_picker_order,
)
from match import (
    REQUIRED_FORMATION,
    calculate_team_strength,
    goal_events,
    simulate_match,
    validate_team,
)
from result_screen import result_text


class PlayerDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.players = load_players()

    def test_player_file_is_valid(self):
        self.assertEqual(validate_players(self.players), [])
        self.assertEqual(len(self.players), 27)

    def test_required_position_counts(self):
        expected = {"GK": 4, "DEF": 5, "MID": 10, "ATT": 8}
        actual = {
            position: len(
                get_players_by_position(position, self.players)
            )
            for position in expected
        }
        self.assertEqual(actual, expected)

    def test_player_can_be_found_by_id(self):
        player = get_player_by_id(1, self.players)
        self.assertIsNotNone(player)
        self.assertEqual(player["name"], "Thibaut Courtois")


class DraftTests(unittest.TestCase):
    def test_draft_position_order(self):
        self.assertEqual(DRAFT_POSITIONS, ["GK", "DEF", "MID", "MID", "ATT"])

    def test_first_picker_order_is_balanced(self):
        order = create_balanced_first_picker_order(random.Random(90))
        counts = [order.count(0), order.count(1)]
        self.assertEqual(sorted(counts), [2, 3])

    def test_automatic_draft_creates_valid_unique_teams(self):
        session = create_automatic_test_draft(90)
        all_ids = [
            player["id"]
            for team in session.teams
            for player in team
        ]

        self.assertEqual(len(all_ids), 10)
        self.assertEqual(len(set(all_ids)), 10)

        for team in session.teams:
            self.assertEqual(validate_team(team), [])
            counts = {
                position: sum(
                    player["position"] == position
                    for player in team
                )
                for position in REQUIRED_FORMATION
            }
            self.assertEqual(counts, REQUIRED_FORMATION)


class MatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = create_automatic_test_draft(90)

    def test_team_strength_is_reasonable(self):
        for team in self.session.teams:
            strength = calculate_team_strength(team)
            self.assertGreaterEqual(strength, 0)
            self.assertLessEqual(strength, 100)

    def test_match_has_full_timeline_and_correct_score(self):
        score_one, score_two, events = simulate_match(
            self.session.teams[0],
            self.session.teams[1],
            random.Random(90),
        )

        self.assertEqual(len(events), 16)
        self.assertEqual(events[-1]["minute"], 90)
        self.assertEqual(events[-1]["score_one"], score_one)
        self.assertEqual(events[-1]["score_two"], score_two)

        goals = goal_events(events)
        team_one_goals = sum(event["team"] == 1 for event in goals)
        team_two_goals = sum(event["team"] == 2 for event in goals)

        self.assertEqual(team_one_goals, score_one)
        self.assertEqual(team_two_goals, score_two)
        self.assertTrue(
            all(
                event["type"] in {"pass", "shot", "save", "goal"}
                for event in events
            )
        )

    def test_result_text(self):
        self.assertEqual(result_text("A", "B", 2, 1), "A WINS!")
        self.assertEqual(result_text("A", "B", 1, 2), "B WINS!")
        self.assertEqual(result_text("A", "B", 1, 1), "MATCH DRAWN")


if __name__ == "__main__":
    unittest.main()
