import plotly.graph_objects as go

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

# Blue team is attacking towards the TOP
#
#             GK
#             DEF
#       MID         MID
#             ATT
#              ⚽

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
        name="Blue Team"
    )
)

# =========================
# RED TEAM
# =========================

# Red team is attacking towards the BOTTOM
#
#              ⚽
#             ATT
#       MID         MID
#             DEF
#             GK

red_x = [40, 40, 22, 58, 40]
red_y = [112, 95, 80, 80, 65]

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
        name="Red Team"
    )
)

# =========================
# BALL
# =========================

# White football
fig.add_shape(
    type="circle",
    x0=38.5,
    y0=58.5,
    x1=41.5,
    y1=61.5,
    fillcolor="white",
    line=dict(
        color="black",
        width=2
    )
)

# Black centre detail
fig.add_shape(
    type="circle",
    x0=39.4,
    y0=59.4,
    x1=40.6,
    y1=60.6,
    fillcolor="black",
    line=dict(width=0)
)

# Small black details
fig.add_shape(
    type="circle",
    x0=38.9,
    y0=60.8,
    x1=39.6,
    y1=61.5,
    fillcolor="black",
    line=dict(width=0)
)

fig.add_shape(
    type="circle",
    x0=40.4,
    y0=58.5,
    x1=41.1,
    y1=59.2,
    fillcolor="black",
    line=dict(width=0)
)

fig.add_shape(
    type="circle",
    x0=40.4,
    y0=60.8,
    x1=41.1,
    y1=61.5,
    fillcolor="black",
    line=dict(width=0)
)

# =========================
# AXES
# =========================

fig.update_xaxes(
    range=[0, 80],
    visible=False
)

fig.update_yaxes(
    range=[-10, 130],
    visible=False,
    scaleanchor="x",
    scaleratio=1
)

# =========================
# FIGURE SIZE
# =========================

fig.update_layout(
    width=800,
    height=1100,
    margin=dict(
        l=20,
        r=20,
        t=20,
        b=20
    ),
    showlegend=False
)

fig.show()