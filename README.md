
My project is an interactive geography-based game inspired by GeoGuessr. Unlike GeoGuessr, which uses street-view images, this game uses satellite imagery instead. Players is be shown a satellite-view image of a mystery location and will have to guess where it is by clicking on a map. The game is based on a single-player model with a computer opponent, with diverging rates of complexity. The game keeps the score of who one and who lose and allows to generate a new round right away. All the gameplay is done in a pop-up desktop window. To generate locations and images, the project uses USGS' open API for image search.

FP Status notes: This project uses the pygame library to create a UI for the game. Because of that, the project can be started only from the
Desktop VS Code. Otherwise, it won't be able to open the windows on the desktop to display the UI.

Before running the code, install everything from requirements.txt

