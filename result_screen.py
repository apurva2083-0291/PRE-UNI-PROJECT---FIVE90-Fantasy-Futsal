import tkinter as tk
from pathlib import Path

from PIL import Image, ImageTk

from match import goal_events


BASE_DIR = Path(__file__).parent
FULL_TIME_BACKGROUND = BASE_DIR / "Screens" / "full_time_background.png"


def result_text(player_one_name, player_two_name, score_one, score_two):
    """Return the correct winner or draw message."""

    if score_one > score_two:
        return f"{player_one_name.upper()} WINS!"
    if score_two > score_one:
        return f"{player_two_name.upper()} WINS!"
    return "MATCH DRAWN"


class ResultWindow:
    def __init__(
        self,
        player_one_name,
        player_two_name,
        score_one,
        score_two,
        events,
    ):
        self.action = "exit"
        self.photos = []

        self.root = tk.Tk()
        self.root.title("FIVE90 — Full Time")
        self.root.geometry("1000x720")
        self.root.minsize(850, 650)
        self.root.configure(bg="#031c18")
        self.root.protocol("WM_DELETE_WINDOW", self.exit_game)

        if FULL_TIME_BACKGROUND.exists():
            background = Image.open(FULL_TIME_BACKGROUND).convert("RGB")
            background.thumbnail((1000, 720), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(background)
            self.photos.append(photo)
            tk.Label(
                self.root,
                image=photo,
                borderwidth=0,
            ).place(relx=0.5, rely=0.5, anchor="center")

        panel = tk.Frame(
            self.root,
            bg="#032b23",
            highlightbackground="#27d69b",
            highlightthickness=3,
            padx=55,
            pady=32,
        )
        panel.place(relx=0.5, rely=0.52, anchor="center")

        tk.Label(
            panel,
            text="FULL TIME",
            bg="#032b23",
            fg="#65f5c0",
            font=("Arial", 24, "bold"),
        ).pack()

        tk.Label(
            panel,
            text=result_text(
                player_one_name,
                player_two_name,
                score_one,
                score_two,
            ),
            bg="#032b23",
            fg="white",
            font=("Arial", 31, "bold"),
        ).pack(pady=(14, 8))

        tk.Label(
            panel,
            text=(
                f"{player_one_name}   {score_one}  -  {score_two}   "
                f"{player_two_name}"
            ),
            bg="#032b23",
            fg="#f5d866",
            font=("Arial", 22, "bold"),
        ).pack(pady=(0, 22))

        goals = goal_events(events)
        if goals:
            goal_lines = [
                f"{event['player']}  {event['minute']}'"
                for event in goals
            ]
            goals_text = "GOALS\n" + "\n".join(goal_lines)
        else:
            goals_text = "NO GOALS"

        tk.Label(
            panel,
            text=goals_text,
            bg="#032b23",
            fg="#d4fff1",
            font=("Arial", 13, "bold"),
            justify="center",
        ).pack(pady=(0, 24))

        buttons = tk.Frame(panel, bg="#032b23")
        buttons.pack()

        self._button(buttons, "REMATCH", "rematch", 0)
        self._button(buttons, "NEW DRAFT", "new_draft", 1)
        self._button(buttons, "EXIT", "exit", 2)

    def _button(self, parent, text, action, column):
        tk.Button(
            parent,
            text=text,
            command=lambda: self.finish(action),
            bg="#20c98b" if action != "exit" else "#173f36",
            fg="#001e17" if action != "exit" else "white",
            activebackground="#65f5c0",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=8,
            cursor="hand2",
        ).grid(row=0, column=column, padx=7)

    def finish(self, action):
        self.action = action
        self.root.destroy()

    def exit_game(self):
        self.finish("exit")

    def run(self):
        self.root.mainloop()
        return self.action


def show_result(
    player_one_name,
    player_two_name,
    score_one,
    score_two,
    events,
    use_gui=True,
):
    """Show full-time results and return rematch, new_draft, or exit."""

    if use_gui:
        try:
            return ResultWindow(
                player_one_name,
                player_two_name,
                score_one,
                score_two,
                events,
            ).run()
        except tk.TclError:
            pass

    print()
    print("FULL TIME")
    print(result_text(player_one_name, player_two_name, score_one, score_two))
    print(
        f"{player_one_name} {score_one} - {score_two} {player_two_name}"
    )

    while True:
        choice = input("[R]ematch, [N]ew draft, or [E]xit: ").strip().lower()
        if choice in {"r", "rematch"}:
            return "rematch"
        if choice in {"n", "new", "new draft"}:
            return "new_draft"
        if choice in {"e", "exit", "q", "quit"}:
            return "exit"
