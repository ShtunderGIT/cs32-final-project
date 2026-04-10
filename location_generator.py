import random
import requests
from datetime import date, timedelta
from PIL import Image
from io import BytesIO

GIBS_WMS_URL = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"

DEFAULT_LAYER = "MODIS_Terra_CorrectedReflectance_TrueColor"

def generate_random_coordinate():
    # we generate random latitude and longitude
    # We won't do (-90,90) for latitude, because that's the coordinates of the poles
    # and after +- 70 we get distortion of satelite imagery
    latitude = random.uniform(-70, 70)
    longitude = random.uniform(-180, 180)
    return latitude, longitude

def build_boundary(latitude, longitude):
    # Build a square boundary around the center point
    boundary_size = 1.0

    min_lat = max(-90, latitude - boundary_size)
    max_lat = min(90, latitude + boundary_size)
    min_lon = max(-180, longitude - boundary_size)
    max_lon = min(180, longitude + boundary_size)

    return f"{min_lon},{min_lat},{max_lon},{max_lat}"

def build_gibs_image_url(latitude, longitude):
    boundary_box = build_boundary(latitude, longitude)
    image_date = (date.today() - timedelta(days=7)).isoformat()

    params = {
        "SERVICE": "WMS",
        "REQUEST": "GetMap",
        "VERSION": "1.1.1",
        "LAYERS": DEFAULT_LAYER,
        "STYLES": "",
        "FORMAT": "image/jpeg",
        "TRANSPARENT": "FALSE",
        "SRS": "EPSG:4326",
        "WIDTH": 512,
        "HEIGHT": 512,
        "BBOX": boundary_box,
        "TIME": image_date,
    }

    query_string = "&".join(f"{key}={value}" for key, value in params.items())
    return f"{GIBS_WMS_URL}?{query_string}"

def get_random_location():
    latitude, longitude = generate_random_coordinate()
    image_url = build_gibs_image_url(latitude, longitude)

    return {
        "latitude": latitude,
        "longitude": longitude,
        "image_url": image_url
    }

def main():
    print("Generating random location...\n")

    try:
        location = get_random_location()

        print("Location:")
        print(f"Latitude:  {location['latitude']}")
        print(f"Longitude: {location['longitude']}")

        image_url = location["image_url"]

        print("\nDownloading image...")

        response = requests.get(image_url)

        if response.status_code == 200:
            # Convert response bytes into an image
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
