import pygame
import random
import RPi.GPIO as GPIO
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

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GREEN_LED_PIN = 4
RED_LED_PIN = 17  # New pin for red LED
GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
GPIO.setup(RED_LED_PIN, GPIO.OUT)

# Fonts
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 40)
bold_font = pygame.font.SysFont("Arial", 80, bold=True)

# Player settings
player_width = 60
player_height = 20
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
shoot_interval = 0.2

# Enemy settings
enemy_width = 40
enemy_height = 30
enemy_speed = 2
enemies = []
enemy_direction = 1

# Game variables
game_over = False

# Game clock
clock = pygame.time.Clock()

def draw_player(x, y):
    pygame.draw.rect(screen, WHITE, (x, y, player_width, player_height))

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
        pygame.draw.rect(screen, RED, (enemy[0], enemy[1], enemy_width, enemy_height))

def update_enemies():
    global enemy_direction, game_over
    for enemy in enemies:
        enemy[0] += enemy_speed * enemy_direction

        if enemy[0] <= 0 or enemy[0] + enemy_width >= screen_width:
            enemy_direction *= -1
            for e in enemies:
                e[1] += 20

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

                # Turn on green LED when an enemy is hit
                GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
                pygame.time.delay(500)
                GPIO.output(GREEN_LED_PIN, GPIO.LOW)
                break

def player_hit():
    global player_lives
    player_lives -= 1

    # Turn on red LED when the player is hit
    GPIO.output(RED_LED_PIN, GPIO.HIGH)
    pygame.time.delay(500)
    GPIO.output(RED_LED_PIN, GPIO.LOW)

def main_game():
    global player_x, bullets, game_over

    create_enemies()

    while not game_over:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                GPIO.cleanup()
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < screen_width - player_width:
            player_x += player_speed

        if keys[pygame.K_SPACE]:
            bullet_x = player_x + player_width // 2 - bullet_width // 2
            bullet_y = player_y
            bullets.append([bullet_x, bullet_y])

        update_bullets()
        update_enemies()
        draw_player(player_x, player_y)
        draw_enemies()

        if player_lives <= 0:
            game_over = True

        pygame.display.flip()
        clock.tick(60)

try:
    main_game()
finally:
    GPIO.cleanup()
