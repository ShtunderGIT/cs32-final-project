import os

from location_generator import get_valid_location_image
from bot import get_bot_guess, distance_in_km


class SatelliteGame:
    def __init__(self):
        self.true_lat = None
        self.true_lon = None
        self.image_path = "images/test_image.jpg"

    def start_new_round(self):
        result = get_valid_location_image(zoom=13, min_success_tiles=9, max_attempts=300)

        self.true_lat = result["latitude"]
        self.true_lon = result["longitude"]

        os.makedirs("images", exist_ok=True)
        result["image"].save(self.image_path)

        return {
            "image_path": self.image_path,
            "true_lat": self.true_lat,
            "true_lon": self.true_lon
        }

    def validate_guess(self, lat_text, lon_text):
        try:
            lat = float(lat_text)
        except ValueError:
            return None, None, "Latitude must be a number."

        try:
            lon = float(lon_text)
        except ValueError:
            return None, None, "Longitude must be a number."

        if lat < -90 or lat > 90:
            return None, None, "Latitude must be between -90 and 90."

        if lon < -180 or lon > 180:
            return None, None, "Longitude must be between -180 and 180."

        if lon > 0:
            return None, None, "U.S. longitudes should be negative."

        return lat, lon, None

    def submit_guess(self, lat_text, lon_text, difficulty):
        player_lat, player_lon, error_message = self.validate_guess(lat_text, lon_text)

        if error_message:
            return {
                "success": False,
                "message": error_message
            }

        bot_guess = get_bot_guess(self.true_lat, self.true_lon, difficulty)

        player_distance = distance_in_km(
            self.true_lat, self.true_lon, player_lat, player_lon
        )

        bot_distance = distance_in_km(
            self.true_lat, self.true_lon,
            bot_guess["guess_latitude"], bot_guess["guess_longitude"]
        )

        if player_distance < bot_distance:
            winner = "You WIN!"
            margin_message = f"You beat the bot by {bot_distance - player_distance:.2f} km"
        elif bot_distance < player_distance:
            winner = "Bot WINS!"
            margin_message = f"Bot beat you by {player_distance - bot_distance:.2f} km"
        else:
            winner = "It's a TIE!"
            margin_message = "You and the bot were equally accurate."

        return {
            "success": True,
            "message": "Round complete.",
            "winner": winner,
            "player_guess": (player_lat, player_lon),
            "player_distance": player_distance,
            "bot_guess": (
                bot_guess["guess_latitude"],
                bot_guess["guess_longitude"]
            ),
            "bot_distance": bot_distance,
            "bot_difficulty": bot_guess["difficulty"],
            "true_location": (self.true_lat, self.true_lon),
            "margin_message": margin_message
        }