# Cyber Security Invaders

**Cyber Security Invaders** is an educational arcade-style game built with Python and Pygame, designed to teach players about cybersecurity concepts while providing a fun gaming experience. Players control a spacecraft at the bottom of the screen, aiming to shoot down enemy invaders while answering cybersecurity questions to earn extra lives.

## Features

- **Engaging Gameplay:** Navigate your player left and right to avoid enemy attacks while shooting down invaders.
- **Educational Questions:** Answer multiple-choice cybersecurity questions to increase your lives and enhance your knowledge.
- **Levels and Difficulty:** Progress through multiple levels, each with increasing difficulty and faster enemies.
- **Game Over Mechanics:** The game ends if any enemy reaches the bottom of the screen or if the player loses all lives.
- **Visuals:** Utilize PNG images for player and enemy sprites, enhancing the game's visual appeal.
- **Leaderboard System:** Flask server for score tracking and display.

## Getting Started

### Prerequisites

- **Python:** Version 3.x
- **Pygame:** For game graphics and sound
- **Flask:** For running the leaderboard server
- **RPi.GPIO (optional):** If running on Raspberry Pi for LED feedback

### Installation

1. **Clone the repository:**
    ```
   . git clone https://github.com/yourusername/cyber-security-invaders.git
   ```
3. **Navigate to the project directory:**
   ```
   . cd cyber-security-invaders
   ```
4. **Install dependencies:**
- Ensure Pygame and Flask are installed. If not, install them using:
  ```
  pip install pygame flask
  ```
- If you're using a Raspberry Pi and want GPIO integration:
  ```
  pip install RPi.GPIO
  ```

### Running the Game

1. **Start the Flask Server** (for leaderboard functionality):
- Navigate to the Flask server directory:
  ```
  cd thisiot_FlaskServer
  ```
- Run the server:
  ```
  python server.py
  ```
- Keep this terminal open as the server needs to run continuously.

2. **Run the Game:**
- Open a new terminal or command prompt.
- Navigate back to the game directory if necessary:
  ```
  cd ..
  cd game
  ```
- Start the game:
  ```
  python main.py
  ```

### Running on Raspberry Pi

- Connect LEDs to GPIO pins as described in the code (pins 4 and 17 for this setup).
- Ensure RPi.GPIO is installed as mentioned in the prerequisites.

### Game Controls

- **Move Left:** Left Arrow Key
- **Move Right:** Right Arrow Key
- **Shoot:** Spacebar
- **Select Menu Options:** Up/Down Arrow Keys, Enter to confirm
- **Game Over Interaction:** 'R' to restart, 'Q' to quit

### Troubleshooting

- **Server Not Responding:** Check if the server is running and that your firewall allows connections on port 5000.
- **Game Freezes:** Verify Python, Pygame, and all dependencies are correctly installed. Also, check server IP in the game code.
- **GPIO Issues on Raspberry Pi:** Ensure you have the necessary permissions and that GPIO pins are correctly configured.

## Contributing

If you'd like to contribute, please fork the project, make your changes, and submit a pull request. Here's how you can contribute:

- Follow PEP 8 for Python code style.
- Add tests or update existing ones for new features or bug fixes.
- Update documentation if you change how the game or server operates.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- Inspiration from classic arcade games.
- Thanks to the open-source community for Pygame and Flask.
