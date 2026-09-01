import os
import platform
import random
import shutil
import subprocess
import threading
import time
from pathlib import Path

import plotly.graph_objects as go


BASE_DIR = Path(__file__).parent
COMMENTARY_SOUND = BASE_DIR / "Sounds" / "Ankara messi.mp3"
FINAL_WHISTLE_SOUND = BASE_DIR / "Sounds" / "final whistle.mp3"

FRAME_DURATION_MS = 5000

BLUE_POSITIONS = [(40, 9), (40, 28), (22, 47), (58, 47), (40, 66)]
RED_POSITIONS = [(40, 111), (40, 92), (22, 73), (58, 73), (40, 57)]

TEAM_ONE_COLOUR = "#25a7ff"
TEAM_TWO_COLOUR = "#ff4f67"
PITCH_COLOUR = "#087548"
LINE_COLOUR = "#d8fff0"
PAGE_COLOUR = "#031c18"


def short_name(full_name):
    """Return a readable short player name for a small pitch circle."""

    preferred_names = {
        "Virgil van Dijk": "Van Dijk",
        "Kevin De Bruyne": "De Bruyne",
        "Vinicius Jr": "Vini Jr",
        "Cristiano Ronaldo": "Ronaldo",
        "Lionel Messi": "Messi",
        "Neymar Jr": "Neymar",
        "Jude Bellingham": "Bellingham",
        "Bruno Fernandes": "Bruno",
        "Bernardo Silva": "Bernardo",
        "Federico Valverde": "Valverde",
        "Martin Odegaard": "Odegaard",
    }

    if full_name in preferred_names:
        return preferred_names[full_name]

    return str(full_name).split()[-1]


