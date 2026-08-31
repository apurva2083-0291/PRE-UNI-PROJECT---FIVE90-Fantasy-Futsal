import plotly.graph_objects as go
import pygame
import os

# =========================
# SOUND
# =========================

pygame.mixer.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COMMENTARY_SOUND = os.path.join(
    BASE_DIR,
    "Sounds",
    "Ankara messi.mp3"
)

FINAL_WHISTLE_SOUND = os.path.join(
    BASE_DIR,
    "Sounds",
    "final whistle.mp3"
)


def play_sound(sound_file):
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()


def show_match(team_one, team_two, events, player_one_name, player_two_name):

    fig = go.Figure()

    # =========================
    # PITCH
    # =========================

    # Main pitch
    fig.add_shape(
        type="rect",
        x0=0,
        y0=0,
        x1=80,
        y1=120,
        line=dict(width=3)
    )

    # Top goal
    fig.add_shape(
        type="rect",
        x0=28,
        y0=120,
        x1=52,
        y1=127,
        line=dict(width=3)
    )

    # Bottom goal
    fig.add_shape(
        type="rect",
        x0=28,
        y0=-7,
        x1=52,
        y1=0,
        line=dict(width=3)
    )

    # Centre line
    fig.add_shape(
        type="line",
        x0=0,
        y0=60,
        x1=80,
        y1=60,
        line=dict(width=2)
    )

    # Centre circle
    fig.add_shape(
        type="circle",
        x0=25,
        y0=45,
        x1=55,
        y1=75,
        line=dict(width=2)
    )

    # =========================
    # BLUE TEAM
    # =========================

    blue_x = [40, 40, 22, 58, 40]
    blue_y = [8, 25, 40, 40, 55]

    blue_names = [
        "GK",
        "DEF",
        "MID",
        "MID",
        "ATT"
    ]

    fig.add_trace(
        go.Scatter(
            x=blue_x,
            y=blue_y,
            mode="markers+text",
            text=blue_names,
            textposition="bottom center",
            marker=dict(
                size=28,
                color="blue"
            ),
            name=team_one
        )
    )

    # =========================
    # RED TEAM
    # =========================

    red_x = [40, 40, 22, 58, 40]

    # ATT moved slightly higher
    # to avoid overlapping the ball.
    red_y = [112, 95, 80, 80, 68]

    red_names = [
        "GK",
        "DEF",
        "MID",
        "MID",
        "ATT"
    ]

    fig.add_trace(
        go.Scatter(
            x=red_x,
            y=red_y,
            mode="markers+text",
            text=red_names,
            textposition="bottom center",
            marker=dict(
                size=28,
                color="red"
            ),
            name=team_two
        )
    )

    # =========================
    # FOOTBALL
    # =========================

    # The football is the familiar black-and-white
    # football emoji.
    #
    # It starts exactly in the centre of the pitch.
    fig.add_trace(
        go.Scatter(
            x=[40],
            y=[60],
            mode="text",
            text=["⚽"],
            textfont=dict(
                size=30
            ),
            showlegend=False
        )
    )

    # =========================
    # BALL ANIMATION
    # =========================

    ball_positions = [
        (40, 60),
        (48, 56),
        (56, 52),
        (64, 48),
        (72, 52)
    ]

    frames = []

    for i, (x, y) in enumerate(ball_positions):

        frames.append(
            go.Frame(
                data=[
                    go.Scatter(
                        x=[x],
                        y=[y],
                        mode="text",
                        text=["⚽"],
                        textfont=dict(
                            size=30
                        ),
                        showlegend=False
                    )
                ],
                traces=[2],
                name=f"frame{i}"
            )
        )

    fig.frames = frames

    # =========================
    # MATCH INFORMATION
    # =========================

    # Player names - top centre
    fig.add_annotation(
        x=40,
        y=135,
        text=f"{player_one_name}  vs  {player_two_name}",
        showarrow=False,
        xanchor="center",
        font=dict(size=22)
    )

    # Score - far top left
    fig.add_annotation(
        x=-10,
        y=135,
        text="Score: 0 - 0",
        showarrow=False,
        xanchor="left",
        font=dict(size=18)
    )

    # Minute - far top right
    fig.add_annotation(
        x=90,
        y=135,
        text="Minute: 0'",
        showarrow=False,
        xanchor="right",
        font=dict(size=18)
    )

    # =========================
    # EVENT TEXT
    # =========================
    event_text = ""

    if events:
        event_text = str(events[0])

    # Play commentary for an exciting event
        if "GOAL" in event_text.upper():
            play_sound(COMMENTARY_SOUND)

    fig.add_annotation(
        x=40,
        y=-15,
        text=event_text,
        showarrow=False,
        xanchor="center",
        font=dict(size=18)
    )

    # =========================
    # PLAY BUTTON
    # =========================

    fig.update_layout(
        updatemenus=[
            {
                "type": "buttons",
                "showactive": False,
                "x": 0.5,
                "y": -0.08,
                "xanchor": "center",
                "buttons": [
                    {
                        "label": "▶ Play Match",
                        "method": "animate",
                        "args": [
                            None,
                            {
                                "frame": {
                                    "duration": 700,
                                    "redraw": True
                                },
                                "fromcurrent": True
                            }
                        ]
                    }
                ]
            }
        ]
    )

    # =========================
    # AXES
    # =========================

    fig.update_xaxes(
        range=[-12, 92],
        visible=False
    )

    fig.update_yaxes(
        range=[-20, 140],
        visible=False,
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