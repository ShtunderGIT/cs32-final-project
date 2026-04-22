import random
import math


def get_bot_guess(true_lat, true_lon, difficulty):
    # Returns a bot guess based on the true coordinates and difficulty
    # Harder difficulty = smaller error

    difficulty_settings = {
        "easy": 10.0,
        "medium": 4.0,
        "hard": 1.5,
        "insane": 0.3
    }

    if difficulty not in difficulty_settings:
        raise ValueError("Difficulty must be: easy, medium, hard, or insane")

    max_offset = difficulty_settings[difficulty]

    # Random offset added to true location
    lat_offset = random.uniform(-max_offset, max_offset)
    lon_offset = random.uniform(-max_offset, max_offset)

    guess_lat = true_lat + lat_offset
    guess_lon = true_lon + lon_offset

    # Keep values within valid coordinate bounds
    guess_lat = max(-90, min(90, guess_lat))
    guess_lon = max(-180, min(180, guess_lon))

    return {
        "guess_latitude": guess_lat,
        "guess_longitude": guess_lon,
        "difficulty": difficulty
    }


def distance_in_km(lat1, lon1, lat2, lon2):
    # Calculates distance between two coordinates using haversine formula

    r = 6371  # Earth radius in km

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return r * c


# Example test
if __name__ == "__main__":
    true_lat = 34.05
    true_lon = -118.25

    bot_guess = get_bot_guess(true_lat, true_lon, "medium")
    print("Bot guess:", bot_guess)

    error = distance_in_km(
        true_lat,
        true_lon,
        bot_guess["guess_latitude"],
        bot_guess["guess_longitude"]
    )

    print("Error (km):", error)
