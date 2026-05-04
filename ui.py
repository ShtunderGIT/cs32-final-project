import os
import pygame
from app import SatelliteGame

pygame.init()

display_info = pygame.display.Info()
WIDTH = min(1850, display_info.current_w - 40)
HEIGHT = min(1100, display_info.current_h - 80)

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Satellite Geography Game")

FONT = pygame.font.SysFont(None, 28)
SMALL_FONT = pygame.font.SysFont(None, 22)
TITLE_FONT = pygame.font.SysFont(None, 38)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (70, 70, 70)
BLUE = (90, 140, 220)
GREEN = (65, 190, 95)
RED = (210, 75, 75)
YELLOW = (235, 205, 70)
BG = (28, 33, 45)
PANEL = (55, 60, 72)

MIN_LAT = 25
MAX_LAT = 49
MIN_LON = -125
MAX_LON = -66

OUTER_PAD = 24
TOP_BAR_Y = 24
CONTENT_TOP = 96
GAP = 18

LEFT_W = int(WIDTH * 0.53)
RIGHT_W = WIDTH - LEFT_W - OUTER_PAD * 2 - GAP

SAT_X = OUTER_PAD
SAT_Y = CONTENT_TOP
SAT_W = LEFT_W
SAT_H = HEIGHT - CONTENT_TOP - OUTER_PAD

RIGHT_X = SAT_X + SAT_W + GAP

MAP_PANEL_X = RIGHT_X
MAP_PANEL_Y = CONTENT_TOP
MAP_PANEL_W = RIGHT_W
MAP_PANEL_H = int(HEIGHT * 0.46)

LOWER_PANEL_X = RIGHT_X
LOWER_PANEL_Y = MAP_PANEL_Y + MAP_PANEL_H + GAP
LOWER_PANEL_W = RIGHT_W
LOWER_PANEL_H = HEIGHT - LOWER_PANEL_Y - OUTER_PAD

MAP_TITLE_H = 46
MAP_HINT_H = 34
MAP_INNER_PAD = 14

MAP_IMAGE_X = 0
MAP_IMAGE_Y = 0
MAP_IMAGE_W = 0
MAP_IMAGE_H = 0

PLAYBOX_LEFT = 0.093
PLAYBOX_RIGHT = 0.919
PLAYBOX_TOP = 0.229
PLAYBOX_BOTTOM = 0.773

CLICK_COOLDOWN_MS = 220


class Button:
    def __init__(self, x, y, w, h, text, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color

    def draw(self, screen, enabled=True):
        color = self.color if enabled else DARK_GRAY
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8)
        text_surface = FONT.render(self.text, True, WHITE)
        screen.blit(text_surface, text_surface.get_rect(center=self.rect.center))

    def is_clicked(self, pos, enabled=True):
        return enabled and self.rect.collidepoint(pos)


class DifficultySelector:
    def __init__(self, x, y, available_width):
        self.options = ["easy", "medium", "hard", "insane"]
        self.selected = "medium"
        self.buttons = []

        gap = 10
        btn_w = (available_width - gap * 3) // 4
        btn_h = 40

        for i, option in enumerate(self.options):
            rect = pygame.Rect(x + i * (btn_w + gap), y, btn_w, btn_h)
            self.buttons.append((option, rect))

    def handle_event(self, event, locked=False):
        if locked:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for option, rect in self.buttons:
                if rect.collidepoint(event.pos):
                    self.selected = option

    def draw(self, screen):
        label_surface = SMALL_FONT.render("Bot Difficulty", True, WHITE)
        label_y = self.buttons[0][1].y - 24
        screen.blit(label_surface, (self.buttons[0][1].x, label_y))

        for option, rect in self.buttons:
            color = GREEN if option == self.selected else DARK_GRAY
            pygame.draw.rect(screen, color, rect, border_radius=6)
            pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)

            text_surface = SMALL_FONT.render(option, True, WHITE)
            screen.blit(text_surface, text_surface.get_rect(center=rect.center))


def load_satellite_image(path):
    if not os.path.exists(path):
        return None

    try:
        image = pygame.image.load(path).convert()
        return pygame.transform.smoothscale(image, (SAT_W, SAT_H))
    except pygame.error:
        return None


