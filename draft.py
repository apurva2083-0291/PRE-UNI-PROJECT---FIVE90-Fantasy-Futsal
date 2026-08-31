import random
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from PIL import Image, ImageTk

from card_generator import OUTPUT_FOLDER, generate_player_card
from data_manager import load_players


BASE_DIR = Path(__file__).parent
SCREENS_FOLDER = BASE_DIR / "Screens"

DRAFT_POSITIONS = ["GK", "DEF", "MID", "MID", "ATT"]
POSITION_NAMES = {
    "GK": "Goalkeeper",
    "DEF": "Defender",
    "MID": "Midfielder",
    "ATT": "Attacker",
}


def create_balanced_first_picker_order(rng=None):
    """Return five first-pickers: one player starts 3 times, the other 2."""

    rng = rng or random.Random()
    three_pick_player = rng.choice([0, 1])
    two_pick_player = 1 - three_pick_player

    order = [three_pick_player] * 3 + [two_pick_player] * 2
    rng.shuffle(order)
    return order


class DraftSession:
    """Store and validate the complete five-round draft state."""

    def __init__(self, player_names, players=None, rng=None):
        self.player_names = player_names
        self.players = players or load_players()
        self.rng = rng or random.Random()
        self.first_picker_order = create_balanced_first_picker_order(
            self.rng
        )
        self.teams = [[], []]
        self.selected_ids = set()
        self.round_index = 0
        self.pick_in_round = 0
        self.options = []
        self.prepare_round()

    @property
    def complete(self):
        return self.round_index >= len(DRAFT_POSITIONS)

    @property
    def required_position(self):
        if self.complete:
            return None
        return DRAFT_POSITIONS[self.round_index]

    @property
    def current_picker(self):
        if self.complete:
            return None

        first_picker = self.first_picker_order[self.round_index]
        if self.pick_in_round == 0:
            return first_picker
        return 1 - first_picker

    def prepare_round(self):
        """Randomly select four unpicked choices for the required position."""

        if self.complete:
            self.options = []
            return

        candidates = [
            player
            for player in self.players
            if player["position"] == self.required_position
            and player["id"] not in self.selected_ids
        ]

        if len(candidates) < 4:
            raise RuntimeError(
                f"Not enough {self.required_position} players remain."
            )

        self.options = self.rng.sample(candidates, 4)
        self.pick_in_round = 0

    def available_options(self):
        """Return this round's options that have not already been selected."""

        return [
            player
            for player in self.options
            if player["id"] not in self.selected_ids
        ]

    def choose(self, player_id):
        """Add a valid selected player to the current picker's team."""

        player_id = int(player_id)
        available = {
            player["id"]: player
            for player in self.available_options()
        }

        if player_id not in available:
            raise ValueError("That player is not available for this pick.")

        selected_player = available[player_id]
        picker = self.current_picker

        self.teams[picker].append(selected_player)
        self.selected_ids.add(player_id)
        self.pick_in_round += 1

        if self.pick_in_round == 2:
            self.round_index += 1
            if not self.complete:
                self.prepare_round()

        return selected_player


def _valid_names(name_one, name_two):
    name_one = name_one.strip()
    name_two = name_two.strip()

    if not name_one or not name_two:
        return False, "Both players must enter a name."

    if name_one.casefold() == name_two.casefold():
        return False, "Please enter two different player names."

    return True, ""


