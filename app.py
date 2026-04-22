from location_generator import get_random_location, get_combined_image
from bot import get_bot_guess, distance_in_km


def main():
    print("Welcome to the Satellite Geography Game")
    print()

    # Generate location
    location = get_random_location()
    true_lat = location["latitude"]
    true_lon = location["longitude"]

    # Generate and save image
    image = get_combined_image(true_lat, true_lon, zoom=11)
    image.save("images/test_image.jpg")

    print("A satellite image has been saved to images/test_image.jpg")
    print()

    # Difficulty
    difficulty = input("Choose bot difficulty (easy, medium, hard, insane): ").strip().lower()

    # Player guess
    player_lat = float(input("Enter your latitude guess: "))
    player_lon = float(input("Enter your longitude guess: "))

    # Bot guess
    bot = get_bot_guess(true_lat, true_lon, difficulty)

    # Distances
    player_distance = distance_in_km(true_lat, true_lon, player_lat, player_lon)
    bot_distance = distance_in_km(true_lat, true_lon, bot["guess_latitude"], bot["guess_longitude"])

    # Results
    print()
    print("Results")
    print("-------------------")

    print("Your guess:")
    print("Latitude:", player_lat)
    print("Longitude:", player_lon)
    print("Distance from true location:", round(player_distance, 2), "km")
    print()

    print("Bot guess:")
    print("Latitude:", bot["guess_latitude"])
    print("Longitude:", bot["guess_longitude"])
    print("Distance from true location:", round(bot_distance, 2), "km")
    print("Difficulty:", bot["difficulty"])
    print("Time taken:", bot["time_taken"], "(ignored for now)")
    print()

    print("True location:")
    print("Latitude:", true_lat)
    print("Longitude:", true_lon)
    print()

    # Determine winner
    if player_distance < bot_distance:
        margin = bot_distance - player_distance
        print("You WIN!")
        print("You beat the bot by", round(margin, 2), "km")
    elif bot_distance < player_distance:
        margin = player_distance - bot_distance
        print("Bot WINS!")
        print("Bot beat you by", round(margin, 2), "km")
    else:
        print("It's a TIE!")



if __name__ == "__main__":
    main()
