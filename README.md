# Cyber Security Invaders

**Cyber Security Invaders** is an educational arcade-style game built with Python and Pygame, designed to teach players about cybersecurity concepts while providing a fun gaming experience. Players control a spacecraft at the bottom of the screen, aiming to shoot down enemy invaders while answering cybersecurity questions to earn extra lives.

## Features

- **Engaging Gameplay:** Navigate your player left and right to avoid enemy attacks while shooting down invaders.
- **Educational Questions:** Answer multiple-choice cybersecurity questions to increase your lives and enhance your knowledge.
- **Levels and Difficulty:** Progress through multiple levels, each with increasing difficulty and faster enemies.
- **Game Over Mechanics:** The game ends if any enemy reaches the bottom of the screen or if the player loses all lives.
- **Visuals:** Utilize PNG images for player and enemy sprites, enhancing the game's visual appeal.
- **Leaderboard System:** Cloud flask server for score tracking and display.

## Getting Started

### Prerequisites

- **Python:** Version 3.x
- **Pygame:** For game graphics and sound
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
- Ensure Pygame is installed. If not, install it using:
  ```
  pip install pygame
  ```
- If you're using a Raspberry Pi and want GPIO integration:
  ```
  pip install RPi.GPIO
  ```

### Running the Game

**Run the Game:**
- Open a new terminal or command prompt.
- Navigate back to the game directory if necessary:
  ```
  cd ..
  cd game
  ```
- Start the game:
  ```
  Cyber_Security_Invaders_V2.py
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

- **Server Not Responding:** The leaderboard server may be down
- **Game Freezes:** Verify Python, Pygame, and all dependencies are correctly installed. Also, check server IP in the game code.
- **GPIO Issues on Raspberry Pi:** Ensure you have the necessary permissions and that GPIO pins are correctly configured.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- Inspiration from classic arcade games.
- Thanks to the open-source community for Pygame and Flask.