def fit_inside_box(image, max_width, max_height):
    original_width = image.get_width()
    original_height = image.get_height()

    scale = min(max_width / original_width, max_height / original_height)
    new_width = max(1, int(original_width * scale))
    new_height = max(1, int(original_height * scale))

    return pygame.transform.smoothscale(image, (new_width, new_height))


def load_region_map():
    base = os.path.dirname(os.path.abspath(__file__))
    possible_files = [
        os.path.join(base, "images", "game_region_map.png"),
        os.path.join(base, "images", "satellite_game_region_map.png"),
        os.path.join(base, "images", "playable_region_map.png"),
        os.path.join(base, "images", "us_reference_map.png"),
        os.path.join(base, "images", "us_reference_map.jpg"),
    ]

    max_w = MAP_PANEL_W - MAP_INNER_PAD * 2
    max_h = MAP_PANEL_H - MAP_TITLE_H - MAP_HINT_H - MAP_INNER_PAD * 2

    for path in possible_files:
        if os.path.exists(path):
            try:
                image = pygame.image.load(path).convert()
                return fit_inside_box(image, max_w, max_h)
            except pygame.error:
                return None

    return None


def draw_lines(screen, lines, x, y, color=WHITE, gap=20):
    for i, line in enumerate(lines):
        surface = SMALL_FONT.render(line, True, color)
        screen.blit(surface, (x, y + i * gap))


def clamp(value, low, high):
    return max(low, min(high, value))


def get_playbox_rect():
    if MAP_IMAGE_W <= 0 or MAP_IMAGE_H <= 0:
        return pygame.Rect(0, 0, 0, 0)

    left = MAP_IMAGE_X + int(MAP_IMAGE_W * PLAYBOX_LEFT)
    right = MAP_IMAGE_X + int(MAP_IMAGE_W * PLAYBOX_RIGHT)
    top = MAP_IMAGE_Y + int(MAP_IMAGE_H * PLAYBOX_TOP)
    bottom = MAP_IMAGE_Y + int(MAP_IMAGE_H * PLAYBOX_BOTTOM)

    return pygame.Rect(left, top, right - left, bottom - top)


def latlon_to_map_xy(lat, lon):
    playbox = get_playbox_rect()

    lon = clamp(lon, MIN_LON, MAX_LON)
    lat = clamp(lat, MIN_LAT, MAX_LAT)

    x_ratio = (lon - MIN_LON) / (MAX_LON - MIN_LON)
    y_ratio = (MAX_LAT - lat) / (MAX_LAT - MIN_LAT)

    x = playbox.left + int(x_ratio * playbox.width)
    y = playbox.top + int(y_ratio * playbox.height)
    return x, y


def map_xy_to_latlon(x, y):
    playbox = get_playbox_rect()

    x = clamp(x, playbox.left, playbox.right)
    y = clamp(y, playbox.top, playbox.bottom)

    x_ratio = (x - playbox.left) / playbox.width
    y_ratio = (y - playbox.top) / playbox.height

    lon = MIN_LON + x_ratio * (MAX_LON - MIN_LON)
    lat = MAX_LAT - y_ratio * (MAX_LAT - MIN_LAT)

    return lat, lon


def draw_marker(screen, lat, lon, color, label_text=None):
    x, y = latlon_to_map_xy(lat, lon)

    pygame.draw.circle(screen, BLACK, (x, y), 10)
    pygame.draw.circle(screen, color, (x, y), 7)
    pygame.draw.circle(screen, WHITE, (x, y), 2)

    if label_text:
        label_surface = SMALL_FONT.render(label_text, True, WHITE)
        screen.blit(label_surface, (x + 10, y - 10))


def draw_satellite_panel(screen, satellite_image):
    if satellite_image:
        screen.blit(satellite_image, (SAT_X, SAT_Y))
        pygame.draw.rect(screen, BLACK, (SAT_X, SAT_Y, SAT_W, SAT_H), 2)
    else:
        placeholder = pygame.Rect(SAT_X, SAT_Y, SAT_W, SAT_H)
        pygame.draw.rect(screen, PANEL, placeholder, border_radius=12)
        pygame.draw.rect(screen, WHITE, placeholder, 2, border_radius=12)
        draw_lines(
            screen,
            [
                "Satellite image unavailable.",
                "Press NEXT ROUND to retry.",
            ],
            SAT_X + 24,
            SAT_Y + 36,
            color=LIGHT_GRAY
        )


