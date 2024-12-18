# Cyber Security Invaders

**Cyber Security Invaders** is an educational arcade-style game built with Python and Pygame, designed to teach players about cybersecurity concepts while providing a fun gaming experience. Players control a spacecraft at the bottom of the screen, aiming to shoot down enemy invaders while answering cybersecurity questions to earn extra lives.

## Features

- **Engaging Gameplay**: Navigate your player left and right to avoid enemy attacks while shooting down invaders.
- **Educational Questions**: Answer multiple-choice cybersecurity questions to increase your lives and enhance your knowledge.
- **Levels and Difficulty**: Progress through multiple levels, each with increasing difficulty and faster enemies.
- **Game Over Mechanics**: The game ends if any enemy reaches the bottom of the screen or if the player loses all lives.
- **Visuals**: Utilize PNG images for player and enemy sprites, enhancing the game's visual appeal.

## Getting Started

### Prerequisites

- Python 3.x
- Pygame library

### Installation

1. Clone the repository:
   git clone https://github.com/yourusername/cyber-security-invaders.git

2. cd cyber-security-invaders

3. Install dependencies:
   Make sure Pygame is installed. If not, you can install it using:
   pip install pygame

4. Run the game:
   python main.py

## Running on Raspberry Pi
If you're using a Raspberry Pi and want to integrate GPIO:

Ensure you have RPi.GPIO installed:
   pip install RPi.GPIO
   Connect LEDs to GPIO pins as described in the code (pins 4 and 17 for this setup).

Game Controls
Move Left: Left Arrow Key
Move Right: Right Arrow Key
Shoot: Spacebar
Select Menu Options: Up/Down Arrow Keys, Enter to confirm
Game Over Interaction: 'R' to restart, 'Q' to quit

## Save the file in your project's root directory.

This file is now ready to be included in your GitHub repository or used locally. If you want to make it available online, you would typically commit and push this file to your repository:

