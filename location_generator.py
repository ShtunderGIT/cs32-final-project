import os
import random
import requests
import math
from PIL import Image
from io import BytesIO

TILE_URL = "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile"


def generate_random_coordinate():
    latitude = random.uniform(25, 49)
    longitude = random.uniform(-125, -66)
    return latitude, longitude


def latlon_to_tile(lat, lon, zoom):
    lat_rad = math.radians(lat)
    n = 2 ** zoom

    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)

    return x, y


def build_tile_url(lat, lon, zoom=15):
    x, y = latlon_to_tile(lat, lon, zoom)
    return f"{TILE_URL}/{zoom}/{y}/{x}"


def get_combined_image(lat, lon, zoom=15):
    x, y = latlon_to_tile(lat, lon, zoom)

    tile_size = 256
    combined = Image.new("RGB", (tile_size * 3, tile_size * 3))
    success_count = 0

    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            tile_url = f"{TILE_URL}/{zoom}/{y + dy}/{x + dx}"

            try:
                response = requests.get(tile_url, timeout=8)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content)).convert("RGB")
                success_count += 1
            except Exception:
                image = Image.new("RGB", (256, 256), (40, 40, 40))

            paste_x = (dx + 1) * tile_size
            paste_y = (dy + 1) * tile_size
            combined.paste(image, (paste_x, paste_y))

    return combined, success_count


def is_too_dark(image, darkness_threshold=18, max_dark_fraction=0.35):
    rgb = image.convert("RGB")
    pixels = rgb.load()
    width, height = rgb.size

    step_x = max(1, width // 120)
    step_y = max(1, height // 120)

    dark_pixels = 0
    sampled = 0

    for x in range(0, width, step_x):
        for y in range(0, height, step_y):
            r, g, b = pixels[x, y]
            if r <= darkness_threshold and g <= darkness_threshold and b <= darkness_threshold:
                dark_pixels += 1
            sampled += 1

    if sampled == 0:
        return True

    return (dark_pixels / sampled) > max_dark_fraction


def get_random_location():
    lat, lon = generate_random_coordinate()
    image_url = build_tile_url(lat, lon)

    return {
        "latitude": lat,
        "longitude": lon,
        "image_url": image_url
    }


def get_valid_location_image(zoom=15, min_success_tiles=9, max_attempts=300):
    for _ in range(max_attempts):
        location = get_random_location()
        image, success_count = get_combined_image(
            location["latitude"],
            location["longitude"],
            zoom=zoom
        )

        if success_count < min_success_tiles:
            continue

        if is_too_dark(image):
            continue

        return {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "image_url": location["image_url"],
            "image": image
        }

    raise RuntimeError("Could not generate a valid satellite image after repeated attempts.")


def main():
    try:
        result = get_valid_location_image(zoom=15, min_success_tiles=9, max_attempts=300)

        print("Location:")
        print(f"Latitude:  {result['latitude']}")
        print(f"Longitude: {result['longitude']}")

        os.makedirs("images", exist_ok=True)
        file_path = "images/test_image.jpg"
        result["image"].save(file_path)

        print(f"Saved image to {file_path}")

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()