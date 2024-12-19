import pygame
import random
import time
import os
import platform

# Check if running on a Raspberry Pi
is_raspberry_pi = platform.system() == "Linux" and "arm" in platform.machine().lower()

if is_raspberry_pi:
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GREEN_LED_PIN = 4
    RED_LED_PIN = 17
    GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
    GPIO.setup(RED_LED_PIN, GPIO.OUT)
else:
    print("Not running on a Raspberry Pi. GPIO functionality disabled.")

pygame.init()

class Game:
    def __init__(self):
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()
        self.game_over = False
        self.level = 1
        self.total_levels = 2
        self.boss_fight = False
        self.question_limit = 3
        self.questions_asked = 0
        self.asked_questions = []
        self.last_hit_time = 0
        self.hit_duration = 1.5

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.BLUE = (0, 0, 128)

        # Fonts
        self.font = pygame.font.SysFont("Arial", 24)
        self.big_font = pygame.font.SysFont("Arial", 40)
        self.bold_font = pygame.font.SysFont("Arial", 80, bold=True)

        self.player = Player(self)
        self.boss = Boss(self)
        self.enemy_manager = EnemyManager(self)
        self.bullet_manager = BulletManager(self)
        
        # Define cybersecurity questions here for direct access
        self.cybersecurity_questions = [
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

    def main_game_loop(self):
        while not self.game_over:
            self.screen.fill(self.BLACK)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            keys = pygame.key.get_pressed()
            self.player.move(keys)
            self.player.shoot(keys)

            if self.boss_fight:
                player_hit = self.boss.update()
                self.boss.check_hit_by_player()
                if player_hit:
                    if not self.ask_cybersecurity_question():
                        self.player.lives -= 1
                        if self.player.lives == 0:
                            self.game_over_screen()
            else:
                self.enemy_manager.update()
                self.enemy_manager.draw()
                player_hit = self.bullet_manager.check_player_hit()
                if player_hit:
                    if not self.ask_cybersecurity_question():
                        self.player.lives -= 1
                        if self.player.lives == 0:
                            self.game_over_screen()

            self.player.draw()
            self.bullet_manager.update_player_bullets()
            self.bullet_manager.update_enemy_bullets()
            self.draw_ui()
            
            pygame.display.update()
            self.clock.tick(60)

    def draw_ui(self):
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, self.WHITE)
        self.screen.blit(lives_text, (10, 10))

        level_text = self.font.render(f"Level: ", True, self.WHITE)
        boss_text = self.font.render("BOSS" if self.boss_fight else str(self.level), True, self.RED if self.boss_fight else self.WHITE)
        self.screen.blit(level_text, (self.screen_width - level_text.get_width() - boss_text.get_width() - 10, 10))
        self.screen.blit(boss_text, (self.screen_width - boss_text.get_width() - 10, 10))

    def ask_cybersecurity_question(self):
        if self.questions_asked >= self.question_limit:
            return False

        self.questions_asked += 1
        available_questions = [q for q in self.cybersecurity_questions if q not in self.asked_questions]

        if not available_questions:
            return False

        question_data = random.choice(available_questions)
        self.asked_questions.append(question_data)

        question = question_data["question"]
        options = question_data["options"]
        correct_answer = question_data["answer"]

        question_lines = self.wrap_text(question, self.big_font, self.screen_width - 40)
        self.screen.fill(self.BLACK)

        total_text_height = len(question_lines) * self.big_font.get_linesize()
        y_offset = self.screen_height // 2 - 150 - total_text_height // 2
        for i, line in enumerate(question_lines):
            question_text = self.big_font.render(line, True, self.WHITE)
            self.screen.blit(question_text, (self.screen_width // 2 - question_text.get_width() // 2, y_offset + i * self.big_font.get_linesize()))

        instruction_text = self.font.render("Use arrow keys to select and Enter to submit", True, self.WHITE)
        self.screen.blit(instruction_text, (self.screen_width // 2 - instruction_text.get_width() // 2, self.screen_height // 2 + 100))

        pygame.display.flip()

        selected_index = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        selected_answer = chr(pygame.K_a + selected_index).upper()
                        if selected_answer == correct_answer:
                            self.display_feedback("Correct!", self.GREEN)
                            return True
                        else:
                            self.display_feedback("Incorrect!", self.RED)
                            return False
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(options)
                    elif event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(options)

            self.screen.fill(self.BLACK)
            for i, line in enumerate(question_lines):
                question_text = self.big_font.render(line, True, self.WHITE)
                self.screen.blit(question_text, (self.screen_width // 2 - question_text.get_width() // 2, y_offset + i * self.big_font.get_linesize()))

            option_y_start = self.screen_height // 2 - 50
            for i, option in enumerate(options):
                color = self.GREEN if i == selected_index else self.WHITE
                option_lines = self.wrap_text(option, self.font, self.screen_width - 40)
                for j, line in enumerate(option_lines):
                    option_text = self.font.render(line, True, color)
                    line_y = option_y_start + i * 60 + j * self.font.get_linesize()
                    self.screen.blit(option_text, (self.screen_width // 2 - option_text.get_width() // 2, line_y))

            self.screen.blit(instruction_text, (self.screen_width // 2 - instruction_text.get_width() // 2, self.screen_height // 2 + 150))
            pygame.display.flip()

    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = ''
        for word in words:
            test_line = current_line + word + ' '
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + ' '
        lines.append(current_line.strip())
        return lines

    def display_feedback(self, message, color):
        self.screen.fill(self.BLACK)
        feedback_text = self.bold_font.render(message, True, color)
        self.screen.blit(feedback_text, (self.screen_width // 2 - feedback_text.get_width() // 2, self.screen_height // 2 - feedback_text.get_height() // 2))
        pygame.display.flip()

        if is_raspberry_pi:
            if color == self.GREEN:
                GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
                GPIO.output(RED_LED_PIN, GPIO.LOW)
            else:
                GPIO.output(RED_LED_PIN, GPIO.HIGH)
                GPIO.output(GREEN_LED_PIN, GPIO.LOW)

        pygame.time.wait(2000)

        if is_raspberry_pi:
            GPIO.output(GREEN_LED_PIN, GPIO.LOW)
            GPIO.output(RED_LED_PIN, GPIO.LOW)

    def boss_fight_splash_screen(self):
        self.screen.fill(self.BLACK)
        boss_fight_text = self.bold_font.render("Boss Fight!", True, self.RED)
        self.screen.blit(boss_fight_text, (self.screen_width // 2 - boss_fight_text.get_width() // 2, self.screen_height // 2 - 100))
        continue_text = self.big_font.render("Press any key to continue", True, self.WHITE)
        self.screen.blit(continue_text, (self.screen_width // 2 - continue_text.get_width() // 2, self.screen_height // 2 + 50))
        pygame.display.flip()
        self.wait_for_keypress()

    def game_over_screen(self):
        self.screen.fill(self.RED)
        game_over_text = self.bold_font.render("GAME OVER!", True, self.WHITE)
        self.screen.blit(game_over_text, (self.screen_width // 2 - game_over_text.get_width() // 2, self.screen_height // 2 - 100))
        instruction_text = self.big_font.render("Press R to Restart or Q to Quit", True, self.WHITE)
        self.screen.blit(instruction_text, (self.screen_width // 2 - instruction_text.get_width() // 2, self.screen_height // 2 + 50))
        pygame.display.flip()

        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        waiting_for_input = False
                        self.show_menu()
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        quit()

    def wait_for_keypress(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    return
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

    def show_menu(self):
        menu_options = ["Start", "Leaderboard", "Instructions", "Exit"]
        selected_option = 0

        while True:
            self.screen.fill(self.BLACK)
            title_text = self.bold_font.render("Cyber Security Invaders", True, self.RED)
            self.screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 50))

            for i, option in enumerate(menu_options):
                color = self.GREEN if i == selected_option else self.WHITE
                option_text = self.big_font.render(option, True, color)
                self.screen.blit(option_text, (self.screen_width // 2 - option_text.get_width() // 2, 200 + i * 60))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if menu_options[selected_option] == "Start":
                            self.reset_game()
                            return
                        elif menu_options[selected_option] == "Leaderboard":
                            self.show_leaderboard()
                        elif menu_options[selected_option] == "Instructions":
                            self.show_instructions()
                        elif menu_options[selected_option] == "Exit":
                            pygame.quit()
                            quit()
                            
    def boss_defeated_screen(self):
        self.screen.fill(self.BLACK)
        defeated_text = self.bold_font.render("Boss Defeated!", True, self.GREEN)
        self.screen.blit(defeated_text, (self.screen_width // 2 - defeated_text.get_width() // 2, self.screen_height // 2))
        pygame.display.flip()
        pygame.time.wait(2000)  # Show for 2 seconds
        self.show_menu()  # Return to menu after showing victory screen

    def show_leaderboard(self):
        self.screen.fill(self.BLACK)
        leaderboard_text = self.big_font.render("Leaderboard Placeholder", True, self.WHITE)
        self.screen.blit(leaderboard_text, (self.screen_width // 2 - leaderboard_text.get_width() // 2, self.screen_height // 2))
        pygame.display.flip()
        self.wait_for_keypress()
        
    def level_complete_screen(self):
        self.screen.fill(self.BLACK)
        complete_text = self.bold_font.render(f"Level {self.level - 1} Complete!", True, self.GREEN)
        self.screen.blit(complete_text, (self.screen_width // 2 - complete_text.get_width() // 2, self.screen_height // 2))
        pygame.display.flip()
        pygame.time.wait(2000)  # Show for 2 seconds

    def show_instructions(self):
        self.screen.fill(self.BLACK)
        instructions = [
            "Move with arrow keys, shoot with space bar.",
            "Defend against enemies with your cybersecurity knowledge.",
            "Answer questions correctly to survive longer.",
            "Defeat the boss to win."
        ]
        y_position = 100
        for line in instructions:
            instruction_text = self.big_font.render(line, True, self.WHITE)
            self.screen.blit(instruction_text, (self.screen_width // 2 - instruction_text.get_width() // 2, y_position))
            y_position += 50
        pygame.display.flip()
        self.wait_for_keypress()

    def reset_game(self):
        self.player.lives = 3
        self.bullet_manager.player_bullets = []
        self.bullet_manager.enemy_bullets = []
        self.level = 1
        self.boss_fight = False
        self.questions_asked = 0
        self.asked_questions = []
        self.last_hit_time = 0
        self.boss.health = self.boss.max_health
        self.enemy_manager.create_enemies()
        self.main_game_loop()

class Player:
    def __init__(self, game):
        self.image = self.load_and_scale_image("player.png", (50, 50))
        self.width, self.height = self.image.get_size()
        self.x = (game.screen_width - self.width) // 2
        self.y = game.screen_height - self.height - 10
        self.speed = 5
        self.lives = 3
        self.game = game

    def load_and_scale_image(self, filename, size):
        try:
            return pygame.transform.scale(pygame.image.load(os.path.join("assets", filename)).convert_alpha(), size)
        except pygame.error as e:
            print(f"Error loading or scaling image '{filename}': {e}")
            pygame.quit()
            quit()

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        self.x = max(0, min(self.x, self.game.screen_width - self.width))

    def shoot(self, keys):
        current_time = time.time()
        if keys[pygame.K_SPACE] and current_time - self.game.bullet_manager.last_shot_time >= self.game.bullet_manager.shoot_interval:
            self.game.bullet_manager.add_player_bullet(self.x + self.width // 2, self.y)
            self.game.bullet_manager.last_shot_time = current_time

    def draw(self):
        self.game.screen.blit(self.image, (self.x, self.y))

class Boss:
    def __init__(self, game):
        self.image1 = self.load_and_scale_image("boss1.png", (150, 150))
        self.image2 = self.load_and_scale_image("boss2.png", (150, 150))
        self.width, self.height = self.image1.get_size()
        self.x = (game.screen_width - self.width) // 2
        self.y = 100
        self.speed = 3
        self.health = 100
        self.max_health = 100
        self.shoot_interval = 1.0
        self.last_shot_time = 0
        self.animation_interval = 0.5
        self.last_animation_time = 0
        self.current_image = self.image1
        self.direction = 1  # 1 for right, -1 for left
        self.game = game

    def load_and_scale_image(self, filename, size):
        try:
            return pygame.transform.scale(pygame.image.load(os.path.join("assets", filename)).convert_alpha(), size)
        except pygame.error as e:
            print(f"Error loading or scaling image '{filename}': {e}")
            pygame.quit()
            quit()

    def update(self):
        self.x += self.speed * self.direction
        if self.x <= 0 or self.x + self.width >= self.game.screen_width:
            self.direction *= -1

        current_time = time.time()
        if current_time - self.last_animation_time >= self.animation_interval:
            self.current_image = self.image2 if self.current_image == self.image1 else self.image1
            self.last_animation_time = current_time

        self.game.screen.blit(self.current_image, (self.x, self.y))
        self.draw_health_bar()

        if current_time - self.last_shot_time >= self.shoot_interval:
            self.game.bullet_manager.add_boss_bullet(self.x + self.width // 2, self.y + self.height)
            self.last_shot_time = current_time

        return self.game.bullet_manager.check_player_hit_by_boss_bullet()

    def draw_health_bar(self):
        health_width = int(200 * (self.health / self.max_health))
        pygame.draw.rect(self.game.screen, self.game.RED, (self.game.screen_width // 2 - 100, 10, 200, 20))
        pygame.draw.rect(self.game.screen, self.game.GREEN, (self.game.screen_width // 2 - 100, 10, health_width, 20))

    def check_hit_by_player(self):
        for bullet in self.game.bullet_manager.player_bullets:
            if self.x < bullet[0] < self.x + self.width and self.y < bullet[1] < self.y + self.height:
                self.game.bullet_manager.player_bullets.remove(bullet)
                self.health -= 1
                if self.health <= 0:
                    self.game.boss_defeated_screen()
                    self.game.reset_game()

class EnemyManager:
    def __init__(self, game):
        self.enemies = []
        self.enemy_image = self.load_and_scale_image("enemy.png", (40, 40))
        self.enemy_speed = 2
        self.shoot_prob = 0.003
        self.direction = 1
        self.game = game
        self.create_enemies()

    def load_and_scale_image(self, filename, size):
        try:
            return pygame.transform.scale(pygame.image.load(os.path.join("assets", filename)).convert_alpha(), size)
        except pygame.error as e:
            print(f"Error loading or scaling image '{filename}': {e}")
            pygame.quit()
            quit()

    def create_enemies(self):
        self.enemies = []
        for row in range(5):
            for col in range(10):
                enemy_x = col * (self.enemy_image.get_width() + 10) + 50
                enemy_y = row * (self.enemy_image.get_height() + 10) + 50
                self.enemies.append([enemy_x, enemy_y])

    def update(self):
        if not self.enemies:
            if self.game.level < self.game.total_levels:
                self.game.level += 1
                self.increase_difficulty()
                self.game.level_complete_screen()
                self.create_enemies()
            else:
                self.game.boss_fight_splash_screen()
                self.game.boss_fight = True

        edge_reached = False
        for enemy in self.enemies:
            enemy[0] += self.enemy_speed * self.direction
            if enemy[0] <= 0 or enemy[0] + 40 >= self.game.screen_width:
                edge_reached = True

            if random.random() < self.shoot_prob:
                self.game.bullet_manager.add_enemy_bullet(enemy[0] + 20, enemy[1] + 40)

            if enemy[1] + 40 >= self.game.screen_height:
                self.game.game_over = True
                self.game.game_over_screen()

        if edge_reached:
            for enemy in self.enemies:
                enemy[1] += 20
            self.direction *= -1

    def draw(self):
        for enemy in self.enemies:
            self.game.screen.blit(self.enemy_image, (enemy[0], enemy[1]))

    def increase_difficulty(self):
        self.enemy_speed += 0.5
        self.shoot_prob += 0.001

class BulletManager:
    def __init__(self, game):
        self.player_bullets = []
        self.enemy_bullets = []
        self.boss_bullets = []
        self.bullet_width = 5
        self.bullet_height = 10
        self.bullet_speed = 7
        self.enemy_bullet_speed = 5
        self.last_shot_time = 0
        self.shoot_interval = 0.05
        self.game = game

    def add_player_bullet(self, x, y):
        self.player_bullets.append([x, y])

    def add_enemy_bullet(self, x, y):
        self.enemy_bullets.append([x, y])

    def add_boss_bullet(self, x, y):
        self.boss_bullets.append([x, y])

    def update_player_bullets(self):
        for bullet in self.player_bullets[:]:
            bullet[1] -= self.bullet_speed
            pygame.draw.rect(self.game.screen, self.game.GREEN, (bullet[0], bullet[1], self.bullet_width, self.bullet_height))
            if bullet[1] < 0:
                self.player_bullets.remove(bullet)
            
            for enemy in self.game.enemy_manager.enemies[:]:
                if enemy[0] < bullet[0] < enemy[0] + 40 and enemy[1] < bullet[1] < enemy[1] + 40:
                    self.player_bullets.remove(bullet)
                    self.game.enemy_manager.enemies.remove(enemy)
                    break

    def update_enemy_bullets(self):
        for bullet in self.enemy_bullets[:]:
            bullet[1] += self.enemy_bullet_speed
            pygame.draw.rect(self.game.screen, self.game.RED, (bullet[0], bullet[1], self.bullet_width, self.bullet_height))
            if bullet[1] > self.game.screen_height:
                self.enemy_bullets.remove(bullet)

        for bullet in self.boss_bullets[:]:
            bullet[1] += self.enemy_bullet_speed * 2  # Boss bullets are faster
            pygame.draw.rect(self.game.screen, self.game.YELLOW, (bullet[0], bullet[1], self.bullet_width, self.bullet_height))
            if bullet[1] > self.game.screen_height:
                self.boss_bullets.remove(bullet)

    def check_player_hit(self):
        for bullet in self.enemy_bullets[:]:
            if self.game.player.x < bullet[0] < self.game.player.x + self.game.player.width and \
               self.game.player.y < bullet[1] < self.game.player.y + self.game.player.height:
                self.enemy_bullets.remove(bullet)
                self.game.last_hit_time = time.time()
                return True
        return False

    def check_player_hit_by_boss_bullet(self):
        for bullet in self.boss_bullets[:]:
            if self.game.player.x < bullet[0] < self.game.player.x + self.game.player.width and \
               self.game.player.y < bullet[1] < self.game.player.y + self.game.player.height:
                self.boss_bullets.remove(bullet)
                self.game.last_hit_time = time.time()
                return True
        return False

def main():
        game = Game()
        while True:
            game.show_menu()

main()