class DraftWindow:
    """Simple same-device graphical interface for the complete draft."""

    def __init__(self, players, rng=None):
        self.players = players
        self.rng = rng or random.Random()
        self.session = None
        self.result = None
        self.photos = []

        self.root = tk.Tk()
        self.root.title("FIVE90 — Fantasy Futsal Draft")
        self.root.geometry("1200x780")
        self.root.minsize(980, 680)
        self.root.configure(bg="#041c18")
        self.root.protocol("WM_DELETE_WINDOW", self.close_game)

        self.show_name_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.photos.clear()

    def add_background(self, filename):
        path = SCREENS_FOLDER / filename

        if not path.exists():
            return

        image = Image.open(path).convert("RGB")
        image.thumbnail((1200, 780), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.photos.append(photo)

        label = tk.Label(self.root, image=photo, borderwidth=0)
        label.place(relx=0.5, rely=0.5, anchor="center")

    def show_name_screen(self):
        self.clear_screen()
        self.add_background("title_screen.png")

        panel = tk.Frame(
            self.root,
            bg="#052d26",
            highlightbackground="#27d69b",
            highlightthickness=2,
            padx=45,
            pady=30,
        )
        panel.place(relx=0.5, rely=0.62, anchor="center")

        tk.Label(
            panel,
            text="DRAFT FIVE. PLAY NINETY.",
            bg="#052d26",
            fg="#65f5c0",
            font=("Arial", 20, "bold"),
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        tk.Label(
            panel,
            text="Player 1",
            bg="#052d26",
            fg="white",
            font=("Arial", 13, "bold"),
        ).grid(row=1, column=0, padx=12, pady=8, sticky="e")

        self.name_one_entry = tk.Entry(
            panel,
            width=24,
            font=("Arial", 14),
        )
        self.name_one_entry.grid(row=1, column=1, padx=12, pady=8)

        tk.Label(
            panel,
            text="Player 2",
            bg="#052d26",
            fg="white",
            font=("Arial", 13, "bold"),
        ).grid(row=2, column=0, padx=12, pady=8, sticky="e")

        self.name_two_entry = tk.Entry(
            panel,
            width=24,
            font=("Arial", 14),
        )
        self.name_two_entry.grid(row=2, column=1, padx=12, pady=8)

        tk.Button(
            panel,
            text="START DRAFT",
            command=self.begin_draft,
            bg="#20c98b",
            fg="#001e17",
            activebackground="#65f5c0",
            font=("Arial", 14, "bold"),
            padx=25,
            pady=8,
            cursor="hand2",
        ).grid(row=3, column=0, columnspan=2, pady=(22, 0))

        self.name_one_entry.focus_set()

    def begin_draft(self):
        name_one = self.name_one_entry.get().strip()
        name_two = self.name_two_entry.get().strip()
        valid, problem = _valid_names(name_one, name_two)

        if not valid:
            messagebox.showerror("Cannot start draft", problem)
            return

        self.session = DraftSession(
            [name_one, name_two],
            self.players,
            self.rng,
        )
        self.show_draft_round()

    def show_draft_round(self):
        if self.session.complete:
            self.show_completed_teams()
            return

        self.clear_screen()
        self.add_background("draft_background.png")

        round_number = self.session.round_index + 1
        position = self.session.required_position
        picker_name = self.session.player_names[
            self.session.current_picker
        ]

        header = tk.Frame(self.root, bg="#03231d", padx=20, pady=12)
        header.pack(fill="x")

        tk.Label(
            header,
            text=f"ROUND {round_number}/5 — {POSITION_NAMES[position].upper()}",
            bg="#03231d",
            fg="#62f5bd",
            font=("Arial", 21, "bold"),
        ).pack()

        tk.Label(
            header,
            text=f"{picker_name}, choose your player",
            bg="#03231d",
            fg="white",
            font=("Arial", 16, "bold"),
        ).pack(pady=(5, 0))

        choices = tk.Frame(self.root, bg="#041c18")
        choices.pack(expand=True, fill="both", padx=22, pady=18)

        options = self.session.available_options()

        for column, player in enumerate(options):
            card_path = OUTPUT_FOLDER / (
                player["name"].replace(" ", "_") + "_Card.png"
            )

            if not card_path.exists():
                card_path = generate_player_card(player)

            card_image = Image.open(card_path).convert("RGBA")
            card_image.thumbnail((235, 335), Image.Resampling.LANCZOS)
            card_photo = ImageTk.PhotoImage(card_image)
            self.photos.append(card_photo)

            option_panel = tk.Frame(choices, bg="#052d26", padx=8, pady=8)
            option_panel.grid(
                row=0,
                column=column,
                padx=9,
                pady=5,
                sticky="n",
            )

            tk.Button(
                option_panel,
                image=card_photo,
                text=f"Select {player['name']}",
                command=lambda player_id=player["id"]: self.select_player(
                    player_id
                ),
                borderwidth=0,
                bg="#052d26",
                activebackground="#0b5443",
                cursor="hand2",
            ).pack()

            tk.Button(
                option_panel,
                text=f"SELECT {player['name'].upper()}",
                command=lambda player_id=player["id"]: self.select_player(
                    player_id
                ),
                bg="#20c98b",
                fg="#001e17",
                font=("Arial", 10, "bold"),
                wraplength=210,
                cursor="hand2",
            ).pack(fill="x", pady=(8, 0))

        team_text = (
            f"{self.session.player_names[0]}: "
            f"{len(self.session.teams[0])}/5     |     "
            f"{self.session.player_names[1]}: "
            f"{len(self.session.teams[1])}/5"
        )

        tk.Label(
            self.root,
            text=team_text,
            bg="#03231d",
            fg="white",
            font=("Arial", 13, "bold"),
            pady=10,
        ).pack(fill="x", side="bottom")

    def select_player(self, player_id):
        picker_name = self.session.player_names[
            self.session.current_picker
        ]

        try:
            selected = self.session.choose(player_id)
        except ValueError as error:
            messagebox.showerror("Invalid selection", str(error))
            return

        messagebox.showinfo(
            "Player selected",
            f"{selected['name']} joins "
            f"{picker_name}'s team.",
        )
        self.show_draft_round()

    def show_completed_teams(self):
        self.clear_screen()

        tk.Label(
            self.root,
            text="DRAFT COMPLETE",
            bg="#041c18",
            fg="#62f5bd",
            font=("Arial", 30, "bold"),
        ).pack(pady=(40, 20))

        teams_frame = tk.Frame(self.root, bg="#041c18")
        teams_frame.pack(expand=True)

        for index, team in enumerate(self.session.teams):
            panel = tk.Frame(
                teams_frame,
                bg="#052d26",
                highlightbackground="#20c98b",
                highlightthickness=2,
                padx=35,
                pady=25,
            )
            panel.grid(row=0, column=index, padx=30)

            tk.Label(
                panel,
                text=self.session.player_names[index],
                bg="#052d26",
                fg="white",
                font=("Arial", 22, "bold"),
            ).pack(pady=(0, 16))

            for player in team:
                tk.Label(
                    panel,
                    text=(
                        f"{player['position']}  "
                        f"{player['name']}  ({player['overall']})"
                    ),
                    bg="#052d26",
                    fg="#c9fbed",
                    font=("Arial", 13, "bold"),
                    anchor="w",
                    width=29,
                ).pack(pady=5)

        tk.Button(
            self.root,
            text="PLAY MATCH",
            command=self.finish_draft,
            bg="#20c98b",
            fg="#001e17",
            font=("Arial", 16, "bold"),
            padx=35,
            pady=10,
            cursor="hand2",
        ).pack(pady=35)

    def finish_draft(self):
        self.result = (
            self.session.player_names[0],
            self.session.player_names[1],
            self.session.teams[0],
            self.session.teams[1],
        )
        self.root.destroy()

    def close_game(self):
        self.result = None
        self.root.destroy()

    def run(self):
        self.root.mainloop()
        return self.result


def start_console_draft(players=None, rng=None):
    """Reliable terminal fallback when a graphical window cannot open."""

    players = players or load_players()

    while True:
        name_one = input("Enter Player 1 name: ").strip()
        name_two = input("Enter Player 2 name: ").strip()
        valid, problem = _valid_names(name_one, name_two)

        if valid:
            break

        print(problem)

    session = DraftSession([name_one, name_two], players, rng)

    while not session.complete:
        print()
        print(
            f"ROUND {session.round_index + 1}/5 — "
            f"{POSITION_NAMES[session.required_position]}"
        )

        picker_name = session.player_names[session.current_picker]
        print(f"{picker_name}'s pick:")

        for player in session.available_options():
            print(
                f"  {player['id']}: {player['name']} "
                f"({player['position']}, {player['overall']})"
            )

        try:
            selected_id = int(input("Enter player ID: "))
            session.choose(selected_id)
        except (ValueError, TypeError) as error:
            print(f"Invalid selection: {error}")

    return name_one, name_two, session.teams[0], session.teams[1]


def start_draft(use_gui=True, players=None, rng=None):
    """Run the graphical draft, with a console fallback if needed."""

    players = players or load_players()

    if use_gui:
        try:
            result = DraftWindow(players, rng).run()
            return result
        except tk.TclError:
            print("Graphical mode is unavailable; using terminal draft.")

    return start_console_draft(players, rng)


def create_automatic_test_draft(seed=90):
    """Create a valid complete draft without user input for testing."""

    rng = random.Random(seed)
    session = DraftSession(
        ["Test Player 1", "Test Player 2"],
        load_players(),
        rng,
    )

    while not session.complete:
        session.choose(session.available_options()[0]["id"])

    return session


if __name__ == "__main__":
    start_draft()
