from collections import deque
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


# --------------------------------------------------
# 1. PROJECT FOLDER LOCATIONS
# --------------------------------------------------

BASE_DIR = Path(__file__).parent

CSV_PATH = BASE_DIR / "data" / "players.csv"
TEMPLATE_FOLDER = BASE_DIR / "Templates"
IMAGE_FOLDER = BASE_DIR / "PlayerImages"
OUTPUT_FOLDER = BASE_DIR / "GeneratedCards"

OUTPUT_FOLDER.mkdir(exist_ok=True)


# --------------------------------------------------
# 2. PLAYER IMAGE FILENAMES
# --------------------------------------------------

IMAGE_NAMES = {
    "Thibaut Courtois": "Thibaut_Courtois.png",
    "Alisson": "Alisson.png",
    "Ederson": "Ederson.png",
    "Manuel Neuer": "Manuel_Neuer.png",
    "Virgil van Dijk": "Van_dijk.png",
    "Antonio Rudiger": "Rudiger.png",
    "William Saliba": "Saliba.png",
    "Ruben Dias": "Ruben_Dias.png",
    "Achraf Hakimi": "Hakimi.png",
    "Rodri": "Rodri.png",
    "Jude Bellingham": "Bellingham.png",
    "Kevin De Bruyne": "Kevin_De_Bruyne.png",
    "Pedri": "Pedri.png",
    "Federico Valverde": "Valverde.png",
    "Declan Rice": "Declan_Rice.png",
    "Martin Odegaard": "Odegaard.png",
    "Bernardo Silva": "Bernardo_Silva.png",
    "Bruno Fernandes": "Bruno_Fernandes.png",
    "Toni Kroos": "Toni_Kroos.png",
    "Vinicius Jr": "Vini_jr.png",
    "Mohamed Salah": "Salah.png",
    "Kylian Mbappe": "Mbappe.png",
    "Erling Haaland": "Haaland.png",
    "Harry Kane": "Harry_Kane.png",
    "Cristiano Ronaldo": "Ronaldo.png",
    "Lionel Messi": "Messi.png",
    "Neymar Jr": "Neymar.png",
}


# --------------------------------------------------
# 3. FONT HELPER
# --------------------------------------------------

def get_font(size, bold=False):
    """Find a usable regular or bold font on Windows or Mac."""

    if bold:
        possible_fonts = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
    else:
        possible_fonts = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]

    for font_path in possible_fonts:
        if Path(font_path).exists():
            return ImageFont.truetype(font_path, size)

    return ImageFont.load_default()


# --------------------------------------------------
# 4. CHECKERBOARD BACKGROUND REMOVAL
# --------------------------------------------------

def remove_checkerboard_background(image):
    """Remove a connected grey-and-white checkerboard background."""

    image = image.convert("RGBA")
    pixels = image.load()
    width, height = image.size

    visited = set()
    queue = deque()

    # Start checking from all four image edges.
    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))

    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    def looks_like_checkerboard(pixel):
        red, green, blue, alpha = pixel

        brightness = (red + green + blue) / 3
        colour_difference = max(red, green, blue) - min(
            red,
            green,
            blue,
        )

        return alpha == 0 or (
            brightness > 140
            and colour_difference < 25
        )

    while queue:
        x, y = queue.popleft()

        if (x, y) in visited:
            continue

        if x < 0 or x >= width or y < 0 or y >= height:
            continue

        visited.add((x, y))

        if not looks_like_checkerboard(pixels[x, y]):
            continue

        red, green, blue, _ = pixels[x, y]
        pixels[x, y] = (red, green, blue, 0)

        queue.append((x + 1, y))
        queue.append((x - 1, y))
        queue.append((x, y + 1))
        queue.append((x, y - 1))

    # Remove empty transparent space around the player.
    visible_area = image.getbbox()

    if visible_area:
        image = image.crop(visible_area)

    return image


# --------------------------------------------------
# 5. GENERATE ONE PLAYER CARD
# --------------------------------------------------

