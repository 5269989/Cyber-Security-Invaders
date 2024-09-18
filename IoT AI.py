
import pygame
import random

# Initialize pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Title and Icon
pygame.display.set_caption("Cyber Security Invaders")
icon = pygame.image.load('spaceship.png')  # Placeholder for spaceship icon
pygame.display.set_icon(icon)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Fonts
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 40)

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

# Enemy settings
enemy_width = 40
enemy_height = 30
enemy_speed = 2
enemy_bullet_speed = 5
enemies = []
enemy_direction = 1  # Moving direction: 1 for right, -1 for left
enemy_shoot_prob = 0.003  # Probability of front row enemies shooting

# Game variables
score = 0
level = 1
total_levels = 3
lives = 3
game_over = False
space_invaders_completed = False

# Game clock
clock = pygame.time.Clock()

# Splash screen for Space Invaders
def splash_screen():
    screen.fill(BLACK)
    message = big_font.render("Cyber Security Invaders", True, WHITE)
    sub_message = font.render("Learn about secure passwords while defeating invaders!", True, WHITE)
    play_message = font.render("Press any key to start...", True, GREEN)
    
    screen.blit(message, (screen_width // 2 - message.get_width() // 2, screen_height // 2 - 100))
    screen.blit(sub_message, (screen_width // 2 - sub_message.get_width() // 2, screen_height // 2))
    screen.blit(play_message, (screen_width // 2 - play_message.get_width() // 2, screen_height // 2 + 100))
    
    pygame.display.flip()
    
    # Wait for user input to start the game
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                waiting = False

# Splash screen for IoT Kong
def iot_kong_splash_screen():
    screen.fill(BLACK)
    message = big_font.render("Welcome to IoT Kong!", True, WHITE)
    sub_message = font.render("Learn about protecting your IoT devices.", True, WHITE)
    play_message = font.render("Press any key to start the next adventure...", True, GREEN)
    
    screen.blit(message, (screen_width // 2 - message.get_width() // 2, screen_height // 2 - 100))
    screen.blit(sub_message, (screen_width // 2 - sub_message.get_width() // 2, screen_height // 2))
    screen.blit(play_message, (screen_width // 2 - play_message.get_width() // 2, screen_height // 2 + 100))
    
    pygame.display.flip()
    
    # Wait for user input to start the next part of the game
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                waiting = False

# Function to draw player
def draw_player(x, y):
    pygame.draw.polygon(screen, GREEN, [(x, y), (x + player_width // 2, y - 20), (x + player_width, y)])

# Function to create enemies in a 10 x 5 grid
def create_enemies():
    global enemies
    enemies = []
    for row in range(5):
        for col in range(10):
            enemy_x = col * (enemy_width + 10) + 50
            enemy_y = row * (enemy_height + 10) + 50
            enemies.append([enemy_x, enemy_y])

# Function to draw enemies
def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(screen, WHITE, (enemy[0], enemy[1], enemy_width, enemy_height))

# Function to update enemies (moving left and right, and only front row shoots)
def update_enemies():
    global enemy_direction, game_over
    edge_reached = False

    front_row = set([enemy[0] for enemy in enemies if not any(e[1] > enemy[1] for e in enemies)])

    for enemy in enemies:
        enemy[0] += enemy_speed * enemy_direction
        if enemy[0] <= 0 or enemy[0] + enemy_width >= screen_width:
            edge_reached = True

        # Only front row enemies shoot occasionally
        if enemy[0] in front_row and random.random() < enemy_shoot_prob:
            enemy_bullets.append([enemy[0] + enemy_width // 2, enemy[1] + enemy_height])

        # Game over if enemies reach bottom
        if enemy[1] + enemy_height >= player_y:
            game_over = True

    if edge_reached:
        for enemy in enemies:
            enemy[1] += 20
        enemy_direction *= -1

# Function to update bullets
def update_bullets():
    global score

    # Player's bullets
    for bullet in bullets:
        bullet[1] -= bullet_speed
        pygame.draw.rect(screen, RED, (bullet[0], bullet[1], bullet_width, bullet_height))

        # Bullet off-screen
        if bullet[1] < 0:
            bullets.remove(bullet)

        # Check for collision with enemies
        for enemy in enemies:
            if enemy[0] < bullet[0] < enemy[0] + enemy_width and enemy[1] < bullet[1] < enemy[1] + enemy_height:
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 1
                break

# Function to update enemy bullets
enemy_bullets = []
def update_enemy_bullets():
    global player_lives

    for bullet in enemy_bullets:
        bullet[1] += enemy_bullet_speed
        pygame.draw.rect(screen, YELLOW, (bullet[0], bullet[1], bullet_width, bullet_height))

        # Bullet off-screen
        if bullet[1] > screen_height:
            enemy_bullets.remove(bullet)

        # Check for collision with player
        if player_x < bullet[0] < player_x + player_width and player_y < bullet[1] < player_y + player_height:
            enemy_bullets.remove(bullet)
            player_lives -= 1

# Function to display score, level, and lives
def display_info():
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}/{total_levels}", True, WHITE)
    lives_text = font.render(f"Lives: {player_lives}", True, WHITE)

    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (screen_width // 2 - 50, 10))
    screen.blit(lives_text, (screen_width - 120, 10))

# Function to reset game state for the next level
def next_level():
    global level, enemy_speed, enemies
    level += 1
    enemy_speed += 1
    create_enemies()

# Main game loop
def main_game():
    global player_x, player_y, bullets, enemy_bullets, player_lives, score, game_over, level, space_invaders_completed

    # Initial setup
    player_x = (screen_width - player_width) // 2
    create_enemies()

    while not game_over:
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < screen_width - player_width:
            player_x += player_speed

        # Shooting bullets
        if keys[pygame.K_SPACE]:
            if len(bullets) < 3:  # Max 3 bullets on screen at a time
                bullet_x = player_x + player_width // 2 - bullet_width // 2
                bullet_y = player_y
                bullets.append([bullet_x, bullet_y])

        # Update and draw bullets
        update_bullets()
        update_enemy_bullets()

        # Draw player
        draw_player(player_x, player_y)

        # Update and draw enemies
        update_enemies()
        draw_enemies()

        # Display score, level, and lives
        display_info()

        # Check for level progression
        if not enemies and level < total_levels:
            next_level()
        elif not enemies and level == total_levels:
            space_invaders_completed = True
            game_over = True

        # Game over condition
        if player_lives <= 0:
            game_over = True

        # Update the display
        pygame.display.flip()

        # Frame rate
        clock.tick(60)

# Run splash screen and main game
splash_screen()
main_game()

if space_invaders_completed:
    iot_kong_splash_screen()

pygame.quit()




------------------------------------

import pygame
import random
import time

# Initialize pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Title and Icon
pygame.display.set_caption("Cyber Security Invaders")
icon = pygame.image.load('spaceship.png')  # Example for spaceship icon
pygame.display.set_icon(icon)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Fonts
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 40)

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

# Enemy settings
enemy_width = 40
enemy_height = 30
enemy_speed = 2
enemy_bullet_speed = 5
enemies = []
enemy_direction = 1  # Moving direction: 1 for right, -1 for left
enemy_shoot_prob = 0.002  # Probability of enemy shooting

# Game variables
score = 0
level = 1
max_score_for_next_level = 15
lives = 3
game_over = False

# Game clock
clock = pygame.time.Clock()

# Splash screen
def splash_screen():
    screen.fill(BLACK)
    message = big_font.render("Cyber Security Invaders", True, RED)
    sub_message = font.render("Learn about the importance of secure passwords while saving the world!", True, WHITE)
    play_message = font.render("Press any key to start...", True, GREEN)
    
    screen.blit(message, (screen_width // 2 - message.get_width() // 2, screen_height // 2 - 100))
    screen.blit(sub_message, (screen_width // 2 - sub_message.get_width() // 2, screen_height // 2))
    screen.blit(play_message, (screen_width // 2 - play_message.get_width() // 2, screen_height // 2 + 100))
    
    pygame.display.flip()
    
    # Wait for user input to start the game
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                waiting = False

# Function to draw player
def draw_player(x, y):
    pygame.draw.polygon(screen, GREEN, [(x, y), (x + player_width // 2, y - 20), (x + player_width, y)])

# Function to create enemies in a 10 x 5 grid
def create_enemies():
    global enemies
    enemies = []
    for row in range(5):
        for col in range(10):
            enemy_x = col * (enemy_width + 10) + 50
            enemy_y = row * (enemy_height + 10) + 50
            enemies.append([enemy_x, enemy_y])

# Function to draw enemies
def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(screen, WHITE, (enemy[0], enemy[1], enemy_width, enemy_height))

# Function to update enemies (moving left and right, and occasionally shooting)
def update_enemies():
    global enemy_direction, game_over
    edge_reached = False

    for enemy in enemies:
        enemy[0] += enemy_speed * enemy_direction
        if enemy[0] <= 0 or enemy[0] + enemy_width >= screen_width:
            edge_reached = True
        
        # Random shooting
        if random.random() < enemy_shoot_prob:
            enemy_bullets.append([enemy[0] + enemy_width // 2, enemy[1] + enemy_height])

        # Check if enemy reached the bottom (Game over condition)
        if enemy[1] + enemy_height >= player_y:
            game_over = True

    if edge_reached:
        for enemy in enemies:
            enemy[1] += 20
        enemy_direction *= -1

# Function to update bullets
def update_bullets():
    global score

    # Player's bullets
    for bullet in bullets:
        bullet[1] -= bullet_speed
        pygame.draw.rect(screen, RED, (bullet[0], bullet[1], bullet_width, bullet_height))

        # Bullet off-screen
        if bullet[1] < 0:
            bullets.remove(bullet)

        # Check for collision with enemies
        for enemy in enemies:
            if enemy[0] < bullet[0] < enemy[0] + enemy_width and enemy[1] < bullet[1] < enemy[1] + enemy_height:
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 1
                break

# Function to update enemy bullets
enemy_bullets = []
def update_enemy_bullets():
    global player_lives

    for bullet in enemy_bullets:
        bullet[1] += enemy_bullet_speed
        pygame.draw.rect(screen, YELLOW, (bullet[0], bullet[1], bullet_width, bullet_height))

        # Bullet off-screen
        if bullet[1] > screen_height:
            enemy_bullets.remove(bullet)

        # Check for collision with player
        if player_x < bullet[0] < player_x + player_width and player_y < bullet[1] < player_y + player_height:
            enemy_bullets.remove(bullet)
            player_lives -= 1

# Function to display score, level, and lives
def display_info():
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    lives_text = font.render(f"Lives: {player_lives}", True, WHITE)

    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (screen_width // 2 - 50, 10))
    screen.blit(lives_text, (screen_width - 120, 10))

# Function to reset game state for the next level
def next_level():
    global level, enemy_speed
    level += 1
    enemy_speed += 1
    create_enemies()

# Main game loop
def main_game():
    global player_x, player_y, bullets, enemy_bullets, player_lives, score, game_over

    # Initial setup
    player_x = (screen_width - player_width) // 2
    create_enemies()

    while not game_over:
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < screen_width - player_width:
            player_x += player_speed

        # Shooting bullets
        if keys[pygame.K_SPACE]:
            if len(bullets) < 3:  # Max 3 bullets on screen at a time
                bullet_x = player_x + player_width // 2 - bullet_width // 2
                bullet_y = player_y
                bullets.append([bullet_x, bullet_y])

        # Update and draw bullets
        update_bullets()
        update_enemy_bullets()

        # Draw player
        draw_player(player_x, player_y)

        # Update and draw enemies
        update_enemies()
        draw_enemies()

        # Display score, level, and lives
        display_info()

        # Check for level progression
        if score >= max_score_for_next_level:
            next_level()

        # Game over condition
        if player_lives <= 0:
            game_over = True

        # Update the display
        pygame.display.flip()

        # Frame rate
        clock.tick(60)

def gameover_splashscreen():
    screen.fill(BLACK)
    message = big_font.render("GAME OVER", True, RED)
    screen.blit(message, (screen_width // 2 - message.get_width() // 2, screen_height // 2 - 50))
    pygame.display.flip()
    time. sleep(5)
    
# Run splash screen and main game
splash_screen()
main_game()
gameover_splashscreen()
pygame.quit()
