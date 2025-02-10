import pygame
import math
import random
import time
import os
from scripts.game_logic.minigame import HackingMiniGame

class Boss:
    def __init__(self, game):
        self.game = game

        # Load assets
        self.base_image = self.load_and_scale_image("boss.png", (150, 150))
        self.rage_image = self.load_and_scale_image("boss_rage.png", (150, 150))
        # Load the virus bullet asset
        self.virus_bullet_image = self.load_and_scale_image("virus.png", (20, 20))

        self.current_image = self.base_image
        self.width, self.height = self.base_image.get_size()
        self.x = (game.screen_width - self.width) // 2
        self.y = 100
        self.speed = 3  
        self.health = 100
        self.max_health = 100
        self.last_shot_time = 0
        self.animation_interval = 0.5
        self.last_animation_time = 0
        self.animation_toggle = False
        
        # Save initial positions/stats so it can be reset if needed
        self.initial_x = self.x
        self.initial_y = self.y
        self.initial_speed = self.speed
        self.initial_shoot_interval = 0.1
        self.initial_animation_interval = self.animation_interval

        self.rage_mode = False
        self.name = "VIRUS"
        self.minigame_triggered = False

        self.dx = self.speed

        self.target_pos = (self.x, self.y)
        self.last_target_update = pygame.time.get_ticks()

        # New attributes for new AI:
        self.phase = 1  
        self.phase1_shoot_interval = 0.15 
        self.phase2_shoot_interval = 0.1  
        self.phase3_shoot_interval = 0.5  
        self.phase4_shoot_interval = 0.07  
        self.phase5_shoot_interval = 0.5  

    def load_and_scale_image(self, filename, size):
        try:
            return pygame.transform.scale(
                pygame.image.load(os.path.join("assets", "sprites", filename)).convert_alpha(), size
            )
        except pygame.error as e:
            print(f"Error loading or scaling image '{filename}': {e}")
            pygame.quit()
            quit()

    def update(self):
        self.update_phase()
        self.perform_movement()
        self.update_virus_bullets()
        self.check_hit_by_player()
        self.draw()

    def update_phase(self):
        # Determine the current phase based on the percentage of remaining health
        health_percent = (self.health / self.max_health) * 100
        if health_percent > 80:
            self.phase = 1
        elif health_percent > 60:
            self.phase = 2
        elif health_percent > 40:
            self.phase = 3
        elif health_percent > 20:
            self.phase = 4
        else:
            self.phase = 5

    # ─── MOVEMENT PATTERNS ─────────────────────────────────────────────
    def perform_movement(self):
        # Call the movement routine for the current phase
        if self.phase == 1:
            self.movement_phase1()
        elif self.phase == 2:
            self.movement_phase2()
        elif self.phase == 3:
            self.movement_phase3()
        elif self.phase == 4:
            self.movement_phase4()
        elif self.phase == 5:
            self.movement_phase5()

    def movement_phase1(self):
        x_min = 50
        x_max = self.game.screen_width - self.width - 50
        self.x += self.dx
        if self.x < x_min or self.x > x_max:
            self.dx = -self.dx
            self.x += self.dx

    def movement_phase2(self):
        x_min = 50
        x_max = self.game.screen_width - self.width - 50
        self.x += self.dx
        if self.x < x_min or self.x > x_max:
            self.dx = -self.dx
            self.x += self.dx
        base_y = 100
        amplitude = 20
        self.y = base_y + amplitude * math.sin(pygame.time.get_ticks() / 1000.0)

    def movement_phase3(self):
        # Boss aims at the player but with smoothing.
        target_x = self.game.player.x + self.game.player.width/2 - self.width/2
        dx = (target_x - self.x) * 0.05
        if dx > self.speed:
            dx = self.speed
        elif dx < -self.speed:
            dx = -self.speed
        self.x += dx
        base_y = 100
        amplitude = 20
        self.y = base_y + amplitude * math.sin(pygame.time.get_ticks() / 1000.0)

    def movement_phase4(self):
        period = 3000  
        t = pygame.time.get_ticks() % period
        x_min = 50
        x_max = self.game.screen_width - self.width - 50
        sine_val = math.sin(2 * math.pi * t / period)
        self.x = x_min + (x_max - x_min) * (sine_val + 1) / 2
        self.y = 50 + (150 - 50) * ((math.sin(2 * math.pi * t / period + math.pi/4) + 1) / 2)

    def movement_phase5(self):
        # Erratic movement: update a target position then move toward it.
        current_time = pygame.time.get_ticks()
        if current_time - self.last_target_update > 2000:
            x_min = 50
            x_max = self.game.screen_width - self.width - 50
            y_min = 50
            y_max = self.game.screen_height // 3
            self.target_pos = (random.randint(x_min, x_max), random.randint(y_min, y_max))
            self.last_target_update = current_time
        target_x, target_y = self.target_pos
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)
        if distance != 0:
            dx = (dx / distance) * self.speed
            dy = (dy / distance) * self.speed
        self.x += dx
        self.y += dy

    # ─── ATTACK PATTERNS ─────────────────────────────────────────────
    def attack_pattern(self):
        # Select and execute an attack based on the current phase
        if self.phase == 1:
            self.phase1_attack()
        elif self.phase == 2:
            self.phase2_attack()
        elif self.phase == 3:
            self.phase3_attack()
        elif self.phase == 4:
            self.phase4_attack()
        elif self.phase == 5:
            self.phase5_attack()

    def phase1_attack(self):
        # Phase 1: Fire a bullet straight down
        current_time = time.time()
        if current_time - self.last_shot_time < self.phase1_shoot_interval:
            return
        self.last_shot_time = current_time
        self.game.bullet_manager.add_boss_bullet(
            self.x + self.width // 2, self.y + self.height, dx=0, dy=3
        )

    def phase2_attack(self):
        # Phase 2: Spread attack – continuously fire a single bullet with a random angle in a 45° cone (relative to straight down)
        current_time = time.time()
        if current_time - self.last_shot_time < self.phase2_shoot_interval:
            return
        self.last_shot_time = current_time

        boss_center_x = self.x + self.width / 2
        boss_bottom_y = self.y + self.height

        # choose a random angle to fire at
        angle = random.uniform(-90, 90)
        rad = math.radians(angle)
    
        dx = math.sin(rad) * 3 
        dy = math.cos(rad) * 3  

        self.game.bullet_manager.add_boss_bullet(boss_center_x, boss_bottom_y, dx, dy)

    def phase3_attack(self):
        # Phase 3: Aim at the player with a little inaccuracy
        current_time = time.time()
        if current_time - self.last_shot_time < self.phase3_shoot_interval:
            return
        self.last_shot_time = current_time
        player_center_x = self.game.player.x + self.game.player.width / 2
        player_center_y = self.game.player.y + self.game.player.height / 2
        boss_center_x = self.x + self.width / 2
        boss_center_y = self.y + self.height / 2
        dx = (player_center_x - boss_center_x) / 50.0
        dy = (player_center_y - boss_center_y) / 50.0
        # Add slight inaccuracy
        dx += dx * random.uniform(-0.05, 0.05)
        dy += dy * random.uniform(-0.05, 0.05)
        self.game.bullet_manager.add_boss_bullet(
            self.x + self.width // 2, self.y + self.height, dx, dy
        )

    def phase4_attack(self):
        # Phase 4: Circle attack firing a bullet in a random direction
        current_time = time.time()
        if current_time - self.last_shot_time < self.phase4_shoot_interval:
            return
        self.last_shot_time = current_time
        angle = random.randint(0, 360)
        rad = math.radians(angle)
        dx = math.cos(rad) * 3
        dy = math.sin(rad) * 3
        self.game.bullet_manager.add_boss_bullet(
            self.x + self.width // 2, self.y + self.height, dx, dy
        )

    def phase5_attack(self):
        # Phase 5: Virus explosion attack – fires a virus bullet that explodes halfway to the player
        current_time = time.time()
        if current_time - self.last_shot_time < self.phase5_shoot_interval:
            return
        self.last_shot_time = current_time

        virus_bullet = {
            "x": self.x + self.width // 2,
            "y": self.y + self.height,
            "dx": 0,
            "dy": 3,
            "type": "virus",
            "image": self.virus_bullet_image
        }
        self.game.bullet_manager.boss_bullets.append(virus_bullet)

    def update_virus_bullets(self):
        # Update virus bullets and trigger their explosion when they reach the threshold

        explosion_threshold = (5000)

        for bullet in self.game.bullet_manager.boss_bullets[:]:
            if isinstance(bullet, dict) and bullet.get("type") == "virus":
                bullet["y"] += bullet["dy"]

                if bullet["y"] >= (500):
                    self.explode_virus(bullet)
                    self.game.bullet_manager.boss_bullets.remove(bullet)

    def explode_virus(self, bullet):
        #Explode the virus bullet into several bullets in a circular pattern
        x, y = bullet["x"], bullet["y"]
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            dx = math.cos(rad) * 4
            dy = math.sin(rad) * 4
            self.game.bullet_manager.add_boss_bullet(x, y, dx, dy)

    # ─── RAGE MODE ─────────────────────────────────────────────
    def enable_rage_mode(self):
        # When called (for example, if the player loses the minigame), the boss goes into rage mode:
        # Movement speed increases by 15%
        # Shooting intervals decrease by 15% (i.e. shooting faster)
        if not self.rage_mode:
            self.rage_mode = True
            self.speed *= 1.5  
            self.phase1_shoot_interval *= 0.5
            self.phase2_shoot_interval *= 0.5
            self.phase3_shoot_interval *= 0.5
            self.phase4_shoot_interval *= 0.5
            self.phase5_shoot_interval *= 0.5

    # ─── DRAWING METHODS ─────────────────────────────────────────────
    def draw(self):
        current_time = time.time()
        if current_time - self.last_animation_time >= self.animation_interval:
            self.animation_toggle = not self.animation_toggle
            base = self.rage_image if self.rage_mode else self.base_image
            self.current_image = (pygame.transform.flip(base, True, False)
                                  if self.animation_toggle else base)
            self.last_animation_time = current_time

        self.game.screen.blit(self.current_image, (self.x, self.y))
        self.draw_health_bar()

    def draw_health_bar(self):
        bar_width = 200
        health_width = int(bar_width * (self.health / self.max_health))
        bar_x = self.game.screen_width // 2 - bar_width // 2
        pygame.draw.rect(self.game.screen, self.game.RED, (bar_x, 40, bar_width, 20))
        pygame.draw.rect(self.game.screen, self.game.GREEN, (bar_x, 40, health_width, 20))
        name_text = self.game.font.render(self.name, True, self.game.YELLOW)
        name_x = self.game.screen_width // 2 - name_text.get_width() // 2
        self.game.screen.blit(name_text, (name_x, 10))
        if self.rage_mode:
            rage_text = self.game.font.render("(Rage Mode)", True, self.game.RED)
            self.game.screen.blit(rage_text, (name_x + name_text.get_width() + 10, 10))

    def check_hit_by_player(self):
        # Check for collision with player bullets and update health
        for bullet in self.game.bullet_manager.player_bullets[:]:
            if (self.x < bullet[0] < self.x + self.width and 
                self.y < bullet[1] < self.y + self.height):
                self.game.bullet_manager.player_bullets.remove(bullet)
                self.health -= 1
                if self.health <= 0:
                    self.game.change_music(self.game.boss_defeated_music)
                    self.game.display_feedback("Boss Defeated!", self.game.GREEN)
                    self.game.end_game_screen()
                elif self.health <= 50 and not self.rage_mode and not self.minigame_triggered:
                    success = HackingMiniGame(self.game).run()
                    if not success:
                        self.enable_rage_mode()
                    self.minigame_triggered = True
                    
    def trigger_minigame(self):
        success = HackingMiniGame(self.game).run()
        if not success:
            self.shoot_interval *= 0.8
            self.rage_mode = True
        self.minigame_triggered = True
        
    def reset_boss(self):
        # Reset the boss to its initial state
        self.x = self.initial_x
        self.y = self.initial_y
        self.health = 100
        self.max_health = 100
        self.speed = self.initial_speed
        self.shoot_interval = self.initial_shoot_interval
        self.animation_interval = self.initial_animation_interval
        self.last_shot_time = 0
        self.last_animation_time = 0
        self.current_image = self.base_image
        self.direction = 1
        self.rage_mode = False
        self.minigame_triggered = False
