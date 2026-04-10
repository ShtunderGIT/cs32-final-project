import random
import requests
import math
from PIL import Image
from io import BytesIO

# USGS Imagery tile server
TILE_URL = "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile"


def generate_random_coordinate():

    #Generate random coordinates within the United States.

    latitude = random.uniform(25, 49)      # US latitude range
    longitude = random.uniform(-125, -66)  # US longitude range
    return latitude, longitude


def latlon_to_tile(lat, lon, zoom):

    #Convert latitude/longitude to tile x,y coordinates.

    lat_rad = math.radians(lat)
    n = 2 ** zoom

    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)

    return x, y


def build_tile_url(lat, lon, zoom=12):
    #Build a tile URL for USGS imagery.

    x, y = latlon_to_tile(lat, lon, zoom)
    return f"{TILE_URL}/{zoom}/{y}/{x}"


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

        response = requests.get(location["image_url"])

        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))

            file_path = "images/test_image.jpg"
            image.save(file_path)

            print(f"Image saved to {file_path}")
        else:
            print("Failed to download image.")

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()
