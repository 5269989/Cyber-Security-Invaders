import pygame
import random
import time
import os
import platform

# Check if running on a Raspberry Pi
is_raspberry_pi = platform.system() == "Linux" and "raspberrypi" in platform.uname().machine.lower()

# If running on Raspberry Pi, initialize GPIO
if is_raspberry_pi:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GREEN_LED_PIN = 4
    RED_LED_PIN = 17
    GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
    GPIO.setup(RED_LED_PIN, GPIO.OUT)
else:
    print("Not running on a Raspberry Pi. GPIO functionality disabled.")

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 128)

# Fonts
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 40)
bold_font = pygame.font.SysFont("Arial", 80, bold=True)

# Load and resize player and enemy images
player_image = pygame.image.load("player.png")
player_image = pygame.transform.scale(player_image, (50, 50))

enemy_image = pygame.image.load("enemy.png")
enemy_image = pygame.transform.scale(enemy_image, (40, 40))

# Load boss images
boss_image_1 = pygame.image.load("boss1.png")
boss_image_2 = pygame.image.load("boss2.png")
boss_image_1 = pygame.transform.scale(boss_image_1, (150, 150))  # Scale to a larger size
boss_image_2 = pygame.transform.scale(boss_image_2, (150, 150))  # Same size for the animation


# Player settings
player_width = player_image.get_width()
player_height = player_image.get_height()
player_x = (screen_width - player_width) // 2
player_y = screen_height - player_height - 10
player_speed = 5
player_lives = 3

# Bullet settings
bullet_width = 5
bullet_height = 10
bullet_speed = 7
bullets = []
last_shot_time = 0
shoot_interval = 0.05

# Enemy settings
enemy_width = enemy_image.get_width()
enemy_height = enemy_image.get_height()
enemy_speed = 2
enemy_bullet_speed = 5
enemies = []
enemy_direction = 1
enemy_shoot_prob = 0.003
enemy_bullets = []

# Boss settings
boss_width = boss_image_1.get_width()
boss_height = boss_image_1.get_height()
boss_x = (screen_width - boss_width) // 2
boss_y = 100  # Move boss down slightly from 50 to 100
boss_speed = 3
boss_health = 100
boss_max_health = 100  # Total health of the boss
boss_shoot_interval = 1.0  # Boss shoots every 1 second
last_boss_shot_time = 0
boss_bullets = []
boss_animation_interval = 0.5  # Switch images every 0.5 seconds
last_boss_animation_time = 0
boss_current_image = boss_image_1  # Start with the first boss image
boss_direction = 1  # 1 for right, -1 for left

