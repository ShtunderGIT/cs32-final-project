import random
import requests
import webbrowser
from datetime import date, timedelta

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
    # We will build a square boundary around the center point
    # This defines the area of Earth we request an image for.
    # The size is fixed to keep the design simple for now.

    boundary_size = 1.0  # degrees (controls zoom level)
    min_lat = max(-90, latitude - boundary_size)
    max_lat = min(90, latitude + boundary_size)
    min_lon = max(-180, longitude - boundary_size)
    max_lon = min(180, longitude + boundary_size)

    return f"{min_lon},{min_lat},{max_lon},{max_lat}"

def build_gibs_image_url(latitude, longitude):
    #Build a NASA GIBS image URL for the given coordinates.

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

    #Return a random location with matching coordinates and image URL.

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

            file_path = "images/test_image.jpg"

            with open(file_path, "wb") as f:
                f.write(response.content)

            print(f"Image saved to {file_path}")
        else:
            print("Failed to download image.")

    except Exception as e:
        print("Error:", e)
