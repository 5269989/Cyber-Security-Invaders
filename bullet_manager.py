import pygame
import math
import time

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

    def add_boss_bullet(self, x, y, dx=0, dy=3):
        # Ensure all parameters are valid numbers
        if all(isinstance(v, (int, float)) for v in [x, y, dx, dy]):
            self.boss_bullets.append([x, y, dx, dy])
        else:
            print(f"Invalid boss bullet parameters: {[x, y, dx, dy]}")

    def update_player_bullets(self, draw_only=False):
        bullets_to_remove = []
        for bullet in self.player_bullets[:]:
            x, y, height, angle = bullet
            # Move bullet based on its angle
            if not draw_only and angle == 0:  # Straight up
                bullet[1] -= self.player_bullet_speed
            elif not draw_only:
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
            
            # Check for conditions to remove bullet
            if not draw_only and (bullet[1] < 0 or bullet[0] < 0 or bullet[0] > self.game.screen_width):
                bullets_to_remove.append(bullet)
            # Check for enemy collision
            for enemy in self.game.enemy_manager.enemies[:]:
                if (enemy[0] < x < enemy[0] + 40 and enemy[1] < y < enemy[1] + 40) or \
                   (enemy[0] < x + height * math.sin(angle) < enemy[0] + 40 and enemy[1] < y - height * math.cos(angle) < enemy[1] + 40):
                    bullets_to_remove.append(bullet)
                    self.game.enemy_manager.enemies.remove(enemy)
                    break
            # Remove all bullets marked for deletion
            for bullet in bullets_to_remove:
                if bullet in self.player_bullets:  # Double check if the bullet is still in the list
                    self.player_bullets.remove(bullet)

    def update_enemy_bullets(self, draw_only=False):
        # Changed from boss_bullets to enemy_bullets
        for bullet in self.enemy_bullets[:]:  # THIS LINE WAS FIXED
            if not draw_only:
                # Move bullet downward
                bullet[1] += self.enemy_bullet_speed
        
            # Draw enemy bullet
            pygame.draw.rect(self.game.screen, self.game.RED, 
                            (bullet[0], bullet[1], self.bullet_width, self.enemy_bullet_height))
        
            # Remove bullets that go off screen
            if not draw_only and bullet[1] > self.game.screen_height:
                self.enemy_bullets.remove(bullet)
                
    def update_boss_bullets(self, draw_only=False):
        """Updates or draws boss bullets, depending on the draw_only flag."""
        for bullet in self.boss_bullets[:]:
            if isinstance(bullet, dict) and bullet.get("type") == "virus":
                if not draw_only:
                    # Update virus bullet position
                    bullet["x"] += bullet["dx"]
                    bullet["y"] += bullet["dy"]

                    # Check if virus bullet should explode
                    explosion_threshold = self.game.screen_height / 2
                    if bullet["y"] >= explosion_threshold:
                        self.game.boss.explode_virus(bullet)
                        self.boss_bullets.remove(bullet)
                        continue  # Skip drawing if removed

                # Draw virus bullet
                self.game.screen.blit(bullet["image"], (bullet["x"], bullet["y"]))

            elif isinstance(bullet, list) and len(bullet) == 4:
                if not draw_only:
                    # Update normal boss bullet (stored as a list)
                    bullet[0] += bullet[2]  # x += dx
                    bullet[1] += bullet[3]  # y += dy

                # Draw normal boss bullet (yellow, same shape as player bullets)
                pygame.draw.rect(self.game.screen, self.game.YELLOW, 
                                 (bullet[0], bullet[1], self.bullet_width, self.enemy_bullet_height))

            else:
                print("WARNING: Skipping invalid bullet:", bullet)
                self.boss_bullets.remove(bullet)

    def check_player_hit(self):
        for bullet in self.enemy_bullets[:]:
            if (self.game.player.x < bullet[0] < self.game.player.x + self.game.player.width and 
                self.game.player.y < bullet[1] < self.game.player.y + self.game.player.height):
                if not self.game.player.invulnerable:
                    self.enemy_bullets.remove(bullet)
                    self.game.last_hit_time = time.time()
                    return True
                self.enemy_bullets.remove(bullet)
        return False

    def reset_triple_shot(self):
        self.triple_shot = False

    def check_player_hit_by_boss_bullet(self):
        for bullet in self.boss_bullets[:]:
            if not isinstance(bullet, list) or len(bullet) < 4:
                print("WARNING: Skipping invalid bullet:", bullet)
                continue  # Skip malformed bullets
        
            # Access bullet as a list
            if (self.game.player.x < bullet[0] < self.game.player.x + self.game.player.width and
                self.game.player.y < bullet[1] < self.game.player.y + self.game.player.height):
                if not self.game.player.invulnerable:
                    self.boss_bullets.remove(bullet)
                    return True
        return False