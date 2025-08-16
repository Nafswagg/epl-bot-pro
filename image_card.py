from PIL import Image, ImageDraw, ImageFont
import os

def generate_standings_card(top_teams):
    """
    Generates an EPL top 6 standings card as a PNG image.

    Args:
        top_teams (list): List of dicts containing 'position', 'team', 'points'.
                          Each dict should have keys: 'position', 'team' {'name'}, 'points'

    Returns:
        str: Path to the generated PNG file
    """
    # Image size
    width, height = 800, 600
    background_color = (255, 255, 255)  # White background
    text_color = (0, 0, 0)  # Black text

    # Create image
    img = Image.new("RGB", (width, height), color=background_color)
    draw = ImageDraw.Draw(img)

    # Fonts (adjust path if needed)
    try:
        font_title = ImageFont.truetype("arial.ttf", 40)
        font_team = ImageFont.truetype("arial.ttf", 28)
    except:
        font_title = ImageFont.load_default()
        font_team = ImageFont.load_default()

    # Title
    draw.text((width//2 - 150, 20), "🏆 EPL TOP 6 🏆", fill=text_color, font=font_title)

    # Draw teams
    start_y = 100
    spacing = 70
    emojis = ["🥇", "🥈", "🥉", "4⃣", "5⃣", "6⃣"]

    for i, team in enumerate(top_teams):
        text = f"{emojis[i]} {team['position']}. {team['team']['name']} - {team['points']} pts"
        draw.text((50, start_y + i * spacing), text, fill=text_color, font=font_team)

    # Ensure output folder exists
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    # Save image
    path = os.path.join(output_dir, "standings_card.png")
    img.save(path)

    return path
