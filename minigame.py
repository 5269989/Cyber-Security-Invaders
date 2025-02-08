import pygame
import random

class HackingMiniGame:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.screen_width = game.screen_width
        self.screen_height = game.screen_height
        self.grid_size = 8
        self.chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        self.words = ["SECURE", "ACCESS", "SYSTEM", "DEFEND", "SHIELD"]
        self.correct_word = random.choice(self.words)
        self.selected_row = 0
        self.selected_col = 0
        self.input_buffer = []
        self.time_limit = 15  # Editable timer variable
        self.start_time = pygame.time.get_ticks() / 1000
        self.grid = []
        self.generate_grid()

    def generate_grid(self):
        # Ensure the word fits in the grid
        word_length = len(self.correct_word)
        max_start = self.grid_size - word_length
        if max_start < 0:
            raise ValueError("Word too long for grid size")
        start_col = random.randint(0, max_start)
        row = random.randint(0, self.grid_size - 1)
        # Replace the grid positions with the word
        for i in range(word_length):
            self.grid[row][start_col + i] = self.correct_word[i]

    def show_instructions(self):
        """Display minigame instructions splash screen"""
        self.screen.fill(self.game.BLACK)
        
        # Title
        title = self.game.bold_font.render("HACKING MINIGAME", True, self.game.GREEN)
        title_rect = title.get_rect(center=(self.screen_width//2, 100))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            "Find the hidden security word in the grid!",
            "Use arrow keys to navigate",
            "Press ENTER to select letters",
            "Press DEL to remove letters",
            f"Max {len(self.correct_word)} letters, Time limit: {self.time_limit}s",
            "Success: Boss remains normal",
            "Failure: Boss enters rage mode!",
            "Press any key to start..."
        ]
        
        y = 200
        for line in instructions:
            text = self.game.font.render(line, True, self.game.WHITE)
            text_rect = text.get_rect(center=(self.screen_width//2, y))
            self.screen.blit(text, text_rect)
            y += 40
            
        pygame.display.flip()
        self.game.wait_for_keypress()

    def draw(self, remaining_time):
        """Draw all game elements"""
        self.screen.fill(self.game.BLACK)
        
        # Timer
        timer_text = self.game.font.render(f"TIME: {int(remaining_time)}", True, 
                                         self.game.RED if remaining_time < 5 else self.game.WHITE)
        self.screen.blit(timer_text, (self.screen_width - 150, 10))
        
        # Grid
        cell_size = 40
        start_x = (self.screen_width - (self.grid_size * cell_size)) // 2
        start_y = (self.screen_height - (self.grid_size * cell_size)) // 2
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = start_x + col * cell_size
                y = start_y + row * cell_size
                char = self.grid[row][col]
                
                # Draw selection box
                if row == self.selected_row and col == self.selected_col:
                    pygame.draw.rect(self.screen, self.game.GREEN, (x-2, y-2, cell_size+4, cell_size+4), 3)
                
                # Draw character
                text = self.game.font.render(char, True, self.game.WHITE)
                self.screen.blit(text, (x + 10, y + 10))
        
        # Input buffer
        input_text = self.game.font.render("".join(self.input_buffer), True, self.game.WHITE)
        input_rect = input_text.get_rect(center=(self.screen_width//2, start_y + (self.grid_size * cell_size) + 50))
        self.screen.blit(input_text, input_rect)
        
        # Input status
        status_color = self.game.RED if len(self.input_buffer) >= 6 else self.game.WHITE
        status_text = self.game.font.render(f"Letters: {len(self.input_buffer)}/6", True, status_color)
        self.screen.blit(status_text, (self.screen_width//2 - 50, input_rect.bottom + 10))

    def show_result(self, success):
        """Show win/lose result screen"""
        self.screen.fill(self.game.BLACK)
        
        result_text = "ACCESS GRANTED!" if success else "ACCESS DENIED!"
        color = self.game.GREEN if success else self.game.RED
        text = self.game.bold_font.render(result_text, True, color)
        text_rect = text.get_rect(center=(self.screen_width//2, self.screen_height//2))
        self.screen.blit(text, text_rect)
        
        if not success:
            effect_text = self.game.font.render("The boss is entering rage mode!", True, self.game.RED)
            effect_rect = effect_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 50))
            self.screen.blit(effect_text, effect_rect)
        
        prompt = self.game.font.render("Press any key to continue...", True, self.game.WHITE)
        prompt_rect = prompt.get_rect(center=(self.screen_width//2, self.screen_height//2 + 100))
        self.screen.blit(prompt, prompt_rect)
        
        pygame.display.flip()
        self.game.wait_for_keypress()

    def run(self):
        """Main minigame loop"""
        self.show_instructions()
        self.start_time = pygame.time.get_ticks() / 1000  # Reset timer after instructions
        success = False
        running = True
        
        while running:
            # Calculate time remaining
            current_time = pygame.time.get_ticks() / 1000
            elapsed = current_time - self.start_time
            remaining = self.time_limit - elapsed
            
            # Handle timeout
            if remaining <= 0:
                running = False
                success = False
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                    
                    # Navigation
                    if event.key == pygame.K_UP:
                        self.selected_row = max(0, self.selected_row - 1)
                    elif event.key == pygame.K_DOWN:
                        self.selected_row = min(self.grid_size-1, self.selected_row + 1)
                    elif event.key == pygame.K_LEFT:
                        self.selected_col = max(0, self.selected_col - 1)
                    elif event.key == pygame.K_RIGHT:
                        self.selected_col = min(self.grid_size-1, self.selected_col + 1)
                    
                    # Selection
                    elif event.key == pygame.K_RETURN:
                        if len(self.input_buffer) < 6:
                            char = self.grid[self.selected_row][self.selected_col]
                            self.input_buffer.append(char)
                    
                    # Deletion
                    elif event.key == pygame.K_DELETE:
                        if self.input_buffer:
                            self.input_buffer.pop()
            
            # Check win condition
            if "".join(self.input_buffer) == self.correct_word:
                running = False
                success = True
            
            # Check max letters exceeded
            if len(self.input_buffer) > 6:
                running = False
                success = False
            
            # Draw everything
            self.draw(remaining)
            pygame.display.flip()
            self.game.clock.tick(60)
        
        self.show_result(success)
        return success
