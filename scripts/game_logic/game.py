import pygame
import platform
import random
import time
import os
import json
import math
import requests
import datetime
from threading import Thread
from requests.auth import HTTPBasicAuth
from scripts.game_logic.player import Player
from scripts.game_logic.boss import Boss
from scripts.game_logic.enemy_manager import EnemyManager
from scripts.game_logic.bullet_manager import BulletManager
from scripts.game_logic.powerup_manager import PowerUpManager
from scripts.game_logic.minigame import HackingMiniGame

def get_asset_path(*path_parts):
    """Returns the absolute path for an asset based on the project root."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", *path_parts))

class Game:
    def __init__(self):
        self.is_raspberry_pi = platform.system() == "Linux" and "arm" in platform.machine().lower()
        self.screen_width = 1200
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
        self.paused = False
        self.save_slots = [None, None, None]  # Stores 3 save games
        self.selected_save_slot = 0
        self.loaded_from_menu = False
        self.save_name_input = ""
        self.current_music = None  # Track currently playing music
        self.save_slots = [None, None, None]  # Default empty save slots
        self.load_saves_from_file()  # Load saves when game starts
        self.init_gpio()
        self.cheat_codes = {
            "D4A52B11": "invincible",
            "C3B89A22": "infinite_ammo"
        }
        self.active_cheats = set()
        if self.is_raspberry_pi:
            self.init_rfid()

        
        
        if self.is_raspberry_pi:
            self.display_score_front = 5000  # Value shown on display
            self.display_score_back = 5000   # Buffered updates
            self.display_update_flag = False
            self.display_lock = threading.Lock()
            self.start_display_thread()
            
            def init_rfid(self):
                from mfrc522 import SimpleMFRC522
                self.reader = SimpleMFRC522()
                self.rfid_thread = threading.Thread(target=self.check_rfid)
                self.rfid_thread.daemon = True
                self.rfid_thread.start()
                
            def check_rfid(self):
                while True:
                    try:
                        id, text = self.reader.read_no_block()
                        if id and str(id) in self.cheat_codes:
                            self.handle_cheat(self.cheat_codes[str(id)])
                        time.sleep(1)
                    except Exception as e:
                        print("RFID Error:", e)
                        
            def handle_cheat(self, cheat):
                self.active_cheats.add(cheat)
                if cheat == "invincible":
                    self.player.set_invulnerable(duration=99999)
                elif cheat == "infinite_ammo":
                    self.bullet_manager.player_shoot_interval = 0.01
            
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.BLUE = (0, 0, 128)
        self.LIGHTBLUE = (60, 60 , 255)

        #Title
        self.title_image = pygame.image.load("assets/fonts/Title.png")

        # Fonts
        self.font = pygame.font.Font("assets/fonts/TextFont.ttf", 18)
        self.big_font = pygame.font.Font("assets/fonts/TextFont.ttf", 23)
        self.bold_font = pygame.font.Font("assets/fonts/TextFont.ttf", 40)
        self.title_font = pygame.font.Font("assets/fonts/TextFont.ttf", 30)  


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
        
        self.load_menu_background()
        
        if self.is_raspberry_pi:
            self.start_display_thread()

    def init_gpio(self):
        if self.is_raspberry_pi:
            import RPi.GPIO as GPIO, threading
            from threading import Event
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
    
            GREEN_LED_PIN = 20
            RED_LED_PIN = 21
    

            # Define the GPIO pins connected to segments and digits
            D4 = 16
            D3 = 25
            D2 = 26
            D1 = 5

            SEGMENT_A = 4
            SEGMENT_F = 17
            SEGMENT_B = 18
            SEGMENT_E = 22
            SEGMENT_D = 23
            SEGMENT_C = 24
            SEGMENT_G = 27 

            GPIO.setmode(GPIO.BCM)  
            pins = [SEGMENT_A, SEGMENT_F, SEGMENT_B, SEGMENT_E, SEGMENT_D, SEGMENT_C, SEGMENT_G, D1, D2, D3, D4, GREEN_LED_PIN, RED_LED_PIN]
            GPIO.setup(pins, GPIO.OUT, initial=GPIO.LOW)

            # Digit to segment mapping (0-9)
            digit_to_segments = {
                '0': [0,0,0,0,0,0,1],
                '1': [1,0,0,1,1,1,1],  
                '2': [0,0,1,0,0,1,0],
                '3': [0,0,0,0,1,1,0],
                '4': [1,0,0,1,1,0,0],  
                '5': [0,1,0,0,1,0,0],  
                '6': [0,1,0,0,0,0,0],
                '7': [0,0,0,1,1,1,1],
                '8': [0,0,0,0,0,0,0],
                '9': [0,0,0,0,1,0,0]
            }

            # Function to display a 4-digit number on the 7-segment display
            def display_number_on_7seg(number):
                digits = str(number).zfill(4)  # Ensure the number is 4 digits long
                start_time = time.perf_counter()
                for i, digit in enumerate(digits):
                    # Select the appropriate digit to display
            
                    digit_pins = [D1, D2, D3, D4]
                    GPIO.output(digit_pins[i], GPIO.HIGH)  # Activate current digit
            
                    # Turn on/off the segments based on the digit
                    segments = digit_to_segments[digit]
                    GPIO.output(SEGMENT_A, GPIO.HIGH if segments[0] == 1 else GPIO.LOW)
                    GPIO.output(SEGMENT_B, GPIO.HIGH if segments[1] == 1 else GPIO.LOW)
                    GPIO.output(SEGMENT_C, GPIO.HIGH if segments[2] == 1 else GPIO.LOW)
                    GPIO.output(SEGMENT_D, GPIO.HIGH if segments[3] == 1 else GPIO.LOW)
                    GPIO.output(SEGMENT_E, GPIO.HIGH if segments[4] == 1 else GPIO.LOW)
                    GPIO.output(SEGMENT_F, GPIO.HIGH if segments[5] == 1 else GPIO.LOW)
                    GPIO.output(SEGMENT_G, GPIO.HIGH if segments[6] == 1 else GPIO.LOW)
            
                    # Turn off other digits to avoid overlap
                    for j in range(4):
                        if j != i:
                            GPIO.output(digit_pins[j], GPIO.LOW)
            
                    while time.perf_counter() - start_time < 0.001 * (i + 1):
                        pass

                # Turn off all digits after displaying
                GPIO.output(D1, GPIO.LOW)
                GPIO.output(D2, GPIO.LOW)
                GPIO.output(D3, GPIO.LOW)
                GPIO.output(D4, GPIO.LOW)

        else:
            print("Not running on RPi, GPIO functionality disabled.")
            


  
    def load_sounds(self):
        """Loads game sound effects and background music safely."""
        # Background Music Paths
        self.menu_music = get_asset_path("assets", "sounds", "background_music", "menu_music.wav")
        self.level_music = get_asset_path("assets", "sounds", "background_music", "level_music.wav")
        self.boss_music = get_asset_path("assets", "sounds", "background_music", "boss_music.wav")
        self.game_over_music = get_asset_path("assets", "sounds", "background_music", "game_over.wav")
        self.boss_defeated_music = get_asset_path("assets", "sounds", "background_music", "boss_defeated.wav")

        # Check if music files exist before loading them
        for music_file in [self.menu_music, self.level_music, self.boss_music, self.game_over_music, self.boss_defeated_music]:
            if not os.path.exists(music_file):
                print(f"🚨 Warning: Music file missing -> {music_file}")

        # Sound Effect Paths
        self.shoot_sound = pygame.mixer.Sound(get_asset_path("assets", "sounds", "shoot.wav"))
        self.hit_sound = pygame.mixer.Sound(get_asset_path("assets", "sounds", "hit.wav"))
        self.correct_answer_sound = pygame.mixer.Sound(get_asset_path("assets", "sounds", "correct.wav"))
        self.wrong_answer_sound = pygame.mixer.Sound(get_asset_path("assets", "sounds", "wrong.wav"))
        self.level_up_sound = pygame.mixer.Sound(get_asset_path("assets", "sounds", "level_up.wav"))
        self.power_up_sound = pygame.mixer.Sound(get_asset_path("assets", "sounds", "power_up.wav"))


        #Set volume (adjust as needed)
        pygame.mixer.music.set_volume(0.8)

    def load_menu_background(self):
        # Load animated menu backgrounds
        self.menu_backgrounds = [
            pygame.image.load("assets/backgrounds/menu_background1.png"),
            pygame.image.load("assets/backgrounds/menu_background2.png"),
            pygame.image.load("assets/backgrounds/menu_background3.png")
        ]
        self.menu_background_index = 0  # Start with the first background
        self.last_bg_update = time.time()  # Track time for animation
        self.bg_animation_interval = 1  # Change background every 0.2 seconds

    def start_display_thread(self):
        self.display_running = True  # Initialize the flag
        self.display_thread = threading.Thread(target=self.update_7seg_display)
        self.display_thread.daemon = True
        self.display_thread.start()
    
    def change_music(self, new_track):
        """Stops current music and plays a new track safely."""
        if not os.path.exists(new_track):  # Check if file exists
            print(f"Music file not found: {new_track}")  # Debugging info
            return  # Exit function to prevent crash

        if self.current_music != new_track:  # Avoid restarting the same track
            pygame.mixer.music.stop()
            pygame.mixer.music.load(new_track)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            self.current_music = new_track  # Track current music

    def update_7seg_display(self):
        digit_pins = [D1, D2, D3, D4]
        try:
            while self.display_running:
                with self.display_lock:
                    current_score = self.display_score_front
                digits = f"{current_score:04d}"
            
                for i in range(4):
                    # Activate the current digit
                    GPIO.output(digit_pins[i], GPIO.HIGH)
                    segments = digit_to_segments[digits[i]]
                    # Set each segment
                    GPIO.output(SEGMENT_A, GPIO.HIGH if segments[0] else GPIO.LOW)
                    GPIO.output(SEGMENT_B, GPIO.HIGH if segments[1] else GPIO.LOW)
                    GPIO.output(SEGMENT_C, GPIO.HIGH if segments[2] else GPIO.LOW)
                    GPIO.output(SEGMENT_D, GPIO.HIGH if segments[3] else GPIO.LOW)
                    GPIO.output(SEGMENT_E, GPIO.HIGH if segments[4] else GPIO.LOW)
                    GPIO.output(SEGMENT_F, GPIO.HIGH if segments[5] else GPIO.LOW)
                    GPIO.output(SEGMENT_G, GPIO.HIGH if segments[6] else GPIO.LOW)
                    # Hold the digit for a short time
                    time.sleep(0.001)
                    # Deactivate the digit
                    GPIO.output(digit_pins[i], GPIO.LOW)
        except KeyboardInterrupt:
            self.display_running = False
            GPIO.cleanup()

    def display_changed_segments(self, number):
        # Only update what has changed
        new_digits = str(number).zfill(4)
        for i, digit in enumerate(new_digits):
            if digit != str(self.display_score).zfill(4)[i]:
                self.changed_segments.add(i)
        for i in self.changed_segments:
            self.display_digit(i, new_digits[i])
        self.changed_segments.clear()
        
    def display_digit(self, position, digit):
        digit_pins = [D1, D2, D3, D4]
        GPIO.output(digit_pins[position], GPIO.HIGH)  # Activate current digit
        segments = digit_to_segments[digit]
        for j, segment in enumerate([SEGMENT_A, SEGMENT_B, SEGMENT_C, SEGMENT_D, SEGMENT_E, SEGMENT_F, SEGMENT_G]):
            GPIO.output(segment, GPIO.HIGH if segments[j] == 1 else GPIO.LOW)
        for j in range(4):
            if j != position:
                GPIO.output(digit_pins[j], GPIO.LOW)

    def adjust_score(self, points):
        with self.display_lock:  # Ensure atomic update
            self.score = max(0, self.score + points)
            self.display_score_back = self.score
            self.display_update_flag = True
            
    def __del__(self):
        if self.is_raspberry_pi:
            self.display_running = False
            self.display_thread.join()
            GPIO.cleanup()

    def main_game_loop(self):
        self.change_music(self.level_music)  # Start level music
        self.start_time = time.time()
        minigamecompleted = False
        last_score_update_time = self.start_time
        score_paused = False
        while not self.game_over:
            self.screen.fill(self.BLACK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused  
                if event.type == pygame.USEREVENT + 1:
                    if hasattr(self, 'score_adjustment') and time.time() - self.score_adjustment_time >= 2:
                        del self.score_adjustment
                if self.paused:
                    self.power_ups.pause_powerups()
                    self.draw_pause_menu() 
                    continue

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
            if keys[pygame.K_ESCAPE]:
                self.paused = not self.paused
            self.player.check_invulnerability()
            if self.boss_fight:
                self.change_music(self.boss_music)  # Start boss music
                self.boss.update()
                if minigamecompleted == False:
                    self.check_minigame_trigger()
                if self.boss_fight:
                    player_hit = self.bullet_manager.check_player_hit_by_boss_bullet()
                else:
                    player_hit = self.bullet_manager.check_player_hit()
                if player_hit:
                    score_paused = True
                    if not self.ask_cybersecurity_question():
                        self.player.lives -= 1
                        self.adjust_score(-250)
                        score_paused = False
                        if self.player.lives == 0:
                            self.game_over_screen()
                    else:
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
                        score_paused = False
                        if self.player.lives == 0:
                            self.game_over_screen()
                            score_paused = False
                    else:
                        score_paused = False
            self.player.draw()
            self.bullet_manager.update_player_bullets()
            self.bullet_manager.update_enemy_bullets()
            self.bullet_manager.update_boss_bullets()
            self.draw_ui()
            # Handle 7-segment display
            if self.is_raspberry_pi:
                if self.score != self.display_score:  # If score has changed
                    with self.lock:
                        self.display_score = self.score
                        self.display_update_event.set()
            pygame.display.update()
            self.clock.tick(60)

    def check_minigame_trigger(self):
        if self.boss.health <= (self.boss.max_health // 2) and not self.boss.minigame_triggered:
            self.boss.minigame_triggered = True 
            success = HackingMiniGame(self).run()
            if not success:
                self.boss.shoot_interval *= 0.8
                self.boss.rage_mode = True
                self.display_feedback("BOSS ENRAGED!", self.RED)
            else:
                self.display_feedback("Firewall Breached!", self.GREEN)

    def draw_pause_menu(self):
        menu_options = ["Resume", "Save Game", "Return to Menu"]

        selected_option = 0  # Track selected option
        while self.paused:
            # Draw game background first
            self.screen.fill(self.BLACK)
 
                # Draw enemies or boss based on current game state
            if self.boss_fight:
                # Draw boss and health bar
                self.screen.blit(self.boss.current_image, (self.boss.x, self.boss.y))
                health_width = int(200 * (self.boss.health / self.boss.max_health))
                pygame.draw.rect(self.screen, self.RED, (self.screen_width // 2 - 100, 40, 200, 20))
                pygame.draw.rect(self.screen, self.GREEN, (self.screen_width // 2 - 100, 40, health_width, 20))
            else:
                self.enemy_manager.draw()

            # Draw player, enemies, bullets, and power-ups
            self.player.draw()
            self.enemy_manager.draw()
            self.bullet_manager.update_player_bullets(draw_only=True)
            self.bullet_manager.update_enemy_bullets(draw_only=True)
            self.bullet_manager.update_boss_bullets(draw_only=True)

             # *** Manually draw power-ups without updating them ***
            for power_up in self.power_ups.power_ups:
                pygame.draw.circle(self.screen, self.BLUE, (int(power_up[0]), int(power_up[1])), 10)
        
            # Draw pause menu overlay
            menu_background = pygame.Surface((400, 300))
            menu_background.fill(self.BLACK)
            pygame.draw.rect(menu_background, self.WHITE, menu_background.get_rect(), 2)
            self.screen.blit(menu_background, (self.screen_width//2 - 200, 150))
        
            # Add PAUSED text
            paused_text = self.bold_font.render("PAUSED", True, self.WHITE)
            self.screen.blit(paused_text, (self.screen_width//2 - paused_text.get_width()//2, 155))
        
            # Draw menu items
            for i, option in enumerate(menu_options):
                y = 250 + i*60
                color = self.GREEN if i == selected_option else self.WHITE
                option_text = self.big_font.render(option, True, color)
                self.screen.blit(option_text, (self.screen_width//2 - option_text.get_width()//2, y))
        
            pygame.display.flip()
        
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = False  # Exit pause menu on ESC
                        return
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                    elif event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if menu_options[selected_option] == "Resume":
                            self.paused = False
                            self.power_ups.resume_powerups()
                            return
                        elif menu_options[selected_option] == "Save Game":
                            self.show_save_slot_menu()
                        elif menu_options[selected_option] == "Return to Menu":
                            self.reset_game_state()
                            self.show_menu()
                    elif event.key == pygame.K_ESCAPE:
                        self.paused = False
                        return

    def show_save_slot_menu(self):
        selected_slot = 0
        name_input = ""
    
        while True:
            self.screen.fill(self.BLACK)
            title = self.big_font.render("Select Save Slot", True, self.YELLOW)
            self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 50))
        
            # Draw slots
            slot_y = 150
            for i in range(3):
                slot_rect = pygame.Rect(200, slot_y, 800, 100)
                color = self.GREEN if i == selected_slot else self.WHITE
                pygame.draw.rect(self.screen, color, slot_rect, 2)
            
                if self.save_slots[i]:
                    save = self.save_slots[i]
                    info_text = f"{save['name']} - Level {save['level']} | {save['timestamp']}"
                else:
                    info_text = "Empty Slot!"
            
                text_surf = self.font.render(info_text, True, color)
                self.screen.blit(text_surf, (220, slot_y + 35))
                slot_y += 120

            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_slot = (selected_slot + 1) % 3
                    elif event.key == pygame.K_UP:
                        selected_slot = (selected_slot - 1) % 3
                    elif event.key == pygame.K_RETURN:
                        if self.save_slots[selected_slot] is None:
                            # Show name input for new saves
                            self.get_save_name(selected_slot)
                            return
                        else:
                            # Overwrite existing save
                            self.get_save_name(selected_slot)
                            return
                    elif event.key == pygame.K_ESCAPE:
                        return

            pygame.display.flip()

    def delete_all_saves(self):
        confirm_text = self.font.render("Confirm delete ALL saves? (Y/N)", True, self.RED)
        self.screen.blit(confirm_text, (self.screen_width//2 - 150, 400))
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        try:
                            self.save_slots = [None, None, None]
                            with open('saves.json', 'w') as f:
                                json.dump(self.save_slots, f)
                            self.display_feedback("All saves deleted!", self.RED)
                            return
                        except Exception as e:
                            print(f"Error deleting saves: {e}")
                    elif event.key in [pygame.K_n, pygame.K_ESCAPE]:
                        return

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
            elif self.power_ups.current_power_up == 'TripleShot':
                color = self.GREEN
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
            pygame.time.set_timer(pygame.USEREVENT + 1, 2000)  
        
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

        if self.is_raspberry_pi:
            if color == self.GREEN:
                GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
                GPIO.output(RED_LED_PIN, GPIO.LOW)
            else:
                GPIO.output(RED_LED_PIN, GPIO.HIGH)
                GPIO.output(GREEN_LED_PIN, GPIO.LOW)

        pygame.time.wait(2000)

        if self.is_raspberry_pi:
            GPIO.output(GREEN_LED_PIN, GPIO.LOW)
            GPIO.output(RED_LED_PIN, GPIO.LOW)

    def boss_fight_splash_screen(self):
        self.change_music(self.boss_music)  # Start boss music
        # Clear player bullets and deactivate power-ups
        self.clear_bullets()
        self.power_ups.reset_power_up()
        self.boss.health = self.boss.max_health
        
        self.screen.fill(self.BLACK)
        boss_fight_text = self.bold_font.render("Boss Fight!", True, self.RED)
        self.screen.blit(boss_fight_text, (self.screen_width // 2 - boss_fight_text.get_width() // 2, self.screen_height // 2 - 100))
        continue_text = self.big_font.render("Press any key to continue", True, self.WHITE)
        self.screen.blit(continue_text, (self.screen_width // 2 - continue_text.get_width() // 2, self.screen_height // 2 + 50))
        pygame.display.flip()
        self.wait_for_keypress()

    def game_over_screen(self):
        self.change_music(self.game_over_music)  # Play Game Over music
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

    def wait_for_keypress(self, cooldown=1000):
        start_time = pygame.time.get_ticks()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    # Only accept the key if the cooldown period has passed.
                    if pygame.time.get_ticks() - start_time >= cooldown:
                        return
            pygame.time.wait(10)  # Prevent a busy loop

    def show_menu(self):
        menu_options = ["New Game", "Load Game", "Leaderboard", "Instructions", "Exit"]
        selected_option = 0
        self.loaded_from_menu = False   

        self.change_music(self.menu_music)  # Play menu music

        while True:
            current_time = time.time()
        
            #Animate the background every 0.2 seconds**
            if current_time - self.last_bg_update >= self.bg_animation_interval:
                self.menu_background_index = (self.menu_background_index + 1) % len(self.menu_backgrounds)
                self.last_bg_update = current_time
        
            #Draw the animated background
            self.screen.blit(self.menu_backgrounds[self.menu_background_index], (0, 0))

            # Title text
            self.screen.blit(self.title_image, (self.screen_width // 2 - self.title_image.get_width() // 2, 50))


            # Draw menu items
            for i, option in enumerate(menu_options):
                y = 200 + i * 80
                color = self.GREEN if i == selected_option else self.WHITE
                option_text = self.big_font.render(option, True, color)
                self.screen.blit(option_text, (self.screen_width//2 - option_text.get_width()//2, y))

            pygame.display.flip()

            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                    elif event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if menu_options[selected_option] == "Load Game":
                            self.show_load_menu()
                        elif menu_options[selected_option] == "New Game":
                            self.reset_game()
                            return
                        elif menu_options[selected_option] == "Leaderboard":
                            self.show_leaderboard()
                        elif menu_options[selected_option] == "Instructions":
                            self.show_instructions()
                        elif menu_options[selected_option] == "Exit":
                            pygame.quit()
                            quit()
                            
    def show_load_menu(self):
        selected_slot = 0
        while True:
            self.screen.fill(self.BLACK)
            title = self.big_font.render("Load Game", True, self.YELLOW)
            self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 50))
        
            # Draw slots with proper empty slot handling
            slot_height = 100
            start_y = 150
            for i in range(3):
                # Create slot_rect FIRST
                slot_rect = pygame.Rect(
                    200,  # x
                    start_y + i*(slot_height + 20),  # y
                    800,  # width
                    slot_height  # height
                )
                color = self.GREEN if i == selected_slot else self.WHITE
            
                # Always draw the slot background
                pygame.draw.rect(self.screen, color, slot_rect, 2)
            
                if self.save_slots[i]:
                    # Draw save info for occupied slot
                    save = self.save_slots[i]
                    text_lines = [
                        f"{save['name']}",
                        f"Level: {save['level']} | Lives: {save['player']['lives']}",
                        f"Score: {save['score']} | Saved: {save['timestamp']}"
                    ]
                    for j, line in enumerate(text_lines):
                        text_surf = self.font.render(line, True, color)
                        self.screen.blit(text_surf, (slot_rect.x + 20, slot_rect.y + 10 + j*30))
                else:
                    # Draw empty slot text
                    empty_text = self.font.render("Empty Slot!", True, color)
                    self.screen.blit(empty_text, (slot_rect.x + 20, slot_rect.y + 40))
        
            # Add return instruction
            return_text = self.font.render("Press ESC to return to menu | DEL to delete save", True, self.GREEN)
            self.screen.blit(return_text, (self.screen_width//2 - return_text.get_width()//2, 550))
        
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_slot = (selected_slot + 1) % 3
                    elif event.key == pygame.K_UP:
                        selected_slot = (selected_slot - 1) % 3
                    elif event.key == pygame.K_RETURN:
                        if self.save_slots[selected_slot]:
                            self.load_game(selected_slot)
                            return
                    elif event.key == pygame.K_ESCAPE:
                        return
                    elif event.key == pygame.K_DELETE:
                        if self.save_slots[selected_slot]:
                            if self.confirm_delete_save():
                                self.save_slots[selected_slot] = None
                                try:
                                    with open('saves.json', 'w') as f:
                                        json.dump(self.save_slots, f)
                                    self.display_feedback("Save deleted!", self.RED)
                                except Exception as e:
                                    print(f"Error deleting save: {e}")
        
            pygame.display.flip()
            
    def confirm_delete_save(self):
        # Display a confirmation screen
        self.screen.fill(self.BLACK)
        confirm_text = self.big_font.render("Confirm delete save? (Y/N)", True, self.WHITE)
        self.screen.blit(confirm_text, (self.screen_width//2 - confirm_text.get_width()//2,
                                        self.screen_height//2 - confirm_text.get_height()//2))
        pygame.display.flip()
    
        # Wait for user input
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        return True
                    elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        return False
                            
    def save_game(self, slot, name):
        """Save all essential game states and force an update to the saves.json file."""
        # Reload current saves from file to ensure we have the latest data
        current_saves = []
        if os.path.exists('saves.json'):
            try:
                with open('saves.json', 'r') as f:
                    current_saves = json.load(f)
                # Ensure we have exactly 3 slots, fill with None if necessary
                current_saves = (current_saves + [None] * 3)[:3]
            except (json.JSONDecodeError, FileNotFoundError):
                current_saves = [None, None, None]
        else:
            current_saves = [None, None, None]

        # Create the new game state
        game_state = {
            'name': name,
            'level': "BOSS" if self.boss_fight else self.level,
            'boss_fight': self.boss_fight,
            'score': self.score,
            'questions_asked': self.questions_asked,
            'asked_questions': self.asked_questions,
            'player': {
                'lives': self.player.lives,
                'x': self.player.x,
                'y': self.player.y,
                'invulnerable': self.player.invulnerable,
                'invulnerable_time': time.time() - self.player.invulnerable_timer,
            },
            'enemies': self.enemy_manager.enemies,
            'enemy_direction': self.enemy_manager.direction,
            'boss_health': self.boss.health if self.boss_fight else None,
            'player_bullets': [(b[0], b[1], b[2], b[3]) for b in self.bullet_manager.player_bullets],
            'enemy_bullets': [(b[0], b[1]) for b in self.bullet_manager.enemy_bullets],
            'boss_bullets': [(b[0], b[1], b[2], b[3]) for b in self.bullet_manager.boss_bullets],
            'power_ups': {
                'active': self.power_ups.power_up_active,
                'type': self.power_ups.current_power_up,
                'positions': self.power_ups.power_ups.copy(),  # Save all power-up positions
                'timer': self.power_ups.power_up_timer - time.time() if self.power_ups.power_up_active else 0,
                'spawn_time': self.power_ups.spawn_time
            },
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        # Update the specific slot
        current_saves[slot] = game_state

        # Write back all slots to the file
        try:
            with open('saves.json', 'w') as f:
                json.dump(current_saves, f)
            # Update in-memory save slots to reflect the latest changes
            self.save_slots = current_saves
            self.display_feedback("Game Saved!", self.GREEN)
        except IOError as e:
            print(f"Error saving game: {e}")
            self.display_feedback("Error saving game!", self.RED)

    def get_save_name(self, slot):
        name = ""
        while True:
            # Draw themed background
            self.screen.fill(self.BLACK)
        
            # Draw decorative border
            pygame.draw.rect(self.screen, self.GREEN, (150, 150, 900, 300), 3)

            # Title text
            prompt = self.big_font.render("NAME YOUR SAVE FILE", True, self.YELLOW)
            self.screen.blit(prompt, (self.screen_width//2 - prompt.get_width()//2, 180))

            # Input box with blinking cursor
            input_rect = pygame.Rect(self.screen_width//2 - 200, 280, 400, 40)
            pygame.draw.rect(self.screen, self.WHITE, input_rect, 2)
            name_text = self.font.render(name, True, self.GREEN)
            self.screen.blit(name_text, (input_rect.x + 10, input_rect.y + 5))
        
            # Blinking cursor
            if int(time.time() * 2) % 2 == 0:
                cursor_x = input_rect.x + 10 + name_text.get_width() + 2
                pygame.draw.line(self.screen, self.GREEN, (cursor_x, input_rect.y+5), 
                               (cursor_x, input_rect.y+35), 3)

            # Instructions
            instr_text = self.font.render("Press ESC to cancel | ENTER to save", True, self.WHITE)
            self.screen.blit(instr_text, (self.screen_width//2 - instr_text.get_width()//2, 350))

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return  # Return to save slot menu
                    elif event.key == pygame.K_RETURN:
                        if name.strip():
                            self.save_game(slot, name.strip())
                            return
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        if len(name) < 20 and event.unicode.isprintable():
                            name += event.unicode

            pygame.display.flip()

    def load_game(self, slot):
        """Forces the game to reload exactly what is in saves.json to ensure consistency."""
        if os.path.exists('saves.json'):
            try:
                with open('saves.json', 'r') as f:
                    self.save_slots = json.load(f)  # Reload the entire save structure
            except (json.JSONDecodeError, FileNotFoundError) as e:
                self.display_feedback(f"Error reading save file: {e}", self.RED)
                return False
        else:
            self.display_feedback("No save file found!", self.RED)
            return False

        # **Ensure selected save slot exists and is not empty**
        if not self.save_slots or not self.save_slots[slot]:
            self.display_feedback("Empty Slot!", self.RED)
            return False

        save_data = self.save_slots[slot]  # Load fresh data from file

        # **CLEAR EVERYTHING BEFORE LOADING TO AVOID CROSSOVER ISSUES**
        self.reset_game_state()

        # Restore core state
        self.level = save_data['level']
        self.boss_fight = save_data['boss_fight']
        self.score = save_data['score']
        self.questions_asked = save_data['questions_asked']
        self.asked_questions = save_data['asked_questions']

        # Restore player
        self.player.lives = save_data['player']['lives']
        self.player.x = save_data['player']['x']
        self.player.y = save_data['player']['y']
        self.player.invulnerable = save_data['player']['invulnerable']
        self.player.invulnerable_timer = time.time() - save_data['player']['invulnerable_time']

        # Restore enemies exactly as saved
        self.enemy_manager.enemies = save_data['enemies'] if save_data['enemies'] else []
        self.enemy_manager.direction = save_data['enemy_direction']
        if not self.enemy_manager.enemies:
            self.enemy_manager.create_enemies()  # **Only recreate enemies if missing from save**

        # Restore boss
        if self.boss_fight:
            self.boss.health = save_data['boss_health']
            self.enemy_manager.enemies.clear() # Fixed issue when loading from save where eneimies would spawn
            

        # Restore bullets
        self.bullet_manager.player_bullets = [[b[0], b[1], b[2], b[3]] for b in save_data['player_bullets']]
        self.bullet_manager.enemy_bullets = [[b[0], b[1]] for b in save_data['enemy_bullets']]
        self.bullet_manager.boss_bullets = [
            [b[0], b[1], b[2], b[3]] 
            for b in save_data['boss_bullets']
            if len(b) == 4 and all(isinstance(v, (int, float)) for v in b)
        ]

        # Restore power-ups
        power_up_data = save_data['power_ups']
        self.power_ups.power_up_active = power_up_data['active']
        self.power_ups.current_power_up = power_up_data['type']
        self.power_ups.power_ups = power_up_data['positions']
        self.power_ups.spawn_time = power_up_data['spawn_time']
        if power_up_data['active']:
            # Calculate remaining time when paused
            self.power_ups.power_up_timer = time.time() + power_up_data['timer']

        self.display_feedback("Game Loaded!", self.GREEN)
        self.paused = False
        self.main_game_loop()
        
    def check_server_availability(self):
        try:
            # Adding Basic Authentication with the username and password
            response = requests.get("https://5269989.pythonanywhere.com/leaderboard", 
                                    timeout=5, 
                                    auth=HTTPBasicAuth('5269989', 'SAM'))
            return response.status_code == 200
        except requests.RequestException:
            return False
        
    def load_saves_from_file(self):
        """Loads saved game data from saves.json at startup."""
        if os.path.exists('saves.json'):
            try:
                with open('saves.json', 'r') as f:
                    loaded_saves = json.load(f)
                    # Ensure exactly 3 slots, filling with None if necessary
                    self.save_slots = (loaded_saves + [None] * 3)[:3]
            except (json.JSONDecodeError, FileNotFoundError):
                self.save_slots = [None, None, None]
        else:
            self.save_slots = [None, None, None]
            
    def create_loading_screen(self):
        self.screen.fill(self.BLACK)
        loading_text = self.big_font.render("Loading...", True, self.GREEN)
        self.screen.blit(loading_text, (self.screen_width // 2 - loading_text.get_width() // 2, self.screen_height // 2 - loading_text.get_height() // 2))
        pygame.display.flip()   
        
    def show_leaderboard(self):
        self.create_loading_screen()  # Show loading screen
        try:
            # Adding Basic Authentication with the username and password
            response = requests.get("https://5269989.pythonanywhere.com/leaderboard", 
                                    timeout=5, 
                                    auth=HTTPBasicAuth('5269989', 'SAM'))
            if response.status_code == 200:
                leaderboard_data = response.json()
                self.screen.fill(self.BLACK)
                leaderboard_title = self.big_font.render("Leaderboard", True, self.YELLOW)
                self.screen.blit(leaderboard_title, (self.screen_width // 2 - leaderboard_title.get_width() // 2, 30))
    
                smaller_font = pygame.font.SysFont("Arial", 22)
                y_position = 100
    
                for i, entry in enumerate(leaderboard_data):
                    player_text = smaller_font.render(f"{i+1}. {entry['player']} - {entry['score']} points", True, self.WHITE)
                    self.screen.blit(player_text, (self.screen_width // 2 - player_text.get_width() // 2, y_position))
                    y_position += 40
            else:
                raise Exception("Failed to retrieve leaderboard")
        except Exception as e:
            self.screen.fill(self.BLACK)
            error_text = self.big_font.render(f"Error: Failed to connect to leaderboard server", True, self.RED)
            self.screen.blit(error_text, (self.screen_width // 2 - error_text.get_width() // 2, self.screen_height // 2 - error_text.get_height() // 2))

        tip = "Press any key to go back!"
        tip_text = self.font.render(tip, True, self.GREEN)
        self.screen.blit(tip_text, (self.screen_width // 2 - tip_text.get_width() // 2, self.screen_height - 50))

        pygame.display.flip()

        # Wait for a key press before returning to the menu
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    waiting = False
        self.show_menu()
                 
    def clear_level(self):
        
        # Clear player bullets and deactivate power-ups
        self.clear_bullets()
        self.power_ups.reset_power_up()  # Reset power-ups
        self.power_ups.spawn_time = time.time()  # Reset spawn timer
        self.power_ups.spawn_power_up()  

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
        back_text = self.font.render("Press any key to go back", True, self.GREEN)
        back_x = self.screen_width // 2 - back_text.get_width() // 2
        self.screen.blit(back_text, (back_x, self.screen_height - 40))

        pygame.display.flip()
        self.wait_for_keypress()

    def reset_game(self):
        """Fully resets the game to avoid cross-over issues and ensure proper startup."""
        self.player.lives = 3
        self.player.x = (self.screen_width - self.player.width) // 2
        self.player.y = self.screen_height - self.player.height - 10
        self.player.invulnerable = False
        self.player.invulnerable_timer = 0
        self.level = 1
        self.boss_fight = False
        self.score = 5000
        self.questions_asked = 0
        self.asked_questions = []
        self.enemy_manager.create_enemies()
        self.boss.health = self.boss.max_health
        # **Reset Bullets**
        self.bullet_manager.player_bullets = []
        self.bullet_manager.enemy_bullets = []
        self.bullet_manager.boss_bullets = []
        # **Reset Power-ups**
        self.power_ups.power_up_active = False
        self.power_ups.current_power_up = None
        self.power_ups.power_ups = []
        self.power_ups.spawn_time = time.time()
        # **Ensure game does NOT start paused**
        self.paused = False
        self.main_game_loop()
               
    def reset_game_state(self):
        """Fully resets the game state to avoid cross-over issues when loading a save."""
        # **Clear Bullets**
        self.bullet_manager.player_bullets.clear()
        self.bullet_manager.enemy_bullets.clear()
        self.bullet_manager.boss_bullets.clear()
        # **Clear Enemies**
        self.enemy_manager.enemies.clear()
        # **Clear Power-Ups**
        self.power_ups.reset_power_up()
        self.power_ups.is_first_level = True
        # Reset Boss
        self.boss.reset_boss()
        self.boss_fight = False
        # **Reset Score & Level**
        self.level = 1
        self.questions_asked = 0
        self.asked_questions.clear()
        self.score = 5000
        # **Reset Player**
        self.player.lives = 3
        self.player.invulnerable = False
        self.player.invulnerable_timer = 0
        # **Ensure UI and timers are reset**
        pygame.time.set_timer(pygame.USEREVENT + 1, 0)
        if hasattr(self, 'score_adjustment'):
            del self.score_adjustment

    def end_game_screen(self):
        self.screen.fill(self.BLACK)
    
        # Game Over Text
        end_text = self.bold_font.render(f"YOU WIN! Your Score is: {self.score}", True, self.GREEN)
        self.screen.blit(end_text, (self.screen_width // 2 - end_text.get_width() // 2, self.screen_height // 3 - end_text.get_height() // 2))
    
        # Name Prompt
        name_prompt = self.big_font.render("Enter your name (3 letters):", True, self.WHITE)
        self.screen.blit(name_prompt, (self.screen_width // 2 - name_prompt.get_width() // 2, self.screen_height // 2 - 30))

        # Input Box
        input_box = pygame.Rect(self.screen_width // 2 + 0, self.screen_height // 2 + 30, 50, 32)
        color_inactive = self.LIGHTBLUE
        color_active = self.GREEN
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
        self.create_loading_screen()  # Show loading screen
        try:
            payload = {'player_name': name, 'score': score}
            # Adding Basic Authentication with the username and password
            response = requests.post("https://5269989.pythonanywhere.com/submit_score", 
                                     json=payload, 
                                     timeout=5, 
                                     auth=HTTPBasicAuth('5269989', 'SAM'))
            if response.status_code != 200:
                raise Exception(f"Failed to submit score. Status code: {response.status_code}")
            else:
                self.display_feedback("Score submitted successfully", self.GREEN)
        except requests.RequestException as e:
            self.display_feedback(f"Network Error: {str(e)}", self.RED)
        except Exception as e:
            self.display_feedback(f"Error: {str(e)}", self.RED)
    
        self.show_menu()
