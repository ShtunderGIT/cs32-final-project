import random
import requests
import math
from PIL import Image
from io import BytesIO

# USGS Imagery tile server
TILE_URL = "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile"


def generate_random_coordinate():
    # Generate random coordinates within the United States
    latitude = random.uniform(25, 49)
    longitude = random.uniform(-125, -66)
    return latitude, longitude


def latlon_to_tile(lat, lon, zoom):
    # Convert latitude/longitude to tile x,y coordinates
    lat_rad = math.radians(lat)
    n = 2 ** zoom

    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)

    return x, y


def build_tile_url(lat, lon, zoom=15):
    # Build a tile URL for USGS imagery
    x, y = latlon_to_tile(lat, lon, zoom)
    return f"{TILE_URL}/{zoom}/{y}/{x}"


def get_combined_image(lat, lon, zoom=15):
    # Download a 3x3 group of tiles and stitch them into one image
    x, y = latlon_to_tile(lat, lon, zoom)

    tile_size = 256
    combined = Image.new("RGB", (tile_size * 3, tile_size * 3))

    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            tile_url = f"{TILE_URL}/{zoom}/{y + dy}/{x + dx}"

            response = requests.get(tile_url)
            image = Image.open(BytesIO(response.content))

            paste_x = (dx + 1) * tile_size
            paste_y = (dy + 1) * tile_size

            combined.paste(image, (paste_x, paste_y))

    return combined


def get_random_location():
    lat, lon = generate_random_coordinate()
    image_url = build_tile_url(lat, lon)

    return {
        "latitude": lat,
        "longitude": lon,
        "image_url": image_url
    }


def main():
    print("Generating random US location...\n")

    try:
        location = get_random_location()

        print("Location:")
        print(f"Latitude:  {location['latitude']}")
        print(f"Longitude: {location['longitude']}")

        print("\nDownloading image...")

        image = get_combined_image(location["latitude"], location["longitude"], zoom=15)

        file_path = "images/test_image.jpg"
        image.save(file_path)

        print(f"Image saved to {file_path}")

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()
