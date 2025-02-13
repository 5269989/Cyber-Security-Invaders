import pygame

class Barricade:
    def __init__(self, x, y, block_width=15, block_height=10, cols=10, rows=4, saved_blocks=None):
        self.blocks = []
        if saved_blocks:  # If loading from save, restore the saved blocks
            for block in saved_blocks:
                block_rect = pygame.Rect(block["x"], block["y"], block_width, block_height)
                self.blocks.append({"rect": block_rect})
        else:  # Normal barricade creation
            for row in range(rows):
                for col in range(cols):
                    block_rect = pygame.Rect(
                        x + col * block_width,
                        y + row * block_height,
                        block_width,
                        block_height
                    )
                    self.blocks.append({"rect": block_rect})

    def draw(self, screen):
        for block in self.blocks:
            pygame.draw.rect(screen, (0, 255, 0), block["rect"])  # Always green

    def hit(self, pos, is_player_bullet=False):
        for block in self.blocks:
            if block["rect"].collidepoint(pos):
                if not is_player_bullet:
                    self.blocks.remove(block)  # Enemy bullets remove the block
                return True  # Bullet should always be removed
        return False

class BarricadeManager:
    def __init__(self, game):
        self.game = game
        self.barricades = []
        self.create_barricades()

    def create_barricades(self, saved_state=None):
        self.barricades = []  # Clear any old barricades
        barricade_y = self.game.screen_height - 120
        block_width = 15
        cols = 10  
        barricade_width = cols * block_width
        positions = [
            self.game.screen_width // 3 - barricade_width // 2,
            2 * self.game.screen_width // 3 - barricade_width // 2
        ]
    
        if saved_state:  # Restoring from save
            for x, barricade_blocks in zip(positions, saved_state):
                self.barricades.append(Barricade(x, barricade_y, block_width, 10, cols, 4, saved_blocks=barricade_blocks))
        else:  # Creating new barricades
            for x in positions:
                self.barricades.append(Barricade(x, barricade_y, block_width, 10, cols, 4))



    def update(self):
        for bullet in self.game.bullet_manager.enemy_bullets[:]:
            bullet_pos = (
                bullet[0] + self.game.bullet_manager.bullet_width / 2,
                bullet[1] + self.game.bullet_manager.enemy_bullet_height / 2
            )
            for barricade in self.barricades:
                if barricade.hit(bullet_pos, is_player_bullet=False):
                    if bullet in self.game.bullet_manager.enemy_bullets:
                        self.game.bullet_manager.enemy_bullets.remove(bullet)
                    break

        for bullet in self.game.bullet_manager.player_bullets[:]:
            bullet_pos = (bullet[0], bullet[1])
            for barricade in self.barricades:
                if barricade.hit(bullet_pos, is_player_bullet=True):
                    if bullet in self.game.bullet_manager.player_bullets:
                        self.game.bullet_manager.player_bullets.remove(bullet)
                    break

    def draw(self):
        for barricade in self.barricades:
            barricade.draw(self.game.screen)

    def reset(self):
        self.create_barricades()
