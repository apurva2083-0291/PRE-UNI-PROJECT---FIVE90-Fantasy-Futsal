import random

import plotly.graph_objects as go


FRAME_DURATION_MS = 550
TRANSITION_DURATION_MS = 150

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


def _text_trace(x, y, text, size, colour="white"):
    """Return replay text as data so every frame replaces it reliably."""

    return go.Scatter(
        x=[x],
        y=[y],
        mode="text",
        text=[text],
        textposition="middle center",
        textfont={"size": size, "color": colour},
        hoverinfo="skip",
        showlegend=False,
        cliponaxis=False,
    )


def _status_traces(text):
    """Return a final-score panel and its text as reliable data traces."""

    visible = bool(text.strip())
    panel_colour = "rgba(0, 25, 20, 0.92)" if visible else "rgba(0,0,0,0)"
    border_colour = "#66f5c0" if visible else "rgba(0,0,0,0)"

    panel = go.Scatter(
        x=[11, 69, 69, 11, 11],
        y=[63, 63, 81, 81, 63],
        mode="lines",
        fill="toself",
        fillcolor=panel_colour,
        line={"color": border_colour, "width": 3},
        hoverinfo="skip",
        showlegend=False,
    )
    message = _text_trace(40, 72, text, 34, "#66f5c0")
    return panel, message


def _full_time_text(event, player_one_name, player_two_name, final=False):
    """Return the winner message only for the final replay frame."""

    if not final:
        return " "

    if event["score_one"] > event["score_two"]:
        winner = f"{player_one_name} WINS!"
    elif event["score_two"] > event["score_one"]:
        winner = f"{player_two_name} WINS!"
    else:
        winner = "MATCH DRAWN"

    return f"<b>FULL TIME<br>{winner}</b>"


def _add_pitch_shapes(fig):
    fig.add_shape(
        type="rect",
        x0=6,
        y0=-18,
        x1=74,
        y1=-10,
        line={"color": "#23d89a", "width": 1},
        fillcolor="rgba(2, 43, 35, 0.92)",
        layer="below",
    )
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


def _ball_trace(ball_x, ball_y):
    """Return the lightweight ball trace used in every animation frame."""

    return go.Scatter(
        x=[ball_x],
        y=[ball_y],
        mode="text",
        text=["⚽"],
        textfont={"size": 28},
        hoverinfo="skip",
        showlegend=False,
    )


def build_match_figure(
    team_one,
    team_two,
    events,
    player_one_name,
    player_two_name,
):
    """Build a smooth replay figure that cannot be skipped with a slider."""

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
    fig.add_trace(_ball_trace(40, 60))
    fig.add_trace(
        _text_trace(
            40,
            137,
            f"<b>{player_one_name}  vs  {player_two_name}</b>",
            22,
        )
    )
    fig.add_trace(_text_trace(40, 130, "<b>0  -  0</b>", 30, "#66f5c0"))
    fig.add_trace(_text_trace(78, 130, "<b>0'</b>", 18))
    fig.add_trace(
        _text_trace(
            40,
            -14,
            "<b>Press PLAY MATCH to begin the replay.</b>",
            18,
        )
    )
    status_panel, status_message = _status_traces(" ")
    fig.add_trace(status_panel)
    fig.add_trace(status_message)

    frames = []
    previous_ball = (40, 60)
    previous_score = (0, 0)

    for event_index, event in enumerate(events):
        move_positions_one = _jitter_positions(
            BLUE_POSITIONS,
            event_index * 2,
        )
        move_positions_two = _jitter_positions(
            RED_POSITIONS,
            event_index * 2 + 100,
        )
        event_positions_one = _jitter_positions(
            BLUE_POSITIONS,
            event_index * 2 + 1,
        )
        event_positions_two = _jitter_positions(
            RED_POSITIONS,
            event_index * 2 + 101,
        )

        target_ball = _ball_position(
            event,
            team_one,
            team_two,
            event_positions_one,
            event_positions_two,
        )
        moving_ball = (
            (previous_ball[0] + target_ball[0]) / 2,
            (previous_ball[1] + target_ball[1]) / 2,
        )
        frames.append(
            go.Frame(
                name=f"{event_index}-move",
                data=[
                    _team_trace(
                        move_positions_one,
                        team_one_names,
                        TEAM_ONE_COLOUR,
                        player_one_name,
                    ),
                    _team_trace(
                        move_positions_two,
                        team_two_names,
                        TEAM_TWO_COLOUR,
                        player_two_name,
                    ),
                    _ball_trace(*moving_ball),
                    _text_trace(
                        40,
                        130,
                        f"<b>{previous_score[0]}  -  {previous_score[1]}</b>",
                        30,
                        "#66f5c0",
                    ),
                    _text_trace(78, 130, f"<b>{event['minute']}'</b>", 18),
                    _text_trace(
                        40,
                        -14,
                        f"<b>{event['player']} builds the attack...</b>",
                        18,
                    ),
                    *_status_traces(" "),
                ],
                traces=[0, 1, 2, 4, 5, 6, 7, 8],
            )
        )

        is_final_event = event_index == len(events) - 1
        frames.append(
            go.Frame(
                name=f"{event_index}-event",
                data=[
                    _team_trace(
                        event_positions_one,
                        team_one_names,
                        TEAM_ONE_COLOUR,
                        player_one_name,
                    ),
                    _team_trace(
                        event_positions_two,
                        team_two_names,
                        TEAM_TWO_COLOUR,
                        player_two_name,
                    ),
                    _ball_trace(*target_ball),
                    _text_trace(
                        40,
                        130,
                        f"<b>{event['score_one']}  -  {event['score_two']}</b>",
                        30,
                        "#66f5c0",
                    ),
                    _text_trace(78, 130, f"<b>{event['minute']}'</b>", 18),
                    _text_trace(40, -14, f"<b>{event['text']}</b>", 18),
                    *_status_traces(
                        _full_time_text(
                            event,
                            player_one_name,
                            player_two_name,
                            final=is_final_event,
                        )
                    ),
                ],
                traces=[0, 1, 2, 4, 5, 6, 7, 8],
            )
        )

        previous_ball = target_ball
        previous_score = (event["score_one"], event["score_two"])

    fig.frames = frames
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
        margin={"l": 45, "r": 45, "t": 90, "b": 90},
        showlegend=False,
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
                                    "redraw": False,
                                },
                                "transition": {
                                    "duration": TRANSITION_DURATION_MS,
                                    "easing": "linear",
                                },
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
    )

    fig.update_xaxes(range=[-5, 85], visible=False, fixedrange=True)
    fig.update_yaxes(
        range=[-19, 142],
        visible=False,
        fixedrange=True,
        scaleanchor="x",
        scaleratio=1,
    )

    return fig


def show_match(team_one, team_two, events, player_one_name, player_two_name):
    """Open the clean animated FIVE90 match replay in Plotly."""

    fig = build_match_figure(
        team_one,
        team_two,
        events,
        player_one_name,
        player_two_name,
    )
    fig.show(
        config={
            "displaylogo": False,
            "displayModeBar": False,
            "responsive": True,
            "scrollZoom": False,
        }
    )
    return fig


if __name__ == "__main__":
    import random as random_module

    from match import create_test_teams, simulate_match

    test_team_one, test_team_two = create_test_teams()
    _, _, test_events = simulate_match(
        test_team_one,
        test_team_two,
        random_module.Random(90),
    )
    show_match(
        test_team_one,
        test_team_two,
        test_events,
        "Player 1",
        "Player 2",
    )
