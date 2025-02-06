import pygame
import random

class HackingMiniGame:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.screen_width = game.screen_width
        self.screen_height = game.screen_height
        self.grid_size = 8  # Size of the grid (8x8)
        self.chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        self.words = ["SECURE", "ACCESS", "SYSTEM", "DEFEND", "SHIELD"]
        self.correct_word = random.choice(self.words)
        self.selected_row = 0
        self.selected_col = 0
        self.input_buffer = []
        self.time_limit = 15  # Editable variable for countdown
        self.start_time = pygame.time.get_ticks() / 1000  # Convert to seconds
        self.grid = []
        self.generate_grid()

    def generate_grid(self):
        """Generate the grid with the correct word hidden in a random row."""
        # Initialize grid with random characters
        self.grid = [[random.choice(self.chars) for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Place correct word in a random row horizontally
        row = random.randint(0, self.grid_size - 1)
        start_col = random.randint(0, self.grid_size - len(self.correct_word))
        for i, c in enumerate(self.correct_word):
            self.grid[row][start_col + i] = c

    def draw(self, remaining_time):
        """Draw all elements of the minigame."""
        self.screen.fill(self.game.BLACK)
        
        # Draw timer
        timer_text = self.game.font.render(f"TIME: {int(remaining_time)}", True, self.game.RED)
        self.screen.blit(timer_text, (self.screen_width - 150, 10))
        
        # Draw instruction box (green panel)
        instruction_box = pygame.Rect(self.screen_width - 300, 50, 280, 200)
        pygame.draw.rect(self.screen, self.game.GREEN, instruction_box)
        instructions = [
            "Use arrow keys to navigate",
            "ENTER to select letters",
            "DEL to remove letters",
            "Find the hidden word!",
            "Max letters: 6"
        ]
        y_offset = 60
        for line in instructions:
            text = self.game.font.render(line, True, self.game.BLACK)
            self.screen.blit(text, (self.screen_width - 290, y_offset))
            y_offset += 30
        
        # Draw grid
        cell_size = 40
        grid_width = self.grid_size * cell_size
        start_x = (self.screen_width - grid_width) // 2
        start_y = (self.screen_height - grid_width) // 2 - 50
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = start_x + col * cell_size
                y = start_y + row * cell_size
                char = self.grid[row][col]
                color = self.game.WHITE
                # Highlight selected cell
                if row == self.selected_row and col == self.selected_col:
                    pygame.draw.rect(self.screen, self.game.GREEN, (x, y, cell_size, cell_size), 3)
                text_surface = self.game.font.render(char, True, color)
                self.screen.blit(text_surface, (x + 10, y + 10))
        
        # Draw input buffer
        input_text = self.game.font.render("".join(self.input_buffer), True, self.game.WHITE)
        input_rect = input_text.get_rect(center=(self.screen_width // 2, start_y + grid_width + 50))
        self.screen.blit(input_text, input_rect)
        
        # Draw current word length
        length_text = self.game.font.render(f"Letters: {len(self.input_buffer)}/6", True, self.game.WHITE)
        self.screen.blit(length_text, (self.screen_width // 2 - 50, start_y + grid_width + 80))

    def show_result(self, success):
        """Display win/lose screen."""
        if success:
            text = "ACCESS GRANTED!"
            color = self.game.GREEN
        else:
            text = "ACCESS DENIED!"
            color = self.game.RED
        
        # Draw result text
        result_surface = self.game.bold_font.render(text, True, color)
        result_rect = result_surface.get_rect(center=(self.screen_width//2, self.screen_height//2))
        self.screen.blit(result_surface, result_rect)
        
        # Draw continue prompt
        prompt = "Press any key to continue..."
        prompt_surface = self.game.font.render(prompt, True, self.game.WHITE)
        prompt_rect = prompt_surface.get_rect(center=(self.screen_width//2, self.screen_height//2 + 50))
        self.screen.blit(prompt_surface, prompt_rect)
        
        pygame.display.flip()
        
        # Wait for user input
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                    waiting = False

    def run(self):
        """Main minigame loop."""
        running = True
        success = False
        
        while running:
            current_time = pygame.time.get_ticks() / 1000  # Current time in seconds
            elapsed = current_time - self.start_time
            remaining_time = max(self.time_limit - elapsed, 0)
            
            # Check timeout
            if remaining_time <= 0:
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
                    # Movement controls
                    elif event.key == pygame.K_UP:
                        self.selected_row = (self.selected_row - 1) % self.grid_size
                    elif event.key == pygame.K_DOWN:
                        self.selected_row = (self.selected_row + 1) % self.grid_size
                    elif event.key == pygame.K_LEFT:
                        self.selected_col = (self.selected_col - 1) % self.grid_size
                    elif event.key == pygame.K_RIGHT:
                        self.selected_col = (self.selected_col + 1) % self.grid_size
                    # Selection controls
                    elif event.key == pygame.K_RETURN:
                        if len(self.input_buffer) < 6:
                            char = self.grid[self.selected_row][self.selected_col]
                            self.input_buffer.append(char)
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
            
            # Update display
            self.draw(remaining_time)
            pygame.display.flip()
            self.game.clock.tick(60)
        
        # Show result screen
        self.show_result(success)
        return success
