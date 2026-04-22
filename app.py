from location_generator import get_random_location, get_combined_image
from bot import get_bot_guess


def main():
    print("Welcome to the Satellite Geography Game")
    print()

    # Generate a random location
    location = get_random_location()

    true_lat = location["latitude"]
    true_lon = location["longitude"]

    # Generate and save the satellite image
    image = get_combined_image(true_lat, true_lon, zoom=15)
    image.save("images/test_image.jpg")

    print("A satellite image has been saved to images/test_image.jpg")
    print()

    # Ask user for difficulty
    difficulty = input("Choose bot difficulty (easy, medium, hard, insane): ").strip().lower()

    # Ask player for guess
    player_lat = float(input("Enter your latitude guess: "))
    player_lon = float(input("Enter your longitude guess: "))

    # Get bot guess
    bot_guess = get_bot_guess(true_lat, true_lon, difficulty)

    # Show results
    print()
    print("Results")
    print("-------------------")
    print("Your guess:")
    print("Latitude:", player_lat)
    print("Longitude:", player_lon)
    print()

    print("Bot guess:")
    print("Latitude:", bot_guess["guess_latitude"])
    print("Longitude:", bot_guess["guess_longitude"])
    print("Difficulty:", bot_guess["difficulty"])
    print("Time taken:", bot_guess["time_taken"])
    print()

    print("True location:")
    print("Latitude:", true_lat)
    print("Longitude:", true_lon)


if __name__ == "__main__":
    main()
