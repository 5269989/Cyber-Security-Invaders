import pygame
import math
import time

class BulletManager:
    def __init__(self, game):
        self.player_bullets = []
        self.enemy_bullets = []
        self.boss_bullets = []
        self.bullet_width = 5
        self.player_bullet_height = 10  
        self.enemy_bullet_height = 10   
        self.player_bullet_speed = 7
        self.enemy_bullet_speed = 5
        self.player_shoot_interval = 0.2  
        self.last_shot_time = 0
        self.game = game
        self.angle = math.radians(20)
        self.triple_shot = False

    def add_player_bullet(self, x, y):
        if self.triple_shot:
            # Middle bullet (straight ahead)
            self.player_bullets.append([x, y, self.player_bullet_height, 0]) 
            # Left bullet (20 degrees to the left)
            self.player_bullets.append([x - 10, y, self.player_bullet_height, -self.angle])  
            # Right bullet (20 degrees to the right)
            self.player_bullets.append([x + 10, y, self.player_bullet_height, self.angle])
        else:
            self.player_bullets.append([x, y, self.player_bullet_height, 0])  

    def add_enemy_bullet(self, x, y):
        self.enemy_bullets.append([x, y])

    def add_boss_bullet(self, x, y, dx=0, dy=3):
        if all(isinstance(v, (int, float)) for v in [x, y, dx, dy]):
            self.boss_bullets.append([x, y, dx, dy])
        else:
            print(f"Invalid boss bullet parameters: {[x, y, dx, dy]}")

    def update_player_bullets(self, draw_only=False):
        bullets_to_remove = []
        for bullet in self.player_bullets[:]:
            x, y, height, angle = bullet
            if not draw_only and angle == 0:  
                bullet[1] -= self.player_bullet_speed
            elif not draw_only:
                bullet[0] += self.player_bullet_speed * math.sin(angle)  
                bullet[1] -= self.player_bullet_speed * math.cos(angle) 
            
            rect_points = [
                (x, y),
                (x + height * math.sin(angle), y - height * math.cos(angle)),
                (x + self.bullet_width * math.cos(angle) + height * math.sin(angle), y + self.bullet_width * math.sin(angle) - height * math.cos(angle)),
                (x + self.bullet_width * math.cos(angle), y + self.bullet_width * math.sin(angle))
            ]
            pygame.draw.polygon(self.game.screen, self.game.GREEN, rect_points)
            
            # Check for conditions to remove bullet
            if not draw_only and (bullet[1] < 0 or bullet[0] < 0 or bullet[0] > self.game.screen_width):
                bullets_to_remove.append(bullet)
            for enemy in self.game.enemy_manager.enemies[:]:
                if (enemy[0] < x < enemy[0] + 40 and enemy[1] < y < enemy[1] + 40) or \
                   (enemy[0] < x + height * math.sin(angle) < enemy[0] + 40 and enemy[1] < y - height * math.cos(angle) < enemy[1] + 40):
                    bullets_to_remove.append(bullet)
                    self.game.enemy_manager.enemies.remove(enemy)
                    break
            for bullet in bullets_to_remove:
                if bullet in self.player_bullets:  # Double check if the bullet is still in the list
                    self.player_bullets.remove(bullet)

    def update_enemy_bullets(self, draw_only=False):
        for bullet in self.enemy_bullets[:]:  # THIS LINE WAS FIXED
            if not draw_only:
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
                    bullet["x"] += bullet["dx"]
                    bullet["y"] += bullet["dy"]

                    # Check if virus bullet should explode
                    explosion_threshold = self.game.screen_height / 2
                    if bullet["y"] >= explosion_threshold:
                        self.game.boss.explode_virus(bullet)
                        self.boss_bullets.remove(bullet)
                        continue  

                self.game.screen.blit(bullet["image"], (bullet["x"], bullet["y"]))

            elif isinstance(bullet, list) and len(bullet) == 4:
                if not draw_only:
                    bullet[0] += bullet[2] 
                    bullet[1] += bullet[3]  

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
                continue  # Debug to show any skipped malformed bullets
        
            if (self.game.player.x < bullet[0] < self.game.player.x + self.game.player.width and
                self.game.player.y < bullet[1] < self.game.player.y + self.game.player.height):
                if not self.game.player.invulnerable:
                    self.boss_bullets.remove(bullet)
                    return True
        return False
