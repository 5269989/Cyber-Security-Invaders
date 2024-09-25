import pygame
import RPi.GPIO as GPIO
import time
import random

# Raspberry Pi GPIO setup
GPIO.setmode(GPIO.BCM)
green_led_pin = 18  # GPIO pin for green LED
red_led_pin = 17    # GPIO pin for red LED

GPIO.setup(green_led_pin, GPIO.OUT)
GPIO.setup(red_led_pin, GPIO.OUT)

# Initialize Pygame
pygame.init()

# Screen settings
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Cybersecurity IoT Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Player settings
player_width = 50
player_height = 50
player_x = screen_width // 2 - player_width // 2
player_y = screen_height - player_height - 10
player_speed = 5

# Enemy settings
enemy_width = 50
enemy_height = 50
enemy_speed = 5
enemies = []

# Quiz settings (for when the player is hit)
quiz_font = pygame.font.Font(None, 36)
quiz_questions = [
    {"question": "What is a strong password?", "options": ["123456", "password", "P@ssw0rd!"], "answer": 2},
    {"question": "What should you not click on?", "options": ["Phishing link", "Trusted link"], "answer": 0},
    # Add more questions
]

# Function to generate random enemies
def create_enemy():
    x = random.randint(0, screen_width - enemy_width)
    y = random.randint(-100, -40)
    return pygame.Rect(x, y, enemy_width, enemy_height)

# Draw player and enemies
def draw_objects(player, enemies):
    pygame.draw.rect(screen, GREEN, player)
    for enemy in enemies:
        pygame.draw.rect(screen, RED, enemy)

# Display quiz question
def display_quiz(question):
    screen.fill(WHITE)
    question_text = quiz_font.render(question["question"], True, BLACK)
    screen.blit(question_text, (50, 100))
    
    for i, option in enumerate(question["options"]):
        option_text = quiz_font.render(f"{i+1}. {option}", True, BLACK)
        screen.blit(option_text, (50, 200 + i * 50))
    
    pygame.display.update()

# Check if the player answers the quiz correctly
def check_quiz_answer(question, selected_option):
    return selected_option == question["answer"]

# Game loop
def game_loop():
    global player_x, player_y
    clock = pygame.time.Clock()
    game_over = False
    score = 0
    enemies.append(create_enemy())
    
    quiz_mode = False
    current_question = None
    
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed

        # Ensure player stays within screen bounds
        player_x = max(0, min(player_x, screen_width - player_width))

        player = pygame.Rect(player_x, player_y, player_width, player_height)

        if not quiz_mode:
            # Move enemies down
            for enemy in enemies:
                enemy.y += enemy_speed

                if enemy.y > screen_height:
                    enemy.y = random.randint(-100, -40)
                    enemy.x = random.randint(0, screen_width - enemy_width)

                # Check for collisions
                if player.colliderect(enemy):
                    GPIO.output(red_led_pin, GPIO.HIGH)  # Light up red LED
                    time.sleep(1)
                    GPIO.output(red_led_pin, GPIO.LOW)
                    
                    quiz_mode = True
                    current_question = random.choice(quiz_questions)

            screen.fill(WHITE)
            draw_objects(player, enemies)
            pygame.display.update()

        else:
            display_quiz(current_question)
            if keys[pygame.K_1]:
                if check_quiz_answer(current_question, 0):
                    quiz_mode = False
                else:
                    print("Incorrect answer!")
            elif keys[pygame.K_2]:
                if check_quiz_answer(current_question, 1):
                    quiz_mode = False
                else:
                    print("Incorrect answer!")
            elif keys[pygame.K_3]:
                if check_quiz_answer(current_question, 2):
                    quiz_mode = False
                else:
                    print("Incorrect answer!")

        clock.tick(30)

    GPIO.cleanup()
    pygame.quit()

# Run the game loop
game_loop()
