import random
import math


def get_bot_guess(true_lat, true_lon, difficulty):
    # Bot settings for each difficulty
    settings = {
        "easy": {
            "min_mistake": 5.0,
            "max_mistake": 10.0,
            "min_time": 8,
            "max_time": 15
        },
        "medium": {
            "min_mistake": 2.0,
            "max_mistake": 5.0,
            "min_time": 5,
            "max_time": 10
        },
        "hard": {
            "min_mistake": 0.5,
            "max_mistake": 2.0,
            "min_time": 3,
            "max_time": 7
        },
        "insane": {
            "min_mistake": 0.1,
            "max_mistake": 0.5,
            "min_time": 1,
            "max_time": 3
        }
    }

    if difficulty not in settings:
        raise ValueError("Difficulty must be: easy, medium, hard, or insane")

    bot_settings = settings[difficulty]

    # Pick how wrong the bot will be
    mistake = random.uniform(bot_settings["min_mistake"], bot_settings["max_mistake"])

    # Randomly choose direction of mistake
    lat_offset = random.uniform(-mistake, mistake)
    lon_offset = random.uniform(-mistake, mistake)

    guess_lat = true_lat + lat_offset
    guess_lon = true_lon + lon_offset

    # Keep coordinates in valid bounds
    guess_lat = max(-90, min(90, guess_lat))
    guess_lon = max(-180, min(180, guess_lon))

    # Pick how long the bot "takes"
    guess_time = random.uniform(bot_settings["min_time"], bot_settings["max_time"])

    return {
        "guess_latitude": guess_lat,
        "guess_longitude": guess_lon,
        "difficulty": difficulty,
        "time_taken": round(guess_time, 2)
    }


def distance_in_km(lat1, lon1, lat2, lon2):
    # Haversine formula

    r = 6371

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
