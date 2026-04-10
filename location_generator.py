import os
import random
import requests
from PIL import Image
from io import BytesIO

MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")

MAPBOX_BASE_URL = "https://api.mapbox.com/styles/v1/mapbox"
SATELLITE_STYLE = "satellite-v9"


def generate_random_coordinate():
    # We generate random latitude and longitude.
    # We avoid the polar regions because they are less useful for gameplay.
    latitude = random.uniform(-70, 70)
    longitude = random.uniform(-180, 180)
    return latitude, longitude


def build_mapbox_image_url(latitude, longitude):
    # Mapbox Static Images API uses:
    # /styles/v1/{username}/{style_id}/static/{lon},{lat},{zoom}/{width}x{height}
    zoom = 10
    width = 512
    height = 512

    return (
        f"{MAPBOX_BASE_URL}/{SATELLITE_STYLE}/static/"
        f"{longitude},{latitude},{zoom}/{width}x{height}"
        f"?access_token={MAPBOX_TOKEN}"
    )


def get_random_location():
    latitude, longitude = generate_random_coordinate()
    image_url = build_mapbox_image_url(latitude, longitude)

    return {
        "latitude": latitude,
        "longitude": longitude,
        "image_url": image_url
    }


def main():
    print("Generating random location...\n")

    if not MAPBOX_TOKEN:
        print("Error: MAPBOX_TOKEN is not set.")
        return

    try:
        location = get_random_location()

        print("Location:")
        print(f"Latitude:  {location['latitude']}")
        print(f"Longitude: {location['longitude']}")

        image_url = location["image_url"]

        print("\nDownloading image...")

        response = requests.get(image_url, timeout=20)

        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))

            file_path = "images/test_image.png"
            image.save(file_path)

            print(f"Image saved to {file_path}")
        else:
            print("Failed to download image.")
            print(f"Status code: {response.status_code}")
            print(response.text)

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()