def draw_region_panel(screen, region_map, click_hint, selected_guess, result, round_locked):
    global MAP_IMAGE_X, MAP_IMAGE_Y, MAP_IMAGE_W, MAP_IMAGE_H

    panel_rect = pygame.Rect(MAP_PANEL_X, MAP_PANEL_Y, MAP_PANEL_W, MAP_PANEL_H)
    pygame.draw.rect(screen, PANEL, panel_rect, border_radius=12)
    pygame.draw.rect(screen, WHITE, panel_rect, 2, border_radius=12)

    title = TITLE_FONT.render("Playable Region Map", True, WHITE)
    screen.blit(title, (MAP_PANEL_X + 16, MAP_PANEL_Y + 8))

    hint_text = SMALL_FONT.render(click_hint, True, LIGHT_GRAY)
    screen.blit(hint_text, (MAP_PANEL_X + 16, MAP_PANEL_Y + 40))

    if region_map:
        MAP_IMAGE_W = region_map.get_width()
        MAP_IMAGE_H = region_map.get_height()

        MAP_IMAGE_X = MAP_PANEL_X + (MAP_PANEL_W - MAP_IMAGE_W) // 2
        MAP_IMAGE_Y = MAP_PANEL_Y + MAP_TITLE_H + 4

        screen.blit(region_map, (MAP_IMAGE_X, MAP_IMAGE_Y))
        pygame.draw.rect(screen, LIGHT_GRAY, (MAP_IMAGE_X, MAP_IMAGE_Y, MAP_IMAGE_W, MAP_IMAGE_H), 2)

        playbox = get_playbox_rect()
        pygame.draw.rect(screen, YELLOW, playbox, 2)

        if selected_guess and not result:
            draw_marker(screen, selected_guess[0], selected_guess[1], GREEN, "Your guess")

        if result and result["success"]:
            player_lat, player_lon = result["player_guess"]
            bot_lat, bot_lon = result["bot_guess"]
            true_lat, true_lon = result["true_location"]

            draw_marker(screen, player_lat, player_lon, GREEN, "You")
            draw_marker(screen, bot_lat, bot_lon, RED, "Bot")
            draw_marker(screen, true_lat, true_lon, YELLOW, "True")

        if round_locked:
            overlay = pygame.Surface((MAP_PANEL_W, MAP_PANEL_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 20))
            screen.blit(overlay, (MAP_PANEL_X, MAP_PANEL_Y))
    else:
        MAP_IMAGE_W = 0
        MAP_IMAGE_H = 0
        draw_lines(
            screen,
            [
                "Region map not found.",
                "Save your map into images/ as:",
                "game_region_map.png",
            ],
            MAP_PANEL_X + 16,
            MAP_PANEL_Y + 90,
            color=LIGHT_GRAY
        )


def draw_scoreboard(screen, wins, bot_wins, ties, rounds_played):
    text = f"Wins: {wins}   Bot Wins: {bot_wins}   Ties: {ties}   Rounds: {rounds_played}"
    surface = SMALL_FONT.render(text, True, LIGHT_GRAY)
    screen.blit(surface, (OUTER_PAD, TOP_BAR_Y + 50))


def draw_result_block(screen, result, x, y):
    if not result or not result["success"]:
        return

    player_lat, player_lon = result["player_guess"]
    bot_lat, bot_lon = result["bot_guess"]
    true_lat, true_lon = result["true_location"]

    player_dist = result["player_distance"]
    bot_dist = result["bot_distance"]
    margin = abs(player_dist - bot_dist)

    if "You WIN" in result["winner"]:
        headline = "YOU WIN THIS ROUND"
        color = GREEN
    elif "Bot WINS" in result["winner"]:
        headline = "BOT WINS THIS ROUND"
        color = RED
    else:
        headline = "THIS ROUND IS A TIE"
        color = YELLOW

    screen.blit(TITLE_FONT.render(headline, True, color), (x, y))

    lines = [
        f"You clicked: ({player_lat:.4f}, {player_lon:.4f})",
        f"Bot chose: ({bot_lat:.4f}, {bot_lon:.4f})",
        f"Real location: ({true_lat:.4f}, {true_lon:.4f})",
        f"Your distance: {player_dist:.2f} km",
        f"Bot distance: {bot_dist:.2f} km",
        f"Difference: {margin:.2f} km",
    ]
    draw_lines(screen, lines, x, y + 48, gap=20)