# Health bar settings
health_bar_width = 200  # The total width of the health bar
health_bar_height = 20  # The height of the health bar
health_bar_position = (screen_width // 2 - health_bar_width // 2, 10)  # Centered at the top of the screen


# Game variables
game_over = False
level = 1
total_levels = 2
boss_fight = False
clock = pygame.time.Clock()
show_title_screen = True
question_limit = 3
questions_asked = 0
asked_questions = []
message_displayed_time = 0
last_hit_time = 0  # Track the last time the player was hit
hit_duration = 1.5  # Duration for which the message should be displayed

# Define a list of cybersecurity questions and their multiple-choice options and correct answers
cybersecurity_questions = [
    {"question": "What does 'HTTPS' stand for?",
     "options": ["A) Hypertext Transfer Protocol Standard", "B) Hypertext Transfer Protocol Secure", "C) High Transfer Protocol Secure"],
     "answer": "B"},

    {"question": "What is a common form of phishing attack?",
     "options": ["A) Email", "B) Phone call", "C) USB stick"],
     "answer": "A"},

    {"question": "Which type of malware locks your files and demands payment?",
     "options": ["A) Virus", "B) Worm", "C) Ransomware"],
     "answer": "C"},

    {"question": "What is a strong password?",
     "options": ["A) Your birthdate", "B) A combination of letters, numbers, and symbols", "C) Your pet's name"],
     "answer": "B"},

    {"question": "What does '2FA' stand for?",
     "options": ["A) Two-Factor Authentication", "B) Two-Factor Access", "C) Two-Factor Allowance"],
     "answer": "A"}
]

def wrap_text(text, font, max_width):
    """Wrap text to fit within a maximum width when rendered with the given font."""
    words = text.split(' ')
    lines = []
    current_line = ''
    for word in words:
        test_line = current_line + word + ' '
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + ' '
    if current_line:
        lines.append(current_line)
    return lines

def ask_cybersecurity_question():
    """Ask a random cybersecurity question and return True if the answer is correct."""
    global bullets, enemy_bullets, questions_asked, asked_questions

    # Check if the question limit has been reached
    if questions_asked >= question_limit:
        return False  # Automatically return False since no more questions can be asked

    # Increment the number of questions asked
    questions_asked += 1

    # Clear all bullets when a question is asked
    bullets = []
    enemy_bullets = []

    # Choose a question that hasn't been asked yet
    available_questions = [q for q in cybersecurity_questions if q not in asked_questions]

    if not available_questions:
        return False  # No more questions available

    question_data = random.choice(available_questions)
    asked_questions.append(question_data)  # Keep track of the asked question

    question = question_data["question"]
    options = question_data["options"]
    correct_answer = question_data["answer"]

    # Wrap the question text
    question_lines = wrap_text(question, big_font, screen_width - 40)
    screen.fill(BLACK)

    # Calculate starting y position to center the text vertically
    total_text_height = len(question_lines) * big_font.get_linesize()
    y_offset = screen_height // 2 - 150 - total_text_height // 2
    for i, line in enumerate(question_lines):
        question_text = big_font.render(line, True, WHITE)
        screen.blit(question_text, (screen_width // 2 - question_text.get_width() // 2, y_offset + i * big_font.get_linesize()))

    # Display instruction on how to answer
    instruction_text = font.render("Use arrow keys to select and Enter to submit", True, WHITE)
    screen.blit(instruction_text, (screen_width // 2 - instruction_text.get_width() // 2, screen_height // 2 + 100))

    pygame.display.flip()

    selected_index = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Check the selected answer
                    selected_answer = chr(pygame.K_a + selected_index).upper()
                    if selected_answer == correct_answer:
                        display_feedback("Correct!", GREEN)
                        return True
                    else:
                        display_feedback("Incorrect!", RED)
                        return False
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(options)
                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(options)

        # Display the question and options with the selected one highlighted
        screen.fill(BLACK)
        # Re-display the question lines
        for i, line in enumerate(question_lines):
            question_text = big_font.render(line, True, WHITE)
            screen.blit(question_text, (screen_width // 2 - question_text.get_width() // 2, y_offset + i * big_font.get_linesize()))

        # Display options
        option_y_start = screen_height // 2 - 50
        for i, option in enumerate(options):
            color = GREEN if i == selected_index else WHITE
            option_lines = wrap_text(option, font, screen_width - 40)
            for j, line in enumerate(option_lines):
                option_text = font.render(line, True, color)
                line_y = option_y_start + i * 60 + j * font.get_linesize()
                screen.blit(option_text, (screen_width // 2 - option_text.get_width() // 2, line_y))

        screen.blit(instruction_text, (screen_width // 2 - instruction_text.get_width() // 2, screen_height // 2 + 150))
        pygame.display.flip()


def display_feedback(message, color):
    """Display feedback on whether the answer was correct or incorrect."""
    screen.fill(BLACK)
    feedback_text = bold_font.render(message, True, color)
    screen.blit(feedback_text, (screen_width // 2 - feedback_text.get_width() // 2, screen_height // 2 - feedback_text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(2000)

def show_splash_screen():
    """Main menu screen with concise text and emphasis on key phrases."""
    screen.fill(BLACK)
    
    # Display the game title
    title_text = bold_font.render("Cyber Security Invaders", True, RED)
    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, screen_height // 2 - title_text.get_height()))

    # Display controls in neon yellow
    controls_text = big_font.render("Use arrow keys to move and space to shoot", True, (255, 255, 0))  # Neon yellow
    screen.blit(controls_text, (screen_width // 2 - controls_text.get_width() // 2, screen_height // 2 + 50))

    # Display "Press any key to continue"
    continue_text = big_font.render("Press any key to continue", True, WHITE)
    screen.blit(continue_text, (screen_width // 2 - continue_text.get_width() // 2, screen_height // 2 + 100))

    pygame.display.flip()
    
    # Wait for user input or a specified duration
    wait_for_keypress()

def boss_fight_splash_screen():
    """Display a splash screen that announces the boss fight and waits for any key press to continue."""
    screen.fill(BLACK)

    # Display 'Boss Fight!' in bold red text
    boss_fight_text = bold_font.render("Boss Fight!", True, RED)
    screen.blit(boss_fight_text, (screen_width // 2 - boss_fight_text.get_width() // 2, screen_height // 2 - 100))

    # Display 'Press any key to continue' in white text
    continue_text = big_font.render("Press any key to continue", True, WHITE)
    screen.blit(continue_text, (screen_width // 2 - continue_text.get_width() // 2, screen_height // 2 + 50))

    pygame.display.flip()

    # Wait for the player to press any key
    wait_for_keypress()

def update_boss():
    global boss_x, last_boss_shot_time, boss_current_image, last_boss_animation_time, boss_direction, player_lives

    # Move the boss left and right
    boss_x += boss_speed * boss_direction
    if boss_x <= 0 or boss_x + boss_width >= screen_width:
        boss_direction *= -1  # Change direction when hitting the edge

    # Switch boss image to create a simple animation
    current_time = time.time()
    if current_time - last_boss_animation_time >= boss_animation_interval:
        if boss_current_image == boss_image_1:
            boss_current_image = boss_image_2
        else:
            boss_current_image = boss_image_1
        last_boss_animation_time = current_time

    # Draw the boss
    screen.blit(boss_current_image, (boss_x, boss_y))

    # Draw the boss health bar
    draw_boss_health_bar()

    # Boss shooting bullets towards the player
    if current_time - last_boss_shot_time >= boss_shoot_interval:
        boss_bullets.append([boss_x + boss_width // 2, boss_y + boss_height])
        last_boss_shot_time = current_time

    # Update boss bullets
    for bullet in boss_bullets:
        bullet[1] += enemy_bullet_speed * 2  # Boss bullets are faster
        pygame.draw.rect(screen, YELLOW, (bullet[0], bullet[1], bullet_width, bullet_height))

        # Check if boss bullets hit the player
        if player_x < bullet[0] < player_x + player_width and player_y < bullet[1] < player_y + player_height:
            boss_bullets.remove(bullet)
            last_hit_time = time.time()  # Update last hit time
            if not ask_cybersecurity_question():
                player_lives -= 1
                if player_lives == 0:
                    game_over_screen()  # Trigger game over when lives run out

        # Remove bullets that go off-screen
        if bullet[1] > screen_height:
            boss_bullets.remove(bullet)

def check_boss_hit():
    global boss_health

    for bullet in bullets:
        if boss_x < bullet[0] < boss_x + boss_width and boss_y < bullet[1] < boss_y + boss_height:
            bullets.remove(bullet)
            boss_health -= 1

            if boss_health <= 0:
                boss_defeated_screen()  # Display boss defeated message
                reset_game()  # Restart the game
                
def check_player_hit():
    global player_x, player_y, player_width, player_height, enemy_bullets
    for bullet in enemy_bullets:
        if player_x < bullet[0] < player_x + player_width and player_y < bullet[1] < player_y + player_height:
            enemy_bullets.remove(bullet)  # Remove the bullet that hit the player
            return True  # Player was hit
    return False  # No hit detected



def boss_defeated_screen():
    screen.fill(BLACK)
    defeated_text = bold_font.render("Boss Defeated!", True, GREEN)
    screen.blit(defeated_text, (screen_width // 2 - defeated_text.get_width() // 2, screen_height // 2))
    pygame.display.flip()
    pygame.time.wait(3000)
    
def draw_boss_health_bar():
    """Draw the boss health bar on the screen."""
    # Calculate the current width of the health bar based on the boss's health
    current_health_ratio = boss_health / boss_max_health
    current_health_width = int(health_bar_width * current_health_ratio)

    # Draw the background of the health bar (the full length in red)
    pygame.draw.rect(screen, RED, (*health_bar_position, health_bar_width, health_bar_height))

    # Draw the current health (green) based on the boss's remaining health
    pygame.draw.rect(screen, GREEN, (*health_bar_position, current_health_width, health_bar_height))

def wait_for_keypress():
    """Wait until a key is pressed to continue."""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                return
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

def draw_player(x, y):
    screen.blit(player_image, (x, y))

def create_enemies():
    global enemies
    enemies = []
    for row in range(5):
        for col in range(10):
            enemy_x = col * (enemy_width + 10) + 50
            enemy_y = row * (enemy_height + 10) + 50
            enemies.append([enemy_x, enemy_y])

def draw_enemies():
    for enemy in enemies:
        screen.blit(enemy_image, (enemy[0], enemy[1]))

def update_enemies():
    global enemy_direction, game_over, level, boss_fight
    if not enemies:
        if level < total_levels:
            level += 1
            increase_difficulty()  # Increase difficulty when leveling up
            create_enemies()
        else:
            boss_fight_splash_screen()
            boss_fight = True

    edge_reached = False
    for enemy in enemies:
        enemy[0] += enemy_speed * enemy_direction
        if enemy[0] <= 0 or enemy[0] + enemy_width >= screen_width:
            edge_reached = True

        if random.random() < enemy_shoot_prob:
            enemy_bullets.append([enemy[0] + enemy_width // 2, enemy[1] + enemy_height])

        if enemy[1] + enemy_height >= screen_height:
            game_over_screen()

    if edge_reached:
        for enemy in enemies:
            enemy[1] += 20
        enemy_direction *= -1

def increase_difficulty():
    """Increase the difficulty by speeding up enemies or changing shooting probability."""
    global enemy_speed, enemy_shoot_prob
    enemy_speed += 0.5
    enemy_shoot_prob += 0.001

def update_bullets():
    for bullet in bullets:
        bullet[1] -= bullet_speed
        pygame.draw.rect(screen, GREEN, (bullet[0], bullet[1], bullet_width, bullet_height))

        if bullet[1] < 0:
            bullets.remove(bullet)

        for enemy in enemies:
            if enemy[0] < bullet[0] < enemy[0] + enemy_width and enemy[1] < bullet[1] < enemy[1] + enemy_height:
                bullets.remove(bullet)
                enemies.remove(enemy)
                break

def update_enemy_bullets():
    global player_lives, last_hit_time, player_lives
    for bullet in enemy_bullets:
        bullet[1] += enemy_bullet_speed
        pygame.draw.rect(screen, RED, (bullet[0], bullet[1], bullet_width, bullet_height))

        if bullet[1] > screen_height:
            enemy_bullets.remove(bullet)

        # Check collision with player
        if player_x < bullet[0] < player_x + player_width and player_y < bullet[1] < player_y + player_height:
            enemy_bullets.remove(bullet)
            last_hit_time = time.time()  # Update last hit time
            if not ask_cybersecurity_question():
                player_lives -= 1
                if player_lives == 0:
                    game_over_screen()  # Trigger game over when lives run out


def game_over_screen():
    """Displays the Game Over screen with options to restart or quit."""
    screen.fill(RED)  # Red background

    # Display 'GAME OVER!' in bold white text
    game_over_text = bold_font.render("GAME OVER!", True, WHITE)
    screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - 100))

    # Display instructions to press 'R' to restart or 'Q' to quit
    instruction_text = big_font.render("Press R to Restart or Q to Quit", True, WHITE)
    screen.blit(instruction_text, (screen_width // 2 - instruction_text.get_width() // 2, screen_height // 2 + 50))

    pygame.display.flip()

    # Wait for player to press 'R' or 'Q'
    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Press 'R' to restart
                    waiting_for_input = False
                    reset_game()
                elif event.key == pygame.K_q:  # Press 'Q' to quit
                    pygame.quit()
                    quit()


def reset_game():
    """Reset game variables and start over."""
    global player_lives, bullets, enemy_bullets, level, boss_fight, questions_asked, message_displayed_time, last_hit_time, asked_questions
    player_lives = 3
    bullets = []
    enemy_bullets = []
    level = 1
    questions_asked = 0
    message_displayed_time = 0
    asked_questions = []
    last_hit_time = 0 
    boss_fight = False
    create_enemies()
    main_game_loop()


def main_game_loop():
    global player_x, player_y, last_shot_time, boss_fight

    player_hit = False  # Add this line to initialize player_hit
    
    while not game_over:
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Key handling
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed
        if keys[pygame.K_SPACE]:
            if time.time() - last_shot_time >= shoot_interval:
                bullets.append([player_x + player_width // 2, player_y])
                last_shot_time = time.time()

        # Ensure player doesn't move off screen
        if player_x < 0:
            player_x = 0
        if player_x + player_width > screen_width:
            player_x = screen_width - player_width

        draw_player(player_x, player_y)
        update_bullets()

        if boss_fight:
            update_boss()
            check_boss_hit()

        else:
            update_enemies()
            draw_enemies()
            update_enemy_bullets()  # Make sure enemy bullets are updated here

        # Check if player was hit by an enemy bullet
        if check_player_hit():  # You'll create this function below
            player_hit = True

        # Display player lives and level
        lives_text = font.render(f"Lives: {player_lives}", True, WHITE)
        screen.blit(lives_text, (10, 10))

        # If the player was hit, display the message and turn on the red LED
        if player_hit:  # Now it's defined
            if is_raspberry_pi:
                GPIO.output(RED_LED_PIN, GPIO.HIGH)  # Turn on red LED
                time.sleep(0.2)  # LED stays on for 200ms
                GPIO.output(RED_LED_PIN, GPIO.LOW)  # Turn off red LED
            player_hit = False  # Reset player_hit after LED blink

        pygame.display.update()
        clock.tick(60)


        
def main():
    create_enemies()
    show_splash_screen()
    main_game_loop()

main()