def generate_player_card(player):
    """Create and save one player card."""

    player_name = str(player["name"])
    position = str(player["position"]).upper()
    overall = int(player["overall"])

    # Choose the correct template.
    if position == "GK":
        template_path = TEMPLATE_FOLDER / "KeeperCard.png"
    else:
        template_path = TEMPLATE_FOLDER / "OutfieldCard.png"

    if not template_path.exists():
        raise FileNotFoundError(
            f"Card template was not found: {template_path}"
        )

    # Find the player image filename.
    if player_name not in IMAGE_NAMES:
        raise KeyError(
            f"No image filename was added for {player_name}"
        )

    player_image_path = IMAGE_FOLDER / IMAGE_NAMES[player_name]

    if not player_image_path.exists():
        raise FileNotFoundError(
            f"Player image was not found: {player_image_path}"
        )

    # Open the template and player image.
    card = Image.open(template_path).convert("RGBA")
    player_image = Image.open(player_image_path).convert("RGBA")

    # Remove any fake checkerboard background.
    player_image = remove_checkerboard_background(player_image)

    # Resize the player while keeping the correct proportions.
    player_image.thumbnail(
        (
            int(card.width * 0.62),
            int(card.height * 0.48),
        ),
        Image.Resampling.LANCZOS,
    )

    # Place the player near the centre.
    image_x = (card.width - player_image.width) // 2
    image_y = int(card.height * 0.19)

    card.alpha_composite(
        player_image,
        (image_x, image_y),
    )

    draw = ImageDraw.Draw(card)

    # Create bold fonts.
    overall_font = get_font(
        max(24, int(card.width * 0.075)),
        bold=True,
    )

    position_font = get_font(
        max(20, int(card.width * 0.055)),
        bold=True,
    )

    name_font = get_font(
        max(20, int(card.width * 0.050)),
        bold=True,
    )

    stat_label_font = get_font(
        max(18, int(card.width * 0.037)),
        bold=True,
    )

    stat_value_font = get_font(
        max(18, int(card.width * 0.035)),
        bold=True,
    )

    white = (255, 255, 255, 255)

    # Align the overall rating directly below the position.
    overall_x = int(card.width * (0.205 if position == "GK" else 0.18))
    overall_y = int(card.height * 0.32)

    draw.text(
        (overall_x, overall_y),
        str(overall),
        fill=white,
        font=overall_font,
        anchor="mm",
        stroke_width=2,
        stroke_fill="black",
    )

    # KeeperCard.png already contains GK.
    # Only draw the position for outfield players.
    if position != "GK":
        draw.text(
            (
                int(card.width * 0.18),
                int(card.height * 0.26),
            ),
            position,
            fill=white,
            font=position_font,
            anchor="mm",
            stroke_width=2,
            stroke_fill="black",
        )

    # Draw the player's name.
    draw.text(
        (
            card.width // 2,
            int(card.height * 0.685),
        ),
        player_name,
        fill=white,
        font=name_font,
        anchor="mm",
        stroke_width=2,
        stroke_fill="black",
    )

    # Choose the correct statistics.
    if position == "GK":
        statistics = [
            ("DIV", "diving"),
            ("HAN", "handling"),
            ("KIC", "kicking"),
            ("REF", "reflexes"),
            ("SPD", "speed"),
            ("POS", "positioning"),
        ]
    else:
        statistics = [
            ("PAC", "pace"),
            ("SHO", "shooting"),
            ("PAS", "passing"),
            ("DRI", "dribbling"),
            ("DEF", "defending"),
            ("PHY", "physical"),
        ]

    # Create a clean dark panel over the template's old labels.
    statistics_panel = Image.new(
        "RGBA",
        card.size,
        (0, 0, 0, 0),
    )

    panel_draw = ImageDraw.Draw(statistics_panel)

    panel_draw.rounded_rectangle(
        (
            int(card.width * 0.09),
            int(card.height * 0.715),
            int(card.width * 0.91),
            int(card.height * 0.835),
        ),
        radius=25,
        fill=(2, 38, 34, 245),
        outline=(26, 185, 133, 180),
        width=2,
    )

    card = Image.alpha_composite(
        card,
        statistics_panel,
    )

    draw = ImageDraw.Draw(card)

    # All labels and values use the same horizontal centres.
    start_x = int(card.width * 0.16)
    end_x = int(card.width * 0.84)
    spacing = (end_x - start_x) / 5

    label_y = int(card.height * 0.755)
    value_y = int(card.height * 0.805)

    for index, (label, column) in enumerate(statistics):
        x = int(start_x + index * spacing)
        value = int(player[column])

        # Attribute label, such as PAC or DIV.
        draw.text(
            (x, label_y),
            label,
            fill=white,
            font=stat_label_font,
            anchor="mm",
            stroke_width=1,
            stroke_fill="black",
        )

        # Attribute rating directly below its label.
        draw.text(
            (x, value_y),
            str(value),
            fill=white,
            font=stat_value_font,
            anchor="mm",
            stroke_width=1,
            stroke_fill="black",
        )

    # Create a safe filename.
    safe_name = player_name.replace(" ", "_")

    output_path = (
        OUTPUT_FOLDER / f"{safe_name}_Card.png"
    )

    # Save the completed card.
    card.save(output_path)

    print(f"Card created: {output_path.name}")

    return output_path


# --------------------------------------------------
# 6. GENERATE CARDS FOR A COMPLETE TEAM
# --------------------------------------------------

def generate_team_cards(team):
    """Generate cards for all players in one team."""

    generated_paths = []

    for player in team:
        card_path = generate_player_card(player)
        generated_paths.append(card_path)

    return generated_paths


# --------------------------------------------------
# 7. TEMPORARY TEST
# --------------------------------------------------

if __name__ == "__main__":
    players = pd.read_csv(CSV_PATH)

    # Select the first goalkeeper.
    goalkeeper = players[
        players["position"] == "GK"
    ].iloc[0]

    # Select the first outfield player.
    outfield_player = players[
        players["position"] != "GK"
    ].iloc[0]

    print("Creating a goalkeeper card...")
    goalkeeper_card = generate_player_card(goalkeeper)

    print("Creating an outfield-player card...")
    outfield_card = generate_player_card(outfield_player)

    print()
    print("Testing finished successfully.")
    print("Goalkeeper card:", goalkeeper_card)
    print("Outfield card:", outfield_card)
