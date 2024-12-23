import pygame
import random
import time
import os
import platform
import json
import math
import requests


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
pygame.mixer.init()  # Initialize the mixer for sound

class Game:
    def __init__(self):
        self.screen_width = 1000
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
        self.start_time = 0
        self.hits = 0
        self.score = 5000
        self.power_ups = PowerUpManager(self)

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.BLUE = (0, 0, 128)
        self.LIGHTBLUE = (60, 60 , 255)

        # Fonts
        self.font = pygame.font.SysFont("Arial", 24)
        self.big_font = pygame.font.SysFont("Arial", 40)
        self.bold_font = pygame.font.SysFont("Arial", 80, bold=True)

        self.player = Player(self)
        self.boss = Boss(self)
        self.enemy_manager = EnemyManager(self)
        self.bullet_manager = BulletManager(self)
        self.power_ups = PowerUpManager(self)
        
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

        # Sounds
        self.load_sounds()

    def load_sounds(self):
        self.shoot_sound = pygame.mixer.Sound(os.path.join("sounds", "shoot.wav"))
        self.hit_sound = pygame.mixer.Sound(os.path.join("sounds", "hit.wav"))
        self.correct_answer_sound = pygame.mixer.Sound(os.path.join("sounds", "correct.wav"))
        self.wrong_answer_sound = pygame.mixer.Sound(os.path.join("sounds", "wrong.wav"))
        self.level_up_sound = pygame.mixer.Sound(os.path.join("sounds", "level_up.wav"))
        self.power_up_sound = pygame.mixer.Sound(os.path.join("sounds", "power_up.wav"))

    def main_game_loop(self):
        self.start_time = time.time()
        last_score_update_time = self.start_time
        score_paused = False
        while not self.game_over:
            self.screen.fill(self.BLACK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.USEREVENT + 1:
                    # Only clear the adjustment if no new adjustment has been made
                    if hasattr(self, 'score_adjustment') and time.time() - self.score_adjustment_time >= 2:  # Only clear after 2 seconds
                        del self.score_adjustment

            keys = pygame.key.get_pressed()
            self.player.move(keys)
            self.player.shoot(keys)

            current_time = time.time()
            elapsed_time = current_time - last_score_update_time
    
            if not score_paused:
                if elapsed_time >= 1:  # Update score every second
                    self.score -= 25  # Deduct 25 points per second
                    self.score = max(0, self.score)  # Ensure score doesn't go below 0
                    last_score_update_time = current_time  # Reset for next frame

            self.player.check_invulnerability()

            if self.boss_fight:
                player_hit = self.boss.update()
                self.boss.check_hit_by_player()
                if player_hit:
                    score_paused = True
                    if not self.ask_cybersecurity_question():
                        self.player.lives -= 1
                        self.adjust_score(-250)
                        if self.player.lives == 0:
                            self.game_over_screen()
                    score_paused = False
            else:
                self.enemy_manager.update()
                self.enemy_manager.draw()
                player_hit = self.bullet_manager.check_player_hit()
                self.power_ups.update()
                if player_hit:
                    score_paused = True
                    self.hit_sound.play()
                    if not self.ask_cybersecurity_question():
                        self.player.lives -= 1
                        self.adjust_score(-250)
                        if self.player.lives == 0:
                            self.game_over_screen()
                    score_paused = False

            self.player.draw()
            self.bullet_manager.update_player_bullets()
            self.bullet_manager.update_enemy_bullets()
            self.draw_ui()
            
            pygame.display.update()
            self.clock.tick(60)

    def draw_ui(self):
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, self.WHITE)
        self.screen.blit(lives_text, (10, 10))

        score_text = self.font.render(f"Score: {self.score}", True, self.WHITE)
        self.screen.blit(score_text, (10, 40))

        level_text = self.font.render(f"Level: ", True, self.WHITE)
        boss_text = self.font.render("BOSS" if self.boss_fight else str(self.level), True, self.RED if self.boss_fight else self.WHITE)
        self.screen.blit(level_text, (self.screen_width - level_text.get_width() - boss_text.get_width() - 10, 10))
        self.screen.blit(boss_text, (self.screen_width - boss_text.get_width() - 10, 10))

        # Draw power-up notification only if active
        if self.power_ups.power_up_active:
            power_up_text = self.font.render("Power Up!", True, self.YELLOW)
            self.screen.blit(power_up_text, (self.screen_width // 2 - power_up_text.get_width() // 2, 10))
        
            # Display the name of the active power-up
            if self.power_ups.current_power_up == 'Laser':
                color = self.RED
            elif self.power_ups.current_power_up == 'Shield':
                color = self.LIGHTBLUE
            elif self.power_ups.current_power_up == 'Score Multiplier':
                color = self.GREEN
            else:
                color = self.WHITE  
            power_up_name = self.font.render(self.power_ups.current_power_up.capitalize(), True, color)
            self.screen.blit(power_up_name, (self.screen_width // 2 - power_up_name.get_width() // 2, 40))
    
        # Display score adjustments
        if hasattr(self, 'score_adjustment'):
            adjust_text = self.font.render(self.score_adjustment, True, self.RED if self.score_adjustment[0] == '-' else self.GREEN)
            self.screen.blit(adjust_text, (score_text.get_width() + 20, 40))


    def adjust_score(self, points):
        self.score = max(0, self.score + points)  # Ensure score is non-negative
    
        if points != 0:
            self.score_adjustment = f"{points:+d}"  # Store the adjustment for display
            self.score_adjustment_time = time.time()
        
            # Clear existing timer and set a new one
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Clear existing timer
            pygame.time.set_timer(pygame.USEREVENT + 1, 2000)  # Set new timer for 2 seconds

        
    def clear_bullets(self):
        """
        Clears all bullets from the game screen to allow a fresh start after answering a question or level completion.
        """
        self.bullet_manager.player_bullets.clear()
        self.bullet_manager.enemy_bullets.clear()
        self.bullet_manager.boss_bullets.clear()

    def ask_cybersecurity_question(self):
        """
        Displays a cybersecurity question and handles user input for answering.
        Returns True if the answer is correct, False otherwise.
        """
        # Ensure there are available questions
        if self.questions_asked >= self.question_limit or not self.cybersecurity_questions:
            return False

        self.questions_asked += 1
        available_questions = [q for q in self.cybersecurity_questions if q not in self.asked_questions]
        if not available_questions:
            return False

        # Select a question
        question_data = random.choice(available_questions)
        self.asked_questions.append(question_data)

        question = question_data["question"]
        options = question_data["options"]
        correct_answer = question_data["answer"]

        # Prepare to display the question
        selected_index = 0
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Check the selected answer
                        selected_answer = chr(pygame.K_a + selected_index).upper()
                        if selected_answer == correct_answer:
                            self.correct_answer_sound.play()
                            self.display_feedback("Correct!", self.GREEN)
                            self.clear_bullets()
                            return True
                        else:
                            self.wrong_answer_sound.play()
                            self.display_feedback("Incorrect!", self.RED)
                            self.clear_bullets()
                            return False
                    elif event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(options)

            # Render the question and options
            self.screen.fill(self.BLACK)

            # Render the question
            question_lines = self.wrap_text(question, self.big_font, self.screen_width - 40)
            total_text_height = len(question_lines) * self.big_font.get_linesize()
            question_y_start = self.screen_height // 3 - total_text_height // 2
            for i, line in enumerate(question_lines):
                question_text = self.big_font.render(line, True, self.WHITE)
                self.screen.blit(question_text, (self.screen_width // 2 - question_text.get_width() // 2, question_y_start + i * self.big_font.get_linesize()))

            # Render the options
            options_y_start = self.screen_height // 2
            for i, option in enumerate(options):
                color = self.GREEN if i == selected_index else self.WHITE
                option_text = self.font.render(option, True, color)
                self.screen.blit(option_text, (self.screen_width // 2 - option_text.get_width() // 2, options_y_start + i * 40))

            # Render the instruction
            instruction_text = self.font.render("Use UP/DOWN to select, ENTER to confirm.", True, self.YELLOW)
            self.screen.blit(instruction_text, (self.screen_width // 2 - instruction_text.get_width() // 2, self.screen_height - 50))

            # Update the display
            pygame.display.flip()

    def wrap_text(self, text, font, max_width):
        """
        Splits text into lines that fit within a given width.
        """
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
        # Clear player bullets and deactivate power-ups
        self.clear_bullets()
        self.power_ups.reset_power_up()
        
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
        instruction_text = self.big_font.render("Press R to Return to menu or Q to Quit", True, self.WHITE)
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
        menu_options = ["Start", "Leaderboard", "Instructions", "Save Game", "Load Game", "Exit"]
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
                            
    def save_game(self):
        game_state = {
            'level': self.level,
            'boss_fight': self.boss_fight,
            'player_lives': self.player.lives,
            'player_position': [self.player.x, self.player.y],
            'score': self.score,
            'enemies': self.enemy_manager.enemies
        }
        with open('game_save.json', 'w') as save_file:
            json.dump(game_state, save_file)
        self.display_feedback("Game Saved!", self.GREEN)

    def load_game(self):
        if not os.path.exists('game_save.json'):
            self.display_feedback("No Save File Found!", self.RED)
            return False

        with open('game_save.json', 'r') as save_file:
            game_state = json.load(save_file)
        
        self.level = game_state['level']
        self.boss_fight = game_state['boss_fight']
        self.player.lives = game_state['player_lives']
        self.player.x, self.player.y = game_state['player_position']
        self.score = game_state['score']
        self.enemy_manager.enemies = game_state['enemies']
        self.display_feedback("Game Loaded!", self.GREEN)
        return True

    def boss_defeated_screen(self):
        self.screen.fill(self.BLACK)
        defeated_text = self.bold_font.render("Boss Defeated!", True, self.GREEN)
        self.screen.blit(defeated_text, (self.screen_width // 2 - defeated_text.get_width() // 2, self.screen_height // 2 - defeated_text.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(2000)  # Show for 2 seconds
        self.end_game_screen()  # Changed to show end game screen for score input
        self.power_ups.reset_power_up()
        
    def check_server_availability(self):
        try:
            response = requests.get("http://localhost:5000/leaderboard", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
        
    def show_leaderboard(self):
        self.screen.fill(self.BLACK)
        leaderboard_title = self.big_font.render("Leaderboard", True, self.YELLOW)
        self.screen.blit(leaderboard_title, (self.screen_width // 2 - leaderboard_title.get_width() // 2, 30))
    
        smaller_font = pygame.font.SysFont("Arial", 22)
        y_position = 100

        if self.check_server_availability():
            try:
                response = requests.get("http://localhost:5000/leaderboard", timeout=5)
                if response.status_code == 200:
                    leaderboard_data = response.json()
                    for i, entry in enumerate(leaderboard_data):
                        player_text = smaller_font.render(f"{i+1}. {entry['player']} - {entry['score']} points", True, self.WHITE)
                        self.screen.blit(player_text, (self.screen_width // 2 - player_text.get_width() // 2, y_position))
                        y_position += 40
                else:
                    raise Exception("Failed to retrieve leaderboard")
            except Exception as e:
                error_text = smaller_font.render(f"Error: {str(e)}", True, self.RED)
                self.screen.blit(error_text, (self.screen_width // 2 - error_text.get_width() // 2, y_position))
        else:
            error_text = smaller_font.render("Server is not available", True, self.RED)
            self.screen.blit(error_text, (self.screen_width // 2 - error_text.get_width() // 2, y_position))

        tip = "Press any key to go back!"
        tip_text = self.font.render(tip, True, self.GREEN)
        self.screen.blit(tip_text, (self.screen_width // 2 - tip_text.get_width() // 2, self.screen_height - 50))

        pygame.display.flip()  # Update the display

        # Wait for a key press before returning to the menu
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    waiting = False
        self.show_menu()  # Return to the menu after viewing the leaderboard

    def level_complete_screen(self):
        self.screen.fill(self.BLACK)
        complete_text = self.bold_font.render(f"Level {self.level - 1} Complete!", True, self.GREEN)
        self.screen.blit(complete_text, (self.screen_width // 2 - complete_text.get_width() // 2, self.screen_height // 2 - complete_text.get_height() // 2))
        self.level_up_sound.play()
        
        # Clear player bullets and deactivate power-ups
        self.clear_bullets()
        self.power_ups.reset_power_up()  # Reset power-ups
        self.power_ups.spawn_time = time.time()  # Reset spawn timer
        self.power_ups.spawn_power_up()  # Spawn a new power-up

        pygame.display.flip()
        pygame.time.wait(2000)  # Show for 2 seconds

    def show_instructions(self):
        self.screen.fill(self.BLACK)
    
        # Title
        title = self.big_font.render("Instructions", True, self.YELLOW)
        title_x = self.screen_width // 2 - title.get_width() // 2
        self.screen.blit(title, (title_x, 20))

        # Instructions
        instructions = [
            ("Controls", "Use arrow keys to move, Spacebar to shoot"),
            ("Objective", "Survive waves of cyber enemies by shooting them down"),
            ("Health", "Lose lives when hit; answer questions to mitigate damage"),
            ("Levels", f"Progress through {self.total_levels} levels to face the Boss"),
            ("Scoring", "Score decreases over time but increases with hits"),
            ("Boss Fight", "Answer questions correctly to defeat the boss"),
            ("Game Over", "Game ends when lives reach zero or if you defeat the Boss")
        ]

        # Layout for instructions
        y_pos = 80
        for title, content in instructions:
            title_text = self.font.render(title + ":", True, self.RED)
            content_text = self.font.render(content, True, self.WHITE)
            title_x = self.screen_width // 2 - (title_text.get_width() + content_text.get_width() + 5) // 2
            self.screen.blit(title_text, (title_x, y_pos))
            self.screen.blit(content_text, (title_x + title_text.get_width() + 5, y_pos))
            y_pos += title_text.get_height() + 5

        # Power-ups title
        power_ups_title = self.font.render("Power-ups:", True, self.RED)
        power_ups_title_x = self.screen_width // 2 - power_ups_title.get_width() // 2
        self.screen.blit(power_ups_title, (power_ups_title_x, y_pos + 20))
    
        # Power-ups explanation
        power_ups = [
            ("Laser", self.RED, "Longer, faster, and more frequent shots"),
            ("Shield", (self.LIGHTBLUE), "Temporary invulnerability"),
            ("Triple Shot", self.GREEN, "Shoot three bullets at once")
        ]
    
        # Calculate starting position for power-ups
        power_up_y = y_pos + 50  # Space for title
        for name, color, effect in power_ups:
            name_text = self.font.render(f"- {name}", True, color)
            effect_text = self.font.render(effect, True, self.WHITE)
            name_x = self.screen_width // 2 - (name_text.get_width() + effect_text.get_width() + 5) // 2
            self.screen.blit(name_text, (name_x, power_up_y))
            self.screen.blit(effect_text, (name_x + name_text.get_width() + 5, power_up_y))
            power_up_y += name_text.get_height() + 5

        # Navigation
        back_text = self.font.render("Press any key to go back", True, self.YELLOW)
        back_x = self.screen_width // 2 - back_text.get_width() // 2
        self.screen.blit(back_text, (back_x, self.screen_height - 40))

        pygame.display.flip()
        self.wait_for_keypress()

    def reset_game(self):
        """
        Resets the game to its initial state.
        """
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
        self.hits = 0
        self.score = 5000
        self.power_ups.reset_power_up()

        # Clear any existing score adjustments
        if hasattr(self, 'score_adjustment'):
            del self.score_adjustment

        # Reset timers for score adjustment and game state
        pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Stop any ongoing timers

        self.main_game_loop()
               
    def end_game_screen(self):
        self.screen.fill(self.BLACK)
    
        # Game Over Text
        end_text = self.bold_font.render(f"Game Over! Your Score is: {self.score}", True, self.YELLOW)
        self.screen.blit(end_text, (self.screen_width // 2 - end_text.get_width() // 2, self.screen_height // 3 - end_text.get_height() // 2))
    
        # Name Prompt
        name_prompt = self.big_font.render("Enter your name (3 letters):", True, self.WHITE)
        self.screen.blit(name_prompt, (self.screen_width // 2 - name_prompt.get_width() // 2, self.screen_height // 2 - 30))

        # Input Box
        input_box = pygame.Rect(self.screen_width // 2 + 0, self.screen_height // 2 + 30, 50, 32)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color(self.GREEN)
        color = color_active  # Active by default
        text = ''

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if len(text) == 3:
                            self.save_score(text.upper(), self.score)
                            return
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    elif len(text) < 3 and event.unicode.isalpha():
                        text += event.unicode

            # Draw input box
            pygame.draw.rect(self.screen, color, input_box)
        
            # Draw text inside the box
            txt_surface = self.font.render(text, True, self.BLACK)
            width = max(30, txt_surface.get_width()+10)
            input_box.w = width
            self.screen.blit(txt_surface, (input_box.x+5, input_box.y+5))

            pygame.display.flip()
            
        self.power_ups.reset_power_up()
            
    def save_score(self, name, score):
        if self.check_server_availability():
            try:
                payload = {'player_name': name, 'score': score}
                response = requests.post("http://localhost:5000/submit_score", json=payload, timeout=5)
                if response.status_code != 200:
                    raise Exception(f"Failed to submit score. Status code: {response.status_code}")
                else:
                    self.display_feedback("Score submitted successfully", self.GREEN)
                    self.show_menu()
            except requests.RequestException as e:
                self.display_feedback(f"Network Error: {str(e)}", self.RED)
            except Exception as e:
                self.display_feedback(f"Error: {str(e)}", self.RED)
        else:
            self.display_feedback("Server is not available", self.RED)
        
class Player:
    def __init__(self, game):
        self.image = self.load_and_scale_image("player.png", (50, 50))
        self.width, self.height = self.image.get_size()
        self.x = (game.screen_width - self.width) // 2
        self.y = game.screen_height - self.height - 10
        self.speed = 5
        self.lives = 3
        self.game = game
        self.invulnerable = False  # Initialize invulnerability state
        self.invulnerable_timer = 0
        self.invulnerable_duration = 5  # Duration in seconds for invulnerability
        self.shield_outline = self.create_shield_outline()


    def load_and_scale_image(self, filename, size):
        try:
            return pygame.transform.scale(pygame.image.load(os.path.join("assets", filename)).convert_alpha(), size)
        except pygame.error as e:
            print(f"Error loading or scaling image '{filename}': {e}")
            pygame.quit()
            quit()

    def create_shield_outline(self):
        outline_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        player_mask = pygame.mask.from_surface(self.image)
        dark_blue = (60, 60 , 180, 255)  # Darker blue for the outline

        for x in range(self.width):
            for y in range(self.height):
                if player_mask.get_at((x, y)):
                    # Check if this pixel is on or near the edge of the shape
                    for dx in range(-2, 3):  # Check 2 pixels in each direction
                        for dy in range(-2, 3):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.width and 0 <= ny < self.height and not player_mask.get_at((nx, ny)):
                                # Set color for a thicker outline
                                outline_surface.set_at((x, y), dark_blue)
                                # Optionally, set color for adjacent pixels to make it even thicker
                                for i in range(-1, 2):
                                    for j in range(-1, 2):
                                        nx2, ny2 = x + i, y + j
                                        if 0 <= nx2 < self.width and 0 <= ny2 < self.height:
                                            outline_surface.set_at((nx2, ny2), dark_blue)
                                break  # Break after setting one outline pixel to prevent overwriting
                        else:
                            continue
                        break

        return outline_surface    

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        self.x = max(0, min(self.x, self.game.screen_width - self.width))

    def shoot(self, keys):
        current_time = time.time()
        if keys[pygame.K_SPACE] and current_time - self.game.bullet_manager.last_shot_time >= self.game.bullet_manager.player_shoot_interval:
            self.game.bullet_manager.add_player_bullet(self.x + self.width // 2, self.y)
            self.game.bullet_manager.last_shot_time = current_time
            self.game.shoot_sound.play()

    def draw(self):
        self.game.screen.blit(self.image, (self.x, self.y))
        
        if self.invulnerable:
            if int(time.time() * 5) % 2 == 0:  # Flash every 0.2 seconds
                self.game.screen.blit(self.shield_outline, (self.x, self.y))
                
    def set_invulnerable(self, duration=None):
        self.invulnerable = True
        self.invulnerable_timer = time.time()
        if duration:
            self.invulnerable_duration = duration
            
    def check_invulnerability(self):
        if self.invulnerable:
            current_time = time.time()
            if current_time - self.invulnerable_timer >= self.invulnerable_duration:
                self.invulnerable = False

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
        self.player_bullet_height = 10  # Default height for player bullets
        self.enemy_bullet_height = 10   # New attribute for enemy bullet height
        self.player_bullet_speed = 7
        self.enemy_bullet_speed = 5
        self.player_shoot_interval = 0.2  # Default shoot interval for player
        self.last_shot_time = 0
        self.game = game
        self.angle = math.radians(20)
        self.triple_shot = False

    def add_player_bullet(self, x, y):
        if self.triple_shot:
            # Middle bullet (straight ahead)
            self.player_bullets.append([x, y, self.player_bullet_height, 0])  # angle 0 means straight up
            
            # Left bullet (20 degrees to the left)
            self.player_bullets.append([x - 10, y, self.player_bullet_height, -self.angle])  
            
            # Right bullet (20 degrees to the right)
            self.player_bullets.append([x + 10, y, self.player_bullet_height, self.angle])
        else:
            self.player_bullets.append([x, y, self.player_bullet_height, 0])  # Single shot straight up

    def add_enemy_bullet(self, x, y):
        self.enemy_bullets.append([x, y])

    def add_boss_bullet(self, x, y):
        self.boss_bullets.append([x, y])

    def update_player_bullets(self):
        for bullet in self.player_bullets[:]:
            x, y, height, angle = bullet
            
            # Move bullet based on its angle
            if angle == 0:  # Straight up
                bullet[1] -= self.player_bullet_speed
            else:
                # Calculate movement based on angle
                bullet[0] += self.player_bullet_speed * math.sin(angle)  # Horizontal movement
                bullet[1] -= self.player_bullet_speed * math.cos(angle)  # Vertical movement

            # Calculate points for drawing a rotated rectangle
            # Here we're using the bullet's height as its length in the direction of travel
            rect_points = [
                (x, y),
                (x + height * math.sin(angle), y - height * math.cos(angle)),
                (x + self.bullet_width * math.cos(angle) + height * math.sin(angle), y + self.bullet_width * math.sin(angle) - height * math.cos(angle)),
                (x + self.bullet_width * math.cos(angle), y + self.bullet_width * math.sin(angle))
            ]

            # Draw the rotated rectangle
            pygame.draw.polygon(self.game.screen, self.game.GREEN, rect_points)

            # Remove bullet if it's off-screen
            if bullet[1] < 0 or bullet[0] < 0 or bullet[0] > self.game.screen_width:
                self.player_bullets.remove(bullet)
            
            # Check for collision with enemies
            for enemy in self.game.enemy_manager.enemies[:]:
                # Simplified collision detection; for accuracy, consider using a more complex method
                if (enemy[0] < x < enemy[0] + 40 and enemy[1] < y < enemy[1] + 40) or \
                   (enemy[0] < x + height * math.sin(angle) < enemy[0] + 40 and enemy[1] < y - height * math.cos(angle) < enemy[1] + 40):
                    self.player_bullets.remove(bullet)
                    self.game.enemy_manager.enemies.remove(enemy)
                    break

    def update_enemy_bullets(self):
        for bullet in self.enemy_bullets[:]:
            bullet[1] += self.enemy_bullet_speed
            pygame.draw.rect(self.game.screen, self.game.RED, (bullet[0], bullet[1], self.bullet_width, self.enemy_bullet_height))
            if bullet[1] > self.game.screen_height:
                self.enemy_bullets.remove(bullet)
                
            if self.game.player.invulnerable and \
                   self.game.player.x < bullet[0] < self.game.player.x + self.game.player.width and \
                   self.game.player.y < bullet[1] < self.game.player.y + self.game.player.height:
                    self.enemy_bullets.remove(bullet)  # Bullet is removed if it hits the shield

        for bullet in self.boss_bullets[:]:
            bullet[1] += self.enemy_bullet_speed * 2  # Boss bullets are faster
            pygame.draw.rect(self.game.screen, self.game.YELLOW, (bullet[0], bullet[1], self.bullet_width, self.enemy_bullet_height))
            if bullet[1] > self.game.screen_height:
                self.boss_bullets.remove(bullet)
                
            # Check if boss bullet hits the player's shield
            if self.game.player.invulnerable and \
               self.game.player.x < bullet[0] < self.game.player.x + self.game.player.width and \
               self.game.player.y < bullet[1] < self.game.player.y + self.game.player.height:
                self.boss_bullets.remove(bullet)  # Bullet is removed if it hits the shield
        

    def check_player_hit(self):
        for bullet in self.enemy_bullets[:]:
            if (self.game.player.x < bullet[0] < self.game.player.x + self.game.player.width and 
                self.game.player.y < bullet[1] < self.game.player.y + self.game.player.height):
                if not self.game.player.invulnerable:
                    self.enemy_bullets.remove(bullet)
                    self.game.last_hit_time = time.time()
                    return True
        return False

    def reset_triple_shot(self):
        self.triple_shot = False

    def check_player_hit_by_boss_bullet(self):
        for bullet in self.boss_bullets[:]:
            if (self.game.player.x < bullet[0] < self.game.player.x + self.game.player.width and 
                self.game.player.y < bullet[1] < self.game.player.y + self.game.player.height):
                if not self.game.player.invulnerable:
                    self.boss_bullets.remove(bullet)
                    self.game.last_hit_time = time.time()
                    return True
        return False

class PowerUpManager:
    def __init__(self, game):
        self.spawn_time = 0
        self.spawn_interval = 15  # seconds between power-ups
        self.power_ups = []
        self.game = game
        self.power_up_active = False
        self.power_up_timer = 0
        self.current_power_up = None
        self.last_level_check = 1
        self.is_first_level = True  # New flag for first level

    def update(self):
        current_time = time.time()
        
        # Handling for the first level
        if self.is_first_level:
            if not self.power_ups:
                self.spawn_power_up()
                self.is_first_level = False
        
        # Check if a new level has started (excluding first level)
        elif self.game.level != self.last_level_check:
            self.power_ups.clear()  # Clear old power-ups
            self.spawn_power_up()  # Spawn new power-up
            self.spawn_time = current_time  # Reset the timer
            self.last_level_check = self.game.level  # Update the last checked level

        # Normal spawn conditions for non-boss levels when no power-up is active
        if not self.game.boss_fight and not self.power_up_active:
            if not self.power_ups and current_time - self.spawn_time >= self.spawn_interval:
                self.spawn_power_up()
                self.spawn_time = current_time

        # Update existing power-up
        if self.power_ups:
            power_up = self.power_ups[0]
            power_up[1] += 2  # Move downwards
            if power_up[1] > self.game.screen_height:
                self.power_ups.clear()  # Remove power-up if it goes off screen
            else:
                pygame.draw.circle(self.game.screen, self.game.BLUE, (int(power_up[0]), int(power_up[1])), 10)

            # Check for collision with player
            if (self.game.player.x < power_up[0] < self.game.player.x + self.game.player.width and 
                self.game.player.y < power_up[1] < self.game.player.y + self.game.player.height):
                self.power_ups.clear()
                self.apply_power_up()

        # Deactivate power-up after duration
        if self.power_up_active:
            if current_time - self.power_up_timer > 5:  # Duration of power-up
                self.reset_power_up()

    def spawn_power_up(self):
        if not self.power_ups:  # Ensure only one power-up spawns at a time
            x = random.randint(0, self.game.screen_width - 20)
            y = 0
            self.power_ups = [[x, y]]

    def apply_power_up(self):
        self.power_up_active = True
        self.power_up_timer = time.time()
        
        power_up_types = ['Laser', 'Shield', 'TripleShot']
        self.current_power_up = random.choice(power_up_types)
        
        if self.current_power_up == 'Laser':
            self.game.bullet_manager.player_bullet_height = 30
            self.game.bullet_manager.player_bullet_speed = 35
            self.game.bullet_manager.player_shoot_interval = 0.005
        elif self.current_power_up == 'Shield':
            self.game.player.set_invulnerable()  # Changed from directly setting invulnerable to using a method
        elif self.current_power_up == 'TripleShot':
            self.game.bullet_manager.triple_shot = True

        self.game.adjust_score(250)  
        self.game.power_up_sound.play()

    def reset_power_up(self):
        """
        Resets all active power-up effects and prepares for the next spawn.
        """
        self.power_up_active = False
        self.current_power_up = None
        self.power_ups.clear()
        self.spawn_time = time.time()  # Reset the spawn timer

        # Reset specific power-up effects
        self.game.bullet_manager.player_bullet_height = 10  # Default bullet height
        self.game.bullet_manager.player_bullet_speed = 7    # Default bullet speed
        self.game.bullet_manager.player_shoot_interval = 0.2  # Default shoot interval
        self.game.bullet_manager.triple_shot = False  # Disable TripleShot
        self.game.player.invulnerable = False  # Disable Shield


def main():
    game = Game()
    while True:
        game.show_menu()

if __name__ == "__main__":
    main()

