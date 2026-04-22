import os
import pygame

from location_generator import get_random_location, get_combined_image
from bot import get_bot_guess, distance_in_km


pygame.init()

WIDTH = 1200
HEIGHT = 800
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Satellite Geography Game")

FONT = pygame.font.SysFont(None, 32)
SMALL_FONT = pygame.font.SysFont(None, 26)
TITLE_FONT = pygame.font.SysFont(None, 42)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (220, 220, 220)
GRAY = (180, 180, 180)
DARK_GRAY = (80, 80, 80)
BLUE = (90, 140, 220)
GREEN = (60, 160, 90)
RED = (180, 70, 70)
YELLOW = (230, 210, 90)


class InputBox:
    def __init__(self, x, y, w, h, label, text=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.text = text
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_TAB:
                pass
            elif event.key == pygame.K_RETURN:
                pass
            else:
                if len(self.text) < 20:
                    self.text += event.unicode

    def draw(self, screen):
        label_surface = SMALL_FONT.render(self.label, True, WHITE)
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=6)
        pygame.draw.rect(screen, BLUE if self.active else BLACK, self.rect, 2, border_radius=6)

        text_surface = FONT.render(self.text, True, BLACK)
        screen.blit(label_surface, (self.rect.x, self.rect.y - 24))
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))


class Button:
    def __init__(self, x, y, w, h, text, color=BLUE):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8)

        text_surface = FONT.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class DifficultySelector:
    def __init__(self, x, y):
        self.options = ["easy", "medium", "hard", "insane"]
        self.selected = "medium"
        self.buttons = []

        start_x = x
        for i, option in enumerate(self.options):
            rect = pygame.Rect(start_x + i * 120, y, 100, 40)
            self.buttons.append((option, rect))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for option, rect in self.buttons:
                if rect.collidepoint(event.pos):
                    self.selected = option

    def draw(self, screen):
        label_surface = SMALL_FONT.render("Bot Difficulty", True, WHITE)
        screen.blit(label_surface, (self.buttons[0][1].x, self.buttons[0][1].y - 24))

        for option, rect in self.buttons:
            color = GREEN if option == self.selected else DARK_GRAY
            pygame.draw.rect(screen, color, rect, border_radius=8)
            pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)

            text_surface = SMALL_FONT.render(option, True, WHITE)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)


def load_round_image(path):
    image = pygame.image.load(path)
    return pygame.transform.scale(image, (600, 600))


def generate_round():
    location = get_random_location()
    true_lat = location["latitude"]
    true_lon = location["longitude"]

    image = get_combined_image(true_lat, true_lon, zoom=13)

    os.makedirs("images", exist_ok=True)
    image_path = "images/test_image.jpg"
    image.save(image_path)

    round_image = load_round_image(image_path)

    return {
        "true_lat": true_lat,
        "true_lon": true_lon,
        "image": round_image
    }


def safe_float(value):
    try:
        return float(value)
    except ValueError:
        return None


def validate_guess(lat_text, lon_text):
    lat = safe_float(lat_text)
    lon = safe_float(lon_text)

    if lat is None:
        return None, None, "Latitude must be a number."

    if lon is None:
        return None, None, "Longitude must be a number."

    if lat < -90 or lat > 90:
        return None, None, "Latitude must be between -90 and 90."

    if lon < -180 or lon > 180:
        return None, None, "Longitude must be between -180 and 180."

    if lon > 0:
        return None, None, "U.S. longitudes should be negative."

    return lat, lon, None


def compute_result(player_distance, bot_distance):
    if player_distance < bot_distance:
        margin = bot_distance - player_distance
        return "You WIN!", f"You beat the bot by {margin:.2f} km"
    if bot_distance < player_distance:
        margin = player_distance - bot_distance
        return "Bot WINS!", f"Bot beat you by {margin:.2f} km"
    return "It's a TIE!", "You and the bot were equally accurate."


def draw_text_lines(screen, lines, x, y, color=WHITE, font=SMALL_FONT, line_gap=28):
    for i, line in enumerate(lines):
        surface = font.render(line, True, color)
        screen.blit(surface, (x, y + i * line_gap))