def play_sound(sound_file):
    """Play an MP3 without pygame. Failure never stops the game."""

    sound_file = Path(sound_file)
    if not sound_file.exists():
        return False

    try:
        system = platform.system()

        if system == "Darwin" and shutil.which("afplay"):
            subprocess.Popen(
                ["afplay", str(sound_file)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True

        if system == "Windows":
            safe_path = str(sound_file).replace("'", "''")
            script = (
                "$p = New-Object -ComObject WMPlayer.OCX; "
                f"$p.URL = '{safe_path}'; "
                "$p.settings.volume = 70; "
                "$p.controls.play(); "
                "while ($p.playState -ne 1) { "
                "Start-Sleep -Milliseconds 200 }"
            )
            creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            subprocess.Popen(
                [
                    "powershell",
                    "-NoProfile",
                    "-WindowStyle",
                    "Hidden",
                    "-Command",
                    script,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creation_flags,
            )
            return True

        if shutil.which("ffplay"):
            subprocess.Popen(
                [
                    "ffplay",
                    "-nodisp",
                    "-autoexit",
                    "-loglevel",
                    "quiet",
                    str(sound_file),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
    except (OSError, subprocess.SubprocessError):
        pass

    return False


def _start_sound_timeline(events):
    """Approximately synchronize goal sounds with Plotly animation frames."""

    if os.environ.get("FIVE90_SOUND", "1") == "0":
        return

    frame_seconds = FRAME_DURATION_MS / 1000

    def worker():
        for event in events:
            time.sleep(frame_seconds)
            if event["type"] == "goal":
                play_sound(COMMENTARY_SOUND)
        play_sound(FINAL_WHISTLE_SOUND)

    threading.Thread(target=worker, daemon=True).start()


def _jitter_positions(base_positions, frame_index):
    rng = random.Random(590 + frame_index)
    return [
        (
            x + rng.uniform(-1.3, 1.3),
            y + rng.uniform(-1.5, 1.5),
        )
        for x, y in base_positions
    ]


def _player_index(team, player_name):
    for index, player in enumerate(team):
        if player["name"] == player_name:
            return index
    return 4


def _ball_position(event, team_one, team_two, blue_positions, red_positions):
    attacking_team = event["attacking_team"]
    team = team_one if attacking_team == 1 else team_two
    positions = blue_positions if attacking_team == 1 else red_positions
    attacker_index = _player_index(team, event["player"])
    player_x, player_y = positions[attacker_index]

    if event["type"] == "goal":
        return (40, 123 if attacking_team == 1 else -3)

    if event["type"] in {"shot", "save"}:
        goal_y = 113 if attacking_team == 1 else 7
        return ((player_x + 40) / 2, goal_y)

    teammate_index = (attacker_index + 1) % len(positions)
    teammate_x, teammate_y = positions[teammate_index]
    return (
        (player_x + teammate_x) / 2,
        (player_y + teammate_y) / 2,
    )


def _annotations(event, player_one_name, player_two_name, final=False):
    annotations = [
        {
            "x": 40,
            "y": 137,
            "text": f"<b>{player_one_name}  vs  {player_two_name}</b>",
            "showarrow": False,
            "font": {"size": 22, "color": "white"},
        },
        {
            "x": 40,
            "y": 130,
            "text": (
                f"<b>{event['score_one']}  -  "
                f"{event['score_two']}</b>"
            ),
            "showarrow": False,
            "font": {"size": 30, "color": "#66f5c0"},
        },
        {
            "x": 78,
            "y": 130,
            "text": f"<b>{event['minute']}'</b>",
            "showarrow": False,
            "font": {"size": 18, "color": "white"},
        },
        {
            "x": 40,
            "y": -14,
            "text": f"<b>{event['text']}</b>",
            "showarrow": False,
            "font": {"size": 18, "color": "white"},
            "bgcolor": "rgba(2, 43, 35, 0.92)",
            "bordercolor": "#23d89a",
            "borderwidth": 1,
            "borderpad": 8,
        },
    ]

    if event["type"] == "goal" and not final:
        annotations.append(
            {
                "x": 40,
                "y": 60,
                "text": "<b>GOAL!</b>",
                "showarrow": False,
                "font": {"size": 52, "color": "#f7d65c"},
                "bgcolor": "rgba(0, 25, 20, 0.80)",
                "bordercolor": "#f7d65c",
                "borderwidth": 3,
                "borderpad": 12,
            }
        )

    if event["minute"] == 45:
        annotations.append(
            {
                "x": 40,
                "y": 92,
                "text": "<b>HALF TIME</b>",
                "showarrow": False,
                "font": {"size": 26, "color": "white"},
                "bgcolor": "rgba(0, 25, 20, 0.88)",
                "borderpad": 8,
            }
        )

    if final:
        if event["score_one"] > event["score_two"]:
            winner = f"{player_one_name} WINS!"
        elif event["score_two"] > event["score_one"]:
            winner = f"{player_two_name} WINS!"
        else:
            winner = "MATCH DRAWN"

        annotations.append(
            {
                "x": 40,
                "y": 60,
                "text": f"<b>FULL TIME<br>{winner}</b>",
                "showarrow": False,
                "font": {"size": 34, "color": "#66f5c0"},
                "bgcolor": "rgba(0, 25, 20, 0.92)",
                "bordercolor": "#66f5c0",
                "borderwidth": 3,
                "borderpad": 14,
            }
        )

    return annotations


def _add_pitch_shapes(fig):
    fig.add_shape(
        type="rect",
        x0=0,
        y0=0,
        x1=80,
        y1=120,
        line={"color": LINE_COLOUR, "width": 3},
        fillcolor=PITCH_COLOUR,
        layer="below",
    )
    fig.add_shape(
        type="line",
        x0=0,
        y0=60,
        x1=80,
        y1=60,
        line={"color": LINE_COLOUR, "width": 2},
    )
    fig.add_shape(
        type="circle",
        x0=27,
        y0=47,
        x1=53,
        y1=73,
        line={"color": LINE_COLOUR, "width": 2},
    )
    fig.add_shape(
        type="circle",
        x0=39,
        y0=59,
        x1=41,
        y1=61,
        line={"color": LINE_COLOUR, "width": 1},
        fillcolor=LINE_COLOUR,
    )

    for y0, y1 in [(0, 20), (100, 120)]:
        fig.add_shape(
            type="rect",
            x0=20,
            y0=y0,
            x1=60,
            y1=y1,
            line={"color": LINE_COLOUR, "width": 2},
        )

    fig.add_shape(
        type="rect",
        x0=28,
        y0=-6,
        x1=52,
        y1=0,
        line={"color": LINE_COLOUR, "width": 3},
    )
    fig.add_shape(
        type="rect",
        x0=28,
        y0=120,
        x1=52,
        y1=126,
        line={"color": LINE_COLOUR, "width": 3},
    )


def _team_trace(positions, names, colour, trace_name):
    return go.Scatter(
        x=[position[0] for position in positions],
        y=[position[1] for position in positions],
        mode="markers+text",
        text=names,
        textposition="middle center",
        textfont={"size": 10, "color": "white"},
        marker={
            "size": 47,
            "color": colour,
            "line": {"color": "white", "width": 2},
        },
        hovertemplate="%{text}<extra></extra>",
        name=trace_name,
    )


def show_match(team_one, team_two, events, player_one_name, player_two_name):
    """Open the animated FIVE90 match replay in Plotly."""

    if not events:
        raise ValueError("The match replay needs at least one event.")

    team_one_names = [short_name(player["name"]) for player in team_one]
    team_two_names = [short_name(player["name"]) for player in team_two]

    fig = go.Figure()
    _add_pitch_shapes(fig)

    fig.add_trace(
        _team_trace(
            BLUE_POSITIONS,
            team_one_names,
            TEAM_ONE_COLOUR,
            player_one_name,
        )
    )
    fig.add_trace(
        _team_trace(
            RED_POSITIONS,
            team_two_names,
            TEAM_TWO_COLOUR,
            player_two_name,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[40],
            y=[60],
            mode="text",
            text=["⚽"],
            textfont={"size": 28},
            hoverinfo="skip",
            showlegend=False,
        )
    )

    frames = []

    for frame_index, event in enumerate(events):
        blue_positions = _jitter_positions(BLUE_POSITIONS, frame_index)
        red_positions = _jitter_positions(RED_POSITIONS, frame_index + 100)
        ball_x, ball_y = _ball_position(
            event,
            team_one,
            team_two,
            blue_positions,
            red_positions,
        )

        frames.append(
            go.Frame(
                name=str(event["minute"]),
                data=[
                    _team_trace(
                        blue_positions,
                        team_one_names,
                        TEAM_ONE_COLOUR,
                        player_one_name,
                    ),
                    _team_trace(
                        red_positions,
                        team_two_names,
                        TEAM_TWO_COLOUR,
                        player_two_name,
                    ),
                    go.Scatter(
                        x=[ball_x],
                        y=[ball_y],
                        mode="text",
                        text=["⚽"],
                        textfont={"size": 28},
                        hoverinfo="skip",
                        showlegend=False,
                    ),
                ],
                traces=[0, 1, 2],
                layout=go.Layout(
                    annotations=_annotations(
                        event,
                        player_one_name,
                        player_two_name,
                        final=frame_index == len(events) - 1,
                    )
                ),
            )
        )

    fig.frames = frames
    first_event = events[0]

    slider_steps = [
        {
            "label": f"{event['minute']}'",
            "method": "animate",
            "args": [
                [str(event["minute"])],
                {
                    "mode": "immediate",
                    "frame": {"duration": 0, "redraw": True},
                    "transition": {"duration": 0},
                },
            ],
        }
        for event in events
    ]

    fig.update_layout(
        title={
            "text": "FIVE90 — MATCH REPLAY",
            "x": 0.5,
            "font": {"size": 24, "color": "#66f5c0"},
        },
        width=860,
        height=1050,
        paper_bgcolor=PAGE_COLOUR,
        plot_bgcolor=PAGE_COLOUR,
        margin={"l": 45, "r": 45, "t": 90, "b": 120},
        showlegend=False,
        annotations=_annotations(
            first_event,
            player_one_name,
            player_two_name,
        ),
        updatemenus=[
            {
                "type": "buttons",
                "showactive": False,
                "x": 0.5,
                "y": -0.055,
                "xanchor": "center",
                "buttons": [
                    {
                        "label": "▶ PLAY MATCH",
                        "method": "animate",
                        "args": [
                            None,
                            {
                                "fromcurrent": True,
                                "frame": {
                                    "duration": FRAME_DURATION_MS,
                                    "redraw": True,
                                },
                                "transition": {"duration": 650},
                            },
                        ],
                    },
                    {
                        "label": "❚❚ PAUSE",
                        "method": "animate",
                        "args": [
                            [None],
                            {
                                "mode": "immediate",
                                "frame": {"duration": 0, "redraw": False},
                                "transition": {"duration": 0},
                            },
                        ],
                    },
                ],
            }
        ],
        sliders=[
            {
                "active": 0,
                "steps": slider_steps,
                "x": 0.08,
                "len": 0.84,
                "y": -0.105,
                "currentvalue": {
                    "prefix": "Minute: ",
                    "font": {"color": "white"},
                },
                "font": {"color": "white"},
            }
        ],
    )

    fig.update_xaxes(range=[-5, 85], visible=False, fixedrange=True)
    fig.update_yaxes(
        range=[-19, 142],
        visible=False,
        fixedrange=True,
        scaleanchor="x",
        scaleratio=1
    )

    # =========================
    # FIGURE SIZE
    # =========================

    fig.update_layout(
        width=900,
        height=1100,
        margin=dict(
            l=40,
            r=40,
            t=60,
            b=80
        ),
        showlegend=False
    )

    fig.show()


# =========================
# TEST
# =========================

show_match(
    "Blue Team",
    "Red Team",
    ["Match started!"],
    "Player 1",
    "Player 2"
)