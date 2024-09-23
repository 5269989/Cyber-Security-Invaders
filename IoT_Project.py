import pygame
import random
import RPi.GPIO as GPIO

# Initialize Pygame
pygame.init()

# GPIO setup
GPIO.setmode(GPIO.BCM)
GREEN_LED_PIN = 4  # GPIO pin 4 for the green LED
GPIO.setup(GREEN_LED_PIN, GPIO.OUT)

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
enemy_bullet_speed = 5
enemies = []
enemy_direction = 1
enemy_shoot_prob = 0.01  # Adjusted shooting probability
enemy_bullets = []

# Game variables
level = 1
total_levels = 3
game_over = False
space_invaders_completed = False

# Game clock
clock = pygame.time.Clock()

# Load images
player_image = pygame.image.load("player.png").convert_alpha()
enemy_image = pygame.image.load("enemy.png").convert_alpha()

# Scale images
player_image = pygame.transform.scale(player_image, (player_width, player_height))
enemy_image = pygame.transform.scale(enemy_image, (enemy_width, enemy_height))

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

                # Turn on the green LED when an enemy is hit
                GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
                pygame.time.delay(500)  # Wait for 500 milliseconds
                GPIO.output(GREEN_LED_PIN, GPIO.LOW)
                break

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
    global enemy_direction, game_over
    if not enemies:
        return

    edge_reached = False

    for enemy in enemies:
        enemy[0] += enemy_speed * enemy_direction

        if enemy[1] + enemy_height >= player_y:  # Game over condition
            game_over = True

        if enemy[0] <= 0 or enemy[0] + enemy_width >= screen_width:
            edge_reached = True

    if edge_reached:
        for enemy in enemies:
            enemy[1] += 20
        enemy_direction *= -1

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

def enemy_shoot():
    if enemies and random.random() < enemy_shoot_prob:  # Randomly shoot based on the probability
        enemy = random.choice(enemies)
        bullet_x = enemy[0] + enemy_width // 2 - bullet_width // 2
        bullet_y = enemy[1] + enemy_height
        enemy_bullets.append([bullet_x, bullet_y])

def display_info():
    level_text = font.render(f"Level: {level}/{total_levels}", True, WHITE)
    lives_text = font.render(f"Lives: {player_lives}", True, WHITE)
    
    screen.blit(level_text, (screen_width // 2 - level_text.get_width() // 2, 10))
    screen.blit(lives_text, (10, 10))

def next_level():
    global level, enemy_speed, enemies
    level += 1
    enemy_speed += 1
    create_enemies()

def splash_screen():
    screen.fill(BLACK)
    message = big_font.render("Cyber Security Invaders", True, RED)
    sub_message = font.render("Learn about secure passwords while defeating invaders!", True, WHITE)
    play_message = font.render("Press any key to start...", True, GREEN)
    screen.blit(message, (screen_width // 2 - message.get_width() // 2, screen_height // 2 - 100))
    screen.blit(sub_message, (screen_width // 2 - sub_message.get_width() // 2, screen_height // 2))
    screen.blit(play_message, (screen_width // 2 - play_message.get_width() // 2, screen_height // 2 + 100))
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                waiting = False

def display_game_over():
    screen.fill(RED)

    game_over_text = big_font.render("Game Over", True, WHITE)
    screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - game_over_text.get_height() // 2 - 50))

    instructions_text = font.render("Press R to Restart or Q to Quit", True, WHITE)
    screen.blit(instructions_text, (screen_width // 2 - instructions_text.get_width() // 2, screen_height // 2 + 60))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main_game()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()

def main_game():
    global player_x, player_y, bullets, enemy_bullets, player_lives, game_over, level, space_invaders_completed, last_shot_time

    player_x = (screen_width - player_width) // 2
    create_enemies()

    while not game_over:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < screen_width - player_width:
            player_x += player_speed

        current_time = pygame.time.get_ticks() / 1000
        if keys[pygame.K_SPACE]:
            if current_time - last_shot_time >= shoot_interval:
                if len(bullets) < 3:
                    bullet_x = player_x + player_width // 2 - bullet_width // 2
                    bullet_y = player_y
                    bullets.append([bullet_x, bullet_y])
                    last_shot_time = current_time

        update_bullets()
        update_enemy_bullets()
        enemy_shoot()
        draw_player(player_x, player_y)
        update_enemies()
        draw_enemies()
        display_info()

        if not enemies and level < total_levels:
            next_level()
        elif not enemies and level == total_levels:
            space_invaders_completed = True
            game_over = True

        if player_lives <= 0:
            game_over = True

        pygame.display.flip()
        clock.tick(60)

splash_screen()
main_game()

if space_invaders_completed:
    display_game_over()

# Clean up GPIO when the game ends
pygame.quit()
GPIO.cleanup()