def main():
    clock = pygame.time.Clock()
    running = True

    print("Starting UI...")
    round_data = generate_round()
    print("Round generated.")
    print("Entering game loop...")

    lat_box = InputBox(700, 180, 180, 45, "Latitude")
    lon_box = InputBox(920, 180, 180, 45, "Longitude")
    difficulty_selector = DifficultySelector(700, 90)
    submit_button = Button(700, 250, 180, 50, "Submit Guess", GREEN)
    new_round_button = Button(900, 250, 200, 50, "New Round", BLUE)

    status_message = "Enter your guess and press Submit."
    result_title = ""
    result_lines = []

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            lat_box.handle_event(event)
            lon_box.handle_event(event)
            difficulty_selector.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if submit_button.is_clicked(event.pos):
                    player_lat, player_lon, error_message = validate_guess(lat_box.text, lon_box.text)

                    if error_message:
                        status_message = error_message
                    else:
                        bot_guess = get_bot_guess(
                            round_data["true_lat"],
                            round_data["true_lon"],
                            difficulty_selector.selected
                        )

                        player_distance = distance_in_km(
                            round_data["true_lat"],
                            round_data["true_lon"],
                            player_lat,
                            player_lon
                        )

                        bot_distance = distance_in_km(
                            round_data["true_lat"],
                            round_data["true_lon"],
                            bot_guess["guess_latitude"],
                            bot_guess["guess_longitude"]
                        )

                        result_title, margin_line = compute_result(player_distance, bot_distance)

                        result_lines = [
                            f"Your guess: ({player_lat:.3f}, {player_lon:.3f})",
                            f"Your distance: {player_distance:.2f} km",
                            f"Bot guess: ({bot_guess['guess_latitude']:.3f}, {bot_guess['guess_longitude']:.3f})",
                            f"Bot distance: {bot_distance:.2f} km",
                            f"Bot difficulty: {bot_guess['difficulty']}",
                            f"Bot time: {bot_guess['time_taken']:.2f} sec (ignored for now)",
                            f"True location: ({round_data['true_lat']:.3f}, {round_data['true_lon']:.3f})",
                            margin_line
                        ]

                        status_message = "Round complete."

                if new_round_button.is_clicked(event.pos):
                    round_data = generate_round()
                    lat_box.text = ""
                    lon_box.text = ""
                    status_message = "New round generated."
                    result_title = ""
                    result_lines = []

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    player_lat, player_lon, error_message = validate_guess(lat_box.text, lon_box.text)

                    if error_message:
                        status_message = error_message

        SCREEN.fill((35, 40, 50))

        title_surface = TITLE_FONT.render("Satellite Geography Game", True, WHITE)
        SCREEN.blit(title_surface, (30, 20))

        subtitle_lines = [
            "Hint: U.S. latitudes are positive. U.S. longitudes are negative.",
            "Time exists in bot.py, but this UI ignores it for winner logic right now."
        ]
        draw_text_lines(SCREEN, subtitle_lines, 30, 70, color=LIGHT_GRAY)

        pygame.draw.rect(SCREEN, BLACK, (30, 130, 600, 600), 2)
        SCREEN.blit(round_data["image"], (30, 130))

        difficulty_selector.draw(SCREEN)
        lat_box.draw(SCREEN)
        lon_box.draw(SCREEN)
        submit_button.draw(SCREEN)
        new_round_button.draw(SCREEN)

        pygame.draw.rect(SCREEN, DARK_GRAY, (670, 330, 490, 400), border_radius=10)
        pygame.draw.rect(SCREEN, WHITE, (670, 330, 490, 400), 2, border_radius=10)

        result_header = TITLE_FONT.render("Results", True, WHITE)
        SCREEN.blit(result_header, (690, 350))

        if result_title:
            result_color = YELLOW if "TIE" in result_title else GREEN if "You WIN" in result_title else RED
            result_title_surface = FONT.render(result_title, True, result_color)
            SCREEN.blit(result_title_surface, (690, 395))

        draw_text_lines(SCREEN, result_lines, 690, 440, color=WHITE, font=SMALL_FONT, line_gap=30)

        status_surface = SMALL_FONT.render(status_message, True, LIGHT_GRAY)
        SCREEN.blit(status_surface, (690, 750))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
