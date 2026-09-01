# FIVE90 — Fantasy Futsal Draft

**Draft Five. Play Ninety.**

FIVE90 is a same-device, two-player fantasy futsal draft and event-based match replay built in Python.

## What the game now includes

- Graphical name-entry screen
- Five draft rounds: `GK`, `DEF`, `MID`, `MID`, `ATT`
- Four randomized player cards per round
- Balanced first-pick order: one user starts three rounds and the other starts two
- No duplicate selections
- Dynamic goalkeeper and outfield cards generated from the CSV
- Validated local database of 27 footballers
- Ratings-based attack, passing, defence, goalkeeper, and overall calculations
- Sixteen events across a virtual 90-minute match
- Passes, shots, saves, goals, half-time, and full-time
- Plotly pitch with five blue players, five red players, surnames, micro-movements, and a moving ball
- Dynamic score, minute, event, winner, and goal-scorer displays
- Rematch, New Draft, and Exit options
- Synchronized "Ankara Messi" goal commentary without `pygame`
- Console fallback for computers where the graphical draft cannot open

## Project structure

```text
FIVE90/
├── data/players.csv
├── Logo/
├── PlayerImages/
├── Screens/
├── Sounds/
├── Templates/
├── tests/
├── card_generator.py
├── data_manager.py
├── draft.py
├── main.py
├── match.py
├── pitch.py
├── result_screen.py
├── requirements.txt
└── test_checklist.md
```

`GeneratedCards/` is created automatically and is not pushed to GitHub because the cards can be regenerated from the templates, CSV, and player images.

## First-time setup — Windows

Open the terminal in the folder containing this README.

```powershell
python -m venv FIVE90.venv
FIVE90.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If your virtual environment is located one folder above `FIVE90`, activate it with:

```powershell
..\FIVE90.venv\Scripts\Activate.ps1
```

## First-time setup — macOS

```bash
python3 -m venv FIVE90.venv
source FIVE90.venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Start the complete game

```bash
python main.py
```

The normal flow is:

1. Enter two names.
2. Draft five players each.
3. Review both teams.
4. Select **Play Match**.
5. Watch the Plotly replay in the browser.
6. Return to the terminal and press Enter.
7. Use the full-time screen to choose Rematch, New Draft, or Exit.

## Useful test modes

Skip manual drafting and create two valid teams automatically:

```bash
python main.py --demo --seed 90
```

Use the terminal instead of graphical draft and result windows:

```bash
python main.py --console
```

Validate the player database:

```bash
python data_manager.py
```

Test the match simulator:

```bash
python match.py
```

Run all automated tests:

```bash
python -m unittest discover -s tests -v
```

## Important sound note

FIVE90 does **not** require `pygame`. The "Ankara Messi" MP3 is embedded into the replay page and plays only when a goal frame appears, keeping the sound synchronized on Windows and macOS without a separate audio process.

## Team responsibilities

- **Roshni:** player data validation, testing checklist, documentation support
- **Prasiddha:** name entry, draft selection, completed-team and full-time interfaces
- **Binisha:** Plotly pitch, player circles, ball movement, events, overlays, and sound assets
- **Apurva:** dynamic cards, match calculations, integration, debugging, and final testing
