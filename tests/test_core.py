import random
import unittest
from unittest.mock import Mock, patch

from PIL import Image

from card_generator import IMAGE_FOLDER, remove_checkerboard_background

from data_manager import (
    get_player_by_id,
    get_players_by_position,
    load_players,
    validate_players,
)
from draft import (
    DRAFT_POSITIONS,
    DraftWindow,
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
from pitch import build_match_figure


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

    def test_player_selection_changes_screen_without_popup(self):
        window = DraftWindow.__new__(DraftWindow)
        window.session = Mock()
        window.show_draft_round = Mock()

        with patch("draft.messagebox.showinfo") as information_popup:
            window.select_player(1)

        window.session.choose.assert_called_once_with(1)
        window.show_draft_round.assert_called_once_with()
        information_popup.assert_not_called()


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

    def test_replay_has_no_skip_slider_or_stuck_goal_overlay(self):
        _, _, events = simulate_match(
            self.session.teams[0],
            self.session.teams[1],
            random.Random(90),
        )
        figure = build_match_figure(
            self.session.teams[0],
            self.session.teams[1],
            events,
            "A",
            "B",
        )

        self.assertEqual(len(figure.frames), len(events) * 2)
        self.assertEqual(len(figure.layout.sliders), 0)

        for event_index, event in enumerate(events):
            movement_frame = figure.frames[event_index * 2]
            event_frame = figure.frames[event_index * 2 + 1]

            expected_traces = (0, 1, 2, 4, 5, 6, 7, 8)
            self.assertEqual(tuple(movement_frame.traces), expected_traces)
            self.assertEqual(tuple(event_frame.traces), expected_traces)
            self.assertIn("builds the attack", movement_frame.data[5].text[0])
            self.assertIn(event["text"], event_frame.data[5].text[0])
            self.assertEqual(
                bool(event_frame.data[7].text[0].strip()),
                event_index == len(events) - 1,
            )

        self.assertIn("FULL TIME", figure.frames[-1].data[7].text[0])


class CardImageTests(unittest.TestCase):
    def test_existing_transparent_cutouts_keep_all_visible_pixels(self):
        for filename in ["Rudiger.png", "Toni_Kroos.png", "Saliba.png"]:
            image = Image.open(IMAGE_FOLDER / filename).convert("RGBA")
            before = sum(image.getchannel("A").histogram()[1:])
            cleaned = remove_checkerboard_background(image)
            after = sum(cleaned.getchannel("A").histogram()[1:])
            self.assertEqual(after, before, filename)

    def test_fragile_white_detail_assets_have_real_transparency(self):
        for filename in [
            "Valverde.png",
            "Neymar.png",
            "Ronaldo.png",
            "Messi.png",
        ]:
            image = Image.open(IMAGE_FOLDER / filename).convert("RGBA")
            self.assertEqual(image.getchannel("A").getextrema(), (0, 255))


if __name__ == "__main__":
    unittest.main()
