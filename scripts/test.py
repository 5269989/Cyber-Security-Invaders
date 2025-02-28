import pygame
import random

class PhishingMiniGame:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.screen_width = game.screen_width
        self.screen_height = game.screen_height
        
        # Game settings
        self.time_limit = 30  # Time limit in seconds
        self.start_time = pygame.time.get_ticks() / 1000
        self.emails_to_play = 5
        self.correct_needed = 3
        
        # Player state
        self.correct_answers = 0
        self.current_email_index = 0
        self.rod_position = self.screen_width // 2
        self.rod_speed = 8
        self.rod_state = "ready"  # "ready", "casting", "reeling"
        self.line_y = 150  # Initial line position
        self.caught_email = None
        self.player_choice = None  # None, "legitimate", "phishing"
        self.choice_made = False
        self.choice_correct = False
        self.show_result_time = 0
        self.email_display_time = 0  # Time when email was displayed
        self.answer_cooldown = 1.0  # 1 second cooldown before allowing answers
        
        # Email elements
        self.emails = self.generate_emails()
        self.email_pool = random.sample(self.emails, self.emails_to_play)
        self.email_positions = self.generate_email_positions()
        self.email_speed = 2
        
        # UI elements
        self.rod_height = 100
        self.email_width = 80
        self.email_height = 60
        
        # Controls state for continuous movement
        self.moving_left = False
        self.moving_right = False
        
    def generate_emails(self):
        """Generate a pool of legitimate and phishing emails"""
        emails = [
            {
                "sender": "paypal@service.paypal.com",
                "subject": "Your account needs verification",
                "body": "Dear customer, please verify your account by clicking on the following link: paypal.com/verify",
                "is_phishing": False
            },
            {
                "sender": "paypa1@service-paypal.net",
                "subject": "URGENT: Account Compromised",
                "body": "Your account has been compromised! Click here to reset: paypa1.com/reset",
                "is_phishing": True
            },
            {
                "sender": "amazon@order-confirmation.amazon.com",
                "subject": "Your Amazon Order #5789302",
                "body": "Thank you for your recent purchase. View your order details here.",
                "is_phishing": False
            },
            {
                "sender": "amazonsupport@amazon-orders.co",
                "subject": "Problem with recent order",
                "body": "There was a problem with your recent order. Click here to fix: amaz0n-verify.co/fix",
                "is_phishing": True
            },
            {
                "sender": "no-reply@netflix.com",
                "subject": "Your Netflix subscription",
                "body": "Your monthly subscription has been processed. View your billing statement here.",
                "is_phishing": False
            },
            {
                "sender": "netflix-support@netflixupdate.co",
                "subject": "Netflix Payment Failed",
                "body": "Your payment method has expired. Update payment here: netflx-account.co/billing",
                "is_phishing": True
            },
            {
                "sender": "support@apple.com",
                "subject": "Your Apple ID receipt",
                "body": "Your recent app purchase has been completed. No action is required.",
                "is_phishing": False
            },
            {
                "sender": "apple-security@secure-apple.net",
                "subject": "Security Alert: Sign-in detected",
                "body": "We detected a sign-in from a new device. Verify your identity: apple-verify.net/secure",
                "is_phishing": True
            },
            {
                "sender": "noreply@github.com",
                "subject": "Security alert: new SSH key added",
                "body": "A new SSH key was added to your GitHub account. If this was you, no action is needed.",
                "is_phishing": False
            },
            {
                "sender": "github-security@github-alerts.net",
                "subject": "Critical Security Vulnerability",
                "body": "Your repository has a security vulnerability. Download this patch: github-patch.co/fix",
                "is_phishing": True
            }
        ]
        return emails
    
    def generate_email_positions(self):
        """Generate positions for the emails swimming across the screen"""
        email_positions = []
        for i in range(self.emails_to_play):
            x = random.randint(100, self.screen_width - 100)
            y = random.randint(350, self.screen_height - 150)
            direction = random.choice([-1, 1])  # -1 for left, 1 for right
            email_positions.append({"x": x, "y": y, "direction": direction})
        return email_positions
    
    def show_instructions(self):
        """Show game instructions"""
        self.screen.fill(self.game.BLACK)
        title = self.game.bold_font.render("PHISHING AWARENESS MINIGAME", True, self.game.GREEN)
        title_rect = title.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(title, title_rect)

        instructions = [
            [("Catch and identify phishing emails!", self.game.WHITE)],
            [("Use ", self.game.WHITE), ("LEFT/RIGHT ARROWS", self.game.LIGHTBLUE), (" to move your fishing rod", self.game.WHITE)],
            [("Press ", self.game.WHITE), ("SPACE", self.game.LIGHTBLUE), (" to cast your line", self.game.WHITE)],
            [("After catching an email, press ", self.game.WHITE), ("LEFT ARROW", self.game.GREEN), (" for legitimate emails", self.game.WHITE)],
            [("or ", self.game.WHITE), ("RIGHT ARROW", self.game.RED), (" for phishing emails", self.game.WHITE)],
            [(f"Correctly identify {self.correct_needed} out of {self.emails_to_play} emails to win!", self.game.WHITE)],
            [(f"Time limit: {self.time_limit}s", self.game.WHITE)],
            [(" ", self.game.WHITE)],
            [("Press any key to start...", self.game.YELLOW)]
        ]

        y = 200
        for line in instructions:
            total_width = sum(self.game.font.size(part[0])[0] for part in line)
            start_x = (self.screen_width - total_width) // 2
            x_offset = 0
            for part_text, part_color in line:
                text_surface = self.game.font.render(part_text, True, part_color)
                self.screen.blit(text_surface, (start_x + x_offset, y))
                x_offset += text_surface.get_width()
            y += 40

        pygame.display.flip()
        self.game.wait_for_keypress()
    
    def draw_fishing_rod(self):
        """Draw the fishing rod and line"""
        # Rod handle
        pygame.draw.rect(self.screen, (139, 69, 19), (self.rod_position - 5, 50, 10, 30))
        
        # Rod
        pygame.draw.line(self.screen, (139, 69, 19), (self.rod_position, 50), (self.rod_position, 80), 3)
        
        # Fishing line
        if self.rod_state in ["casting", "reeling"]:
            line_end = self.line_y if self.caught_email is None else self.email_positions[self.current_email_index]["y"]
            pygame.draw.line(self.screen, self.game.WHITE, (self.rod_position, 80), (self.rod_position, line_end), 1)
            
            # Draw hook - larger hitbox
            if self.caught_email is None:
                pygame.draw.arc(self.screen, self.game.WHITE, (self.rod_position - 7, self.line_y - 7, 14, 14), 0, 3.14, 2)
                # Draw a small circle to make hook more visible
                pygame.draw.circle(self.screen, self.game.WHITE, (self.rod_position, self.line_y), 3)
    
    def draw_emails(self):
        """Draw the emails swimming in the water"""
        for i, position in enumerate(self.email_positions):
            if i == self.current_email_index or i > self.current_email_index:
                # Email icon (envelope)
                if self.caught_email is not None and i == self.current_email_index:
                    # Don't draw caught email in water
                    continue
                    
                color = self.game.LIGHTBLUE
                pygame.draw.rect(self.screen, color, (position["x"] - 20, position["y"] - 15, 40, 30))
                pygame.draw.polygon(self.screen, self.game.WHITE, [
                    (position["x"] - 20, position["y"] - 15),
                    (position["x"], position["y"]),
                    (position["x"] + 20, position["y"] - 15)
                ])
    
    def draw_water(self):
        """Draw the water area"""
        pygame.draw.rect(self.screen, (0, 0, 139), (0, 300, self.screen_width, self.screen_height - 300))
        
        # Draw water surface
        for i in range(0, self.screen_width, 40):
            pygame.draw.arc(self.screen, (30, 144, 255), (i, 290, 40, 20), 3.14, 2 * 3.14, 2)
    
    def draw_email_details(self):
        """Draw the details of the caught email"""
        if self.caught_email is not None:
            email = self.email_pool[self.current_email_index]
            
            # Email background
            pygame.draw.rect(self.screen, (220, 220, 220), (self.screen_width // 4, 100, self.screen_width // 2, 180))
            
            # Email content
            sender_text = self.game.font.render(f"From: {email['sender']}", True, self.game.BLACK)
            subject_text = self.game.font.render(f"Subject: {email['subject']}", True, self.game.BLACK)
            
            # Split body text to fit
            body_words = email['body'].split()
            body_lines = []
            current_line = ""
            for word in body_words:
                test_line = current_line + " " + word if current_line else word
                if self.game.font.size(test_line)[0] < self.screen_width // 2 - 20:
                    current_line = test_line
                else:
                    body_lines.append(current_line)
                    current_line = word
            if current_line:
                body_lines.append(current_line)
            
            # Render email parts
            self.screen.blit(sender_text, (self.screen_width // 4 + 10, 110))
            self.screen.blit(subject_text, (self.screen_width // 4 + 10, 140))
            
            for i, line in enumerate(body_lines):
                body_text = self.game.font.render(line, True, self.game.BLACK)
                self.screen.blit(body_text, (self.screen_width // 4 + 10, 170 + i * 20))
            
            # Decision prompt
            current_time = pygame.time.get_ticks() / 1000
            time_since_display = current_time - self.email_display_time
            
            if not self.choice_made:
                prompt_text = self.game.font.render("Is this email legitimate or phishing?", True, self.game.WHITE)
                
                # Show cooldown or controls based on time elapsed
                if time_since_display < self.answer_cooldown:
                    cooldown_text = self.game.font.render(f"Ready in: {max(0, round(self.answer_cooldown - time_since_display, 1))}s", True, self.game.YELLOW)
                    self.screen.blit(cooldown_text, (self.screen_width // 2 - cooldown_text.get_width() // 2, 320))
                else:
                    left_text = self.game.font.render("LEFT = Legitimate", True, self.game.GREEN)
                    right_text = self.game.font.render("RIGHT = Phishing", True, self.game.RED)
                    self.screen.blit(left_text, (self.screen_width // 4, 320))
                    self.screen.blit(right_text, (3 * self.screen_width // 4 - right_text.get_width(), 320))
                
                self.screen.blit(prompt_text, (self.screen_width // 2 - prompt_text.get_width() // 2, 290))
            else:
                # Show if answer was correct
                if self.choice_correct:
                    result_text = self.game.font.render("CORRECT!", True, self.game.GREEN)
                else:
                    result_text = self.game.font.render("INCORRECT!", True, self.game.RED)
                
                is_phishing_text = self.game.font.render(
                    f"This email is {'phishing' if email['is_phishing'] else 'legitimate'}", 
                    True, 
                    self.game.RED if email['is_phishing'] else self.game.GREEN
                )
                
                self.screen.blit(result_text, (self.screen_width // 2 - result_text.get_width() // 2, 290))
                self.screen.blit(is_phishing_text, (self.screen_width // 2 - is_phishing_text.get_width() // 2, 320))
    
    def draw_progress(self):
        """Draw game progress (score and timer)"""
        # Timer
        current_time = pygame.time.get_ticks() / 1000
        elapsed = current_time - self.start_time
        remaining = max(0, self.time_limit - elapsed)
        
        timer_text = self.game.font.render(f"TIME: {int(remaining)}s", True, 
                                         self.game.RED if remaining < 5 else self.game.WHITE)
        self.screen.blit(timer_text, (10, 10))
        
        # Score
        score_text = self.game.font.render(f"SCORE: {self.correct_answers}/{self.correct_needed} needed", True, self.game.WHITE)
        self.screen.blit(score_text, (self.screen_width - score_text.get_width() - 10, 10))
        
        # Progress indicator
        progress_text = self.game.font.render(f"Email {self.current_email_index + 1}/{self.emails_to_play}", True, self.game.WHITE)
        self.screen.blit(progress_text, (self.screen_width // 2 - progress_text.get_width() // 2, 10))
    
    def draw(self):
        """Draw the complete game state"""
        self.screen.fill(self.game.BLACK)
        
        # Draw water and environment
        self.draw_water()
        
        # Draw emails in the water
        self.draw_emails()
        
        # Draw fishing rod
        self.draw_fishing_rod()
        
        # Draw caught email if any
        self.draw_email_details()
        
        # Draw score and timer
        self.draw_progress()
        
        pygame.display.flip()
    
    def update_email_positions(self):
        """Update the positions of the emails in the water"""
        for i, position in enumerate(self.email_positions):
            if i == self.current_email_index and self.caught_email is not None:
                continue  # Don't move caught email
                
            position["x"] += position["direction"] * self.email_speed
            
            # Bounce off edges
            if position["x"] <= 40 or position["x"] >= self.screen_width - 40:
                position["direction"] *= -1
    
    def update_rod_position(self):
        """Update rod position based on continuous movement"""
        if self.moving_left:
            self.rod_position = max(50, self.rod_position - self.rod_speed)
        if self.moving_right:
            self.rod_position = min(self.screen_width - 50, self.rod_position + self.rod_speed)
    
    def check_hook_collision(self):
        """Check if the hook collides with any email - with larger hitbox"""
        if self.rod_state == "casting" and self.caught_email is None:
            for i, position in enumerate(self.email_positions):
                if i == self.current_email_index:
                    # Calculate distance between hook and email
                    dx = self.rod_position - position["x"]
                    dy = self.line_y - position["y"]
                    distance = (dx * dx + dy * dy) ** 0.5
                    
                    # Larger hitbox - 40 pixel radius
                    if distance < 40:
                        self.caught_email = self.email_pool[i]
                        self.rod_state = "reeling"
                        self.email_display_time = pygame.time.get_ticks() / 1000
                        break
    
    def show_result(self, success):
        """Show the final result screen"""
        self.screen.fill(self.game.BLACK)
        
        result_text = "SECURITY AWARENESS PASSED!" if success else "SECURITY AWARENESS FAILED!"
        color = self.game.GREEN if success else self.game.RED
        text = self.game.bold_font.render(result_text, True, color)
        text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(text, text_rect)
        
        score_text = self.game.font.render(f"You identified {self.correct_answers} out of {self.emails_to_play} emails correctly", True, self.game.WHITE)
        score_rect = score_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
        self.screen.blit(score_text, score_rect)
        
        if not success:
            effect_text = self.game.font.render("The boss is entering rage mode!", True, self.game.RED)
            effect_rect = effect_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 100))
            self.screen.blit(effect_text, effect_rect)
            self.game.boss.enable_rage_mode()
        
        prompt = self.game.font.render("Press any key to continue...", True, self.game.WHITE)
        prompt_rect = prompt.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 150))
        self.screen.blit(prompt, prompt_rect)
        
        pygame.display.flip()
        self.game.wait_for_keypress()
    
    def run(self):
        """Main game loop"""
        self.show_instructions()
        # Reset timer so it starts after instructions are dismissed
        self.start_time = pygame.time.get_ticks() / 1000
        success = False
        running = True
        
        while running:
            # Calculate time remaining
            current_time = pygame.time.get_ticks() / 1000
            elapsed = current_time - self.start_time
            remaining = self.time_limit - elapsed
            
            # Check time limit
            if remaining <= 0 and self.caught_email is None:
                running = False
            
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                
                if event.type == pygame.KEYDOWN:
                    # Setup continuous movement with key down
                    if event.key == pygame.K_LEFT:
                        self.moving_left = True
                    elif event.key == pygame.K_RIGHT:
                        self.moving_right = True
                    
                    # Other controls
                    if self.caught_email is None:
                        # Fishing controls
                        if event.key == pygame.K_SPACE and self.rod_state == "ready":
                            self.rod_state = "casting"
                    else:
                        # Email judgment controls (if email is caught)
                        current_time = pygame.time.get_ticks() / 1000
                        time_since_display = current_time - self.email_display_time
                        
                        if not self.choice_made and time_since_display >= self.answer_cooldown:
                            if event.key == pygame.K_LEFT:  # Legitimate
                                self.player_choice = "legitimate"
                                self.choice_made = True
                                self.choice_correct = not self.email_pool[self.current_email_index]["is_phishing"]
                                if self.choice_correct:
                                    self.correct_answers += 1
                                self.show_result_time = current_time
                            elif event.key == pygame.K_RIGHT:  # Phishing
                                self.player_choice = "phishing"
                                self.choice_made = True
                                self.choice_correct = self.email_pool[self.current_email_index]["is_phishing"]
                                if self.choice_correct:
                                    self.correct_answers += 1
                                self.show_result_time = current_time
                
                # Handle key up events for continuous movement
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.moving_left = False
                    elif event.key == pygame.K_RIGHT:
                        self.moving_right = False
            
            # Update rod position based on continuous movement
            if self.caught_email is None:
                self.update_rod_position()
            
            # Update fishing line when casting
            if self.rod_state == "casting" and self.caught_email is None:
                self.line_y += 5
                
                # Check for collisions with emails
                self.check_hook_collision()
                
                # If line goes too far, reel it back in
                if self.line_y >= self.screen_height - 50:
                    self.rod_state = "reeling"
            
            # Reel in the line
            if self.rod_state == "reeling" and self.caught_email is None:
                self.line_y -= 7
                if self.line_y <= 80:
                    self.rod_state = "ready"
                    self.line_y = 150
            
            # Move to next email after showing result
            if self.choice_made and current_time - self.show_result_time > 2:
                self.current_email_index += 1
                self.caught_email = None
                self.choice_made = False
                self.rod_state = "ready"
                self.line_y = 150
            
            # Check win/lose conditions
            if self.current_email_index >= self.emails_to_play:
                running = False
                success = self.correct_answers >= self.correct_needed
            
            # Update email positions
            self.update_email_positions()
            
            # Draw everything
            self.draw()
            self.game.clock.tick(60)
        
        self.show_result(success)
        return success
