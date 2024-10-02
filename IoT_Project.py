import pygame
import random
from gpiozero import LED
import time

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
shoot_interval = 0.25

# Enemy settings
enemy_width = enemy_image.get_width()
enemy_height = enemy_image.get_height()
enemy_speed = 2
enemy_bullet_speed = 5
enemies = []
enemy_direction = 1
enemy_shoot_prob = 0.003
enemy_bullets = []

# Game variables
game_over = False
level = 1
total_levels = 2
boss_fight = False
clock = pygame.time.Clock()
show_title_screen = True

# GPIO LED setup
Green_LED = LED(4)  # GPIO pin 4 for green LED
Red_LED = LED(17)   # GPIO pin 17 for red LED

# LED flashing state variables
led_flash_duration = 0.5  # Duration in seconds
green_led_flash_time = None
red_led_flash_time = None

def ask_cybersecurity_question():
    """Ask a random cybersecurity question and return True if the answer is correct."""
    cybersecurity_questions = [
        {"question": "What does 'HTTPS' stand for?", "options": ["A) Hypertext Transfer Protocol Standard", "B) Hypertext Transfer Protocol Secure", "C) High Transfer Protocol Secure"], "answer": "B"},
        {"question": "What is a common form of phishing attack?", "options": ["A) Email", "B) Phone call", "C) USB stick"], "answer": "A"},
        {"question": "Which type of malware locks your files and demands payment?", "options": ["A) Virus", "B) Worm", "C) Ransomware"], "answer": "C"},
        {"question": "What is a strong password?", "options": ["A) Your birthdate", "B) A combination of letters, numbers, and symbols", "C) Your pet's name"], "answer": "B"},
        {"question": "What does '2FA' stand for?", "options": ["A) Two-Factor Authentication", "B) Two-Factor Access", "C) Two-Factor Allowance"], "answer": "A"}
    ]
    
    question_data = random.choice(cybersecurity_questions)
    question = question_data["question"]
    options = question_data["options"]
    correct_answer = question_data["answer"]

    selected_index = 0
    screen.fill(BLACK)
    question_text = big_font.render(question, True, WHITE)
    screen.blit(question_text, (screen_width // 2 - question_text.get_width() // 2, screen_height // 2 - 150))

    instruction_text = font.render("Use arrow keys to select and Enter to submit", True, WHITE)
    screen.blit(instruction_text, (screen_width // 2 - instruction_text.get_width() // 2, screen_height // 2 + 100))
    
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
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

        screen.fill(BLACK)
        screen.blit(question_text, (screen_width // 2 - question_text.get_width() // 2, screen_height // 2 - 150))
        for i, option in enumerate(options):
            color = GREEN if i == selected_index else WHITE
            option_text = font.render(option, True, color)
            screen.blit(option_text, (screen_width // 2 - option_text.get_width() // 2, screen_height // 2 - 50 + i * 40))
        screen.blit(instruction_text, (screen_width // 2 - instruction_text.get_width() // 2, screen_height // 2 + 100))
        pygame.display.flip()

def display_feedback(message, color):
    """Display feedback on whether the answer was correct or incorrect."""
    screen.fill(BLACK)
    feedback_text = bold_font.render(message, True, color)
    screen.blit(feedback_text, (screen_width // 2 - feedback_text.get_width() // 2, screen_height // 2 - feedback_text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(2000)

def show_splash_screen(message, duration=None):
    """Show a splash screen with a message."""
    screen.fill(BLACK)
    splash_text = big_font.render(message, True, RED)
    screen.blit(splash_text, (screen_width // 2 - splash_text.get_width() // 2, screen_height // 2 - splash_text.get_height() // 2))
    pygame.display.flip()
    if duration:
        pygame.time.wait(duration)
    else:
        wait_for_keypress()

def wait_for_keypress():
    """Wait until a key is pressed to continue."""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                return

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
            increase_difficulty()
            create_enemies()
        else:
            show_splash_screen("Boss Fight!", 3000)
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
                hit_enemy()

def update_enemy_bullets():
    global player_lives
    for bullet in enemy_bullets:
        bullet[1] += enemy_bullet_speed
        pygame.draw.rect(screen, RED, (bullet[0], bullet[1], bullet_width, bullet_height))

        if bullet[1] > screen_height:
            enemy_bullets.remove(bullet)

        if player_x < bullet[0] < player_x + player_width and player_y < bullet[1] < player_y + player_height:
            enemy_bullets.remove(bullet)
            player_lives -= 1
            hit_player()

def hit_enemy():
    """Handle when a player hits an enemy."""
    global green_led_flash_time
    green_led_flash_time = time.time()  # Record the time to flash the LED
    Green_LED.on()

def hit_player():
    """Handle when an enemy hits the player."""
    global red_led_flash_time
    if player_lives > 0:
        if ask_cybersecurity_question():
            return
    red_led_flash_time = time.time()  # Record the time to flash the LED
    Red_LED.on()

    if player_lives <= 0:
        game_over_screen()

def game_over_screen():
    """Display the game over screen."""
    show_splash_screen("Game Over!")
    pygame.quit()
    quit()

def handle_led_flash():
    """Handle the LED flash timing and turning off the LEDs after the duration has passed."""
    global green_led_flash_time, red_led_flash_time

    if green_led_flash_time and time.time() - green_led_flash_time >= led_flash_duration:
        Green_LED.off()
        green_led_flash_time = None  # Reset the flash time
    
    if red_led_flash_time and time.time() - red_led_flash_time >= led_flash_duration:
        Red_LED.off()
        red_led_flash_time = None  # Reset the flash time

# Main game loop
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_x -= player_speed
            if event.key == pygame.K_RIGHT:
                player_x += player_speed
            if event.key == pygame.K_SPACE:
                current_time = time.time()
                if current_time - last_shot_time >= shoot_interval:
                    bullets.append([player_x + player_width // 2 - bullet_width // 2, player_y])
                    last_shot_time = current_time

    # Draw player, bullets, enemies, and enemy bullets
    draw_player(player_x, player_y)
    update_bullets()
    update_enemy_bullets()
    update_enemies()
    draw_enemies()

    # Draw player lives
    lives_text = font.render(f"Lives: {player_lives}", True, WHITE)
    screen.blit(lives_text, (10, 10))

    # Handle LED flashing logic
    handle_led_flash()

    pygame.display.flip()
    clock.tick(60)

# Cleanup GPIO resources
Green_LED.off()
Red_LED.off()
