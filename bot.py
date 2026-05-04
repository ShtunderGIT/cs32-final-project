import random
import math


def get_bot_guess(true_lat, true_lon, difficulty):
    settings = {
        "easy": {
            "min_mistake": 7.0,
            "max_mistake": 13.0
        },
        "medium": {
            "min_mistake": 3.0,
            "max_mistake": 6.5
        },
        "hard": {
            "min_mistake": 1.0,
            "max_mistake": 3.0
        },
        "insane": {
            "min_mistake": 0.1,
            "max_mistake": 0.5
        }
    }

    if difficulty not in settings:
        raise ValueError("Difficulty must be: easy, medium, hard, or insane")

    bot_settings = settings[difficulty]

    mistake = random.uniform(bot_settings["min_mistake"], bot_settings["max_mistake"])

    lat_offset = random.uniform(-mistake, mistake)
    lon_offset = random.uniform(-mistake, mistake)

    guess_lat = true_lat + lat_offset
    guess_lon = true_lon + lon_offset

    guess_lat = max(-90, min(90, guess_lat))
    guess_lon = max(-180, min(180, guess_lon))

    return {
        "guess_latitude": guess_lat,
        "guess_longitude": guess_lon,
        "difficulty": difficulty
    }


def distance_in_km(lat1, lon1, lat2, lon2):
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