def draw_lower_panel(
    screen,
    difficulty,
    next_round_btn,
    result,
    selected_guess,
):
    panel_rect = pygame.Rect(LOWER_PANEL_X, LOWER_PANEL_Y, LOWER_PANEL_W, LOWER_PANEL_H)
    pygame.draw.rect(screen, PANEL, panel_rect, border_radius=12)
    pygame.draw.rect(screen, WHITE, panel_rect, 2, border_radius=12)

    col_left = LOWER_PANEL_X + 18

    difficulty.draw(screen)
    next_round_btn.draw(screen, enabled=True)

    divider_y = LOWER_PANEL_Y + 118
    pygame.draw.line(screen, DARK_GRAY, (col_left, divider_y), (LOWER_PANEL_X + LOWER_PANEL_W - 18, divider_y), 2)

    title_surface = TITLE_FONT.render("Round Result", True, WHITE)
    screen.blit(title_surface, (col_left, divider_y + 6))

    if result and result["success"]:
        draw_result_block(screen, result, col_left, divider_y + 44)
    else:
        preview_lines = [
            "Click inside the yellow box on the map",
            "to submit your guess instantly.",
        ]

        if selected_guess:
            preview_lines.extend(
                [
                    f"Selected latitude: {selected_guess[0]:.4f}",
                    f"Selected longitude: {selected_guess[1]:.4f}",
                ]
            )

        draw_lines(screen, preview_lines, col_left, divider_y + 50, color=LIGHT_GRAY, gap=20)


def start_new_round(game):
    round_data = game.start_new_round()
    satellite_image = load_satellite_image(round_data["image_path"])
    return round_data, satellite_image


def main():
    clock = pygame.time.Clock()
    running = True

    game = SatelliteGame()
    round_data, satellite_image = start_new_round(game)
    region_map = load_region_map()

    difficulty = DifficultySelector(LOWER_PANEL_X + 18, LOWER_PANEL_Y + 20, LOWER_PANEL_W - 36)

    next_round_btn = Button(
        LOWER_PANEL_X + 18,
        LOWER_PANEL_Y + 60,
        LOWER_PANEL_W - 36,
        48,
        "NEXT ROUND",
        BLUE
    )

    result = None
    selected_guess = None
    click_hint = "Click inside the yellow rectangle to submit your guess instantly."
    round_locked = False

    wins = 0
    bot_wins = 0
    ties = 0
    rounds_played = 0

    last_click_time = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            difficulty.handle_event(event, locked=round_locked)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                now = pygame.time.get_ticks()
                if now - last_click_time < CLICK_COOLDOWN_MS:
                    continue
                last_click_time = now

                if next_round_btn.is_clicked(event.pos, enabled=True):
                    round_data, satellite_image = start_new_round(game)
                    region_map = load_region_map()
                    result = None
                    selected_guess = None
                    round_locked = False
                    click_hint = "Click inside the yellow rectangle to submit your guess instantly."
                    continue

                if not round_locked:
                    playbox = get_playbox_rect()
                    if playbox.width > 0 and playbox.collidepoint(event.pos):
                        lat, lon = map_xy_to_latlon(event.pos[0], event.pos[1])
                        selected_guess = (lat, lon)

                        result = game.submit_guess(
                            f"{lat:.4f}",
                            f"{lon:.4f}",
                            difficulty.selected
                        )

                        if result["success"]:
                            round_locked = True
                            rounds_played += 1
                            click_hint = "Round complete. Press NEXT ROUND to continue."

                            if "You WIN" in result["winner"]:
                                wins += 1
                            elif "Bot WINS" in result["winner"]:
                                bot_wins += 1
                            else:
                                ties += 1

        SCREEN.fill(BG)

        title_surface = TITLE_FONT.render("Satellite Game", True, WHITE)
        SCREEN.blit(title_surface, (OUTER_PAD, TOP_BAR_Y))
        draw_scoreboard(SCREEN, wins, bot_wins, ties, rounds_played)

        draw_satellite_panel(SCREEN, satellite_image)
        draw_region_panel(SCREEN, region_map, click_hint, selected_guess, result, round_locked)
        draw_lower_panel(
            SCREEN,
            difficulty,
            next_round_btn,
            result,
            selected_guess,
        )

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()