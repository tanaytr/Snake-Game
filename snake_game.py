import pygame
import sys
import random
import time
import os
from pygame.math import Vector2

# Initialize pygame
pygame.init()

# Constants
CELL_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 20
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT
NOKIA_GREEN = (170, 215, 81)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FPS = 10

# Helper functions for dynamic grid dimensions
def get_grid_width():
    return SCREEN_WIDTH // CELL_SIZE

def get_grid_height():
    return SCREEN_HEIGHT // CELL_SIZE

# Initialize screen - make it resizable
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Hungry Snake's Megalomania")
clock = pygame.time.Clock()

# Font - Using Blox BRK from system fonts
try:
    font = pygame.font.SysFont('Blox BRK', 20)  # Main game font
    # Try to load Terminal and Fixedsys fonts from various locations
    try:
        terminal_font = pygame.font.Font('C:/Windows/Fonts/cour.ttf', 20)  # Try Courier New as Terminal
        fixedsys_font = pygame.font.Font('C:/Windows/Fonts/cour.ttf', 16)  # Try Courier New as Fixedsys
    except:
        try:
            terminal_font = pygame.font.Font('C:/Windows/Fonts/consola.ttf', 20)  # Try Consolas
            fixedsys_font = pygame.font.Font('C:/Windows/Fonts/consola.ttf', 16)  # Try Consolas
        except:
            terminal_font = pygame.font.SysFont('Courier New', 20, bold=True)  # Fallback to system Courier New
            fixedsys_font = pygame.font.SysFont('Courier New', 16)  # Fallback to system Courier New
except Exception as e:
    print(f"Font loading error: {e}")
    font = pygame.font.SysFont('Arial', 20)
    terminal_font = pygame.font.SysFont('Courier New', 20, bold=True)
    fixedsys_font = pygame.font.SysFont('Courier New', 16)
    print("Could not load some fonts, using fallback fonts")

class Snake:
    def __init__(self):
        self.body = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]
        self.direction = Vector2(1, 0)
        self.new_block = False
        
    def draw(self, color_mode):
        # Draw head with triangle
        head_rect = pygame.Rect(self.body[0].x * CELL_SIZE, self.body[0].y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        
        if color_mode:
            head_color = WHITE
            body_color = BLACK
        else:
            head_color = (0, 100, 0)
            body_color = (0, 150, 0)
        
        pygame.draw.rect(screen, body_color, head_rect)
        
        # Draw triangle on head to indicate direction
        if self.direction == Vector2(1, 0):  # Right
            points = [
                (head_rect.right, head_rect.centery),
                (head_rect.right - CELL_SIZE/2, head_rect.top),
                (head_rect.right - CELL_SIZE/2, head_rect.bottom)
            ]
        elif self.direction == Vector2(-1, 0):  # Left
            points = [
                (head_rect.left, head_rect.centery),
                (head_rect.left + CELL_SIZE/2, head_rect.top),
                (head_rect.left + CELL_SIZE/2, head_rect.bottom)
            ]
        elif self.direction == Vector2(0, 1):  # Down
            points = [
                (head_rect.centerx, head_rect.bottom),
                (head_rect.left, head_rect.bottom - CELL_SIZE/2),
                (head_rect.right, head_rect.bottom - CELL_SIZE/2)
            ]
        else:  # Up
            points = [
                (head_rect.centerx, head_rect.top),
                (head_rect.left, head_rect.top + CELL_SIZE/2),
                (head_rect.right, head_rect.top + CELL_SIZE/2)
            ]
        
        pygame.draw.polygon(screen, head_color, points)
        
        # Draw body
        for block in self.body[1:]:
            block_rect = pygame.Rect(block.x * CELL_SIZE, block.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, body_color, block_rect)
    
    def move(self):
        if self.new_block:
            body_copy = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy
            
        # Handle screen wrapping for left/right
        for i, block in enumerate(self.body):
            if block.x < 0:
                self.body[i].x = get_grid_width() - 1
            elif block.x >= get_grid_width():
                self.body[i].x = 0
    
    def add_block(self):
        self.new_block = True
    
    def reset(self):
        # Position snake in the middle of the current grid
        grid_width = get_grid_width()
        grid_height = get_grid_height()
        mid_x = grid_width // 2
        mid_y = grid_height // 2
        
        self.body = [Vector2(mid_x, mid_y), Vector2(mid_x-1, mid_y), Vector2(mid_x-2, mid_y)]
        self.direction = Vector2(1, 0)
        self.new_block = False
    
    def check_collision(self):
        # Check if snake hits itself
        if self.body[0] in self.body[1:]:
            return True
        
        # Check if snake hits top or bottom wall
        if self.body[0].y < 0 or self.body[0].y >= get_grid_height():
            return True
            
        return False

class Food:
    def __init__(self):
        self.randomize()
    
    def draw(self, color_mode):
        food_rect = pygame.Rect(self.pos.x * CELL_SIZE, self.pos.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if color_mode:
            pygame.draw.circle(screen, BLACK, food_rect.center, CELL_SIZE/2)
        else:
            pygame.draw.circle(screen, self.color, food_rect.center, CELL_SIZE/2)
    
    def randomize(self):
        grid_width = get_grid_width()
        grid_height = get_grid_height()
        
        # Keep trying until we get a valid position
        while True:
            self.x = random.randint(0, grid_width - 1)
            self.y = random.randint(0, grid_height - 1)
            
            # Avoid top area where score is displayed (first 2 rows)
            if self.y >= 2:
                break
        
        self.pos = Vector2(self.x, self.y)
        self.color = self.random_color()
    
    def random_color(self):
        # Generate random color but avoid green shades
        while True:
            r = random.randint(50, 255)
            g = random.randint(50, 255)
            b = random.randint(50, 255)
            
            # Avoid green colors (where green is dominant)
            if not (g > r and g > b):
                return (r, g, b)
            
            # If we got here, the color was too green, try again

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.obstacles = []  # List to store obstacles
        self.obstacle_count = 0  # Track number of obstacles to show
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.game_started = False
        self.game_completed = False
        self.game_paused = False
        self.bw_mode = False
        self.username = ""
        self.input_active = False
        self.max_username_length = 15
        self.main_menu = True
        self.show_rules = False
        self.show_leaderboard = False
        self.scores_history = []  # List to store historical scores
        self.session_scores = {}  # Dictionary to store scores for current session
        self.load_scores_history()  # Load previous scores
        
    def load_scores_history(self):
        try:
            with open('snake_scores.txt', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    username, score, date_time = line.strip().split('|')
                    self.scores_history.append({
                        'username': username,
                        'score': int(score),
                        'date_time': date_time
                    })
                # Keep only last 25 scores
                self.scores_history = self.scores_history[-25:]
        except FileNotFoundError:
            self.scores_history = []
    
    def save_scores_history(self):
        # Update session best score if needed
        if self.username in self.session_scores:
            if self.score > self.session_scores[self.username]:
                self.session_scores[self.username] = self.score
        else:
            self.session_scores[self.username] = self.score
        
        # Only save if this is the best score for this session
        if self.score == self.session_scores[self.username]:
            from datetime import datetime
            current_time = datetime.now().strftime("%I:%M:%S %p")  # 12-hour format with AM/PM
            current_date = datetime.now().strftime("%Y-%m-%d")
            formatted_datetime = f"{current_date} {current_time}"
            
            # Add new score
            self.scores_history.append({
                'username': self.username,
                'score': self.score,
                'date_time': formatted_datetime
            })
            
            # Keep only last 25 scores
            self.scores_history = sorted(self.scores_history, key=lambda x: x['score'], reverse=True)[:25]
            
            # Save to file
            with open('snake_scores.txt', 'w') as f:
                for score_data in self.scores_history:
                    f.write(f"{score_data['username']}|{score_data['score']}|{score_data['date_time']}\n")

    def handle_resize(self, new_width, new_height):
        # Calculate scaling factors
        width_scale = new_width / SCREEN_WIDTH
        height_scale = new_height / SCREEN_HEIGHT
        
        # Scale snake position
        for i, block in enumerate(self.snake.body):
            self.snake.body[i] = Vector2(
                (block.x * width_scale) // CELL_SIZE,
                (block.y * height_scale) // CELL_SIZE
            )
        
        # Scale food position
        self.food.pos = Vector2(
            (self.food.pos.x * width_scale) // CELL_SIZE,
            (self.food.pos.y * height_scale) // CELL_SIZE
        )
        
        # Scale obstacles
        new_obstacles = []
        for pos in self.obstacles:
            new_pos = Vector2(
                (pos.x * width_scale) // CELL_SIZE,
                (pos.y * height_scale) // CELL_SIZE
            )
            new_obstacles.append(new_pos)
        self.obstacles = new_obstacles

    def update(self):
        if not self.game_started or self.game_completed or self.game_paused:
            return  # Don't update anything if game hasn't started, is completed, or is paused
            
        self.snake.move()
        self.check_collision()
        self.check_fail()
        
        # Update black and white mode
        self.bw_mode = self.score >= 100
        
        # Check for game completion
        if self.score >= 300:
            self.game_completed = True
    
    def draw_elements(self):
        # Draw background
        if self.bw_mode:
            screen.fill(WHITE)
        else:
            screen.fill(NOKIA_GREEN)
        
        # Draw grid lines
        self.draw_grid()
        
        # Main menu screen
        if self.main_menu:
            self.draw_main_menu()
        # Rules screen
        elif self.show_rules:
            self.draw_rules()
        # Leaderboard screen
        elif self.show_leaderboard:
            self.draw_leaderboard()
        # Username input screen
        elif self.input_active:
            self.draw_username_input()
        # Only draw snake and food if game has started and not completed
        elif self.game_started and not self.game_completed:
            # Draw obstacles if score >= 200
            if self.score >= 200:
                self.draw_obstacles()
                
            self.snake.draw(self.bw_mode)
            self.food.draw(self.bw_mode)
            
            # Draw score
            self.draw_score()
        elif self.game_completed:
            # Draw game completion text
            completion_text = font.render('You have completed the game!', True, BLACK if self.bw_mode else WHITE)
            restart_text = font.render('Press SPACE to restart', True, BLACK if self.bw_mode else WHITE)
            
            text_rect1 = completion_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 40))
            text_rect2 = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 10))
            
            screen.blit(completion_text, text_rect1)
            screen.blit(restart_text, text_rect2)
            
            # Display player score
            if self.username:
                player_score_text = font.render(f'{self.username} Scored {self.score}', True, BLACK if self.bw_mode else WHITE)
                player_score_rect = player_score_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 30))
                screen.blit(player_score_text, player_score_rect)
    
    def draw_grid(self):
        grid_color = BLACK if self.bw_mode else (150, 200, 70)
        
        # Draw vertical lines
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(screen, grid_color, (x, 0), (x, SCREEN_HEIGHT), 1)
        
        # Draw horizontal lines
        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, grid_color, (0, y), (SCREEN_WIDTH, y), 1)
    
    def check_collision(self):
        if self.food.pos == self.snake.body[0]:
            # Reposition food
            self.food.randomize()
            
            # Make sure food doesn't appear on snake or obstacles
            while self.food.pos in self.snake.body or self.food.pos in self.obstacles:
                self.food.randomize()
            
            # Grow snake
            self.snake.add_block()
            
            # Increase score - double points in black & white mode
            if self.bw_mode:
                self.score += 20
            else:
                self.score += 10
            
            # Update high score
            if self.score > self.high_score:
                self.high_score = self.score
                
            # Increase obstacle count and generate new obstacles if score >= 200
            if self.score >= 200:
                self.obstacle_count += 1
                self.generate_obstacles()
    
    def check_fail(self):
        # Check if snake hits itself or walls
        if self.snake.check_collision():
            self.game_over = True
            
        # Check if snake hits obstacles
        if self.score >= 200:
            if self.snake.body[0] in self.obstacles:
                self.game_over = True
    
    def reset(self):
        self.snake.reset()
        self.food.randomize()
        self.obstacles = []  # Clear obstacles
        self.obstacle_count = 0  # Reset obstacle count
        self.score = 0
        self.game_over = False
        self.game_completed = False  # Reset game completed state
        self.game_started = True  # Keep the game started after reset
        # Note: We don't reset username or input_active here to keep the username between games
    
    def draw_score(self):
        # Draw score
        score_text = font.render(f'Score: {self.score}', True, BLACK if self.bw_mode else WHITE)
        screen.blit(score_text, (10, 10))
        
        # Draw high score
        high_score_text = font.render(f'High Score: {self.high_score}', True, BLACK if self.bw_mode else WHITE)
        screen.blit(high_score_text, (SCREEN_WIDTH - high_score_text.get_width() - 10, 10))
        
        # Draw pause/play icon if game is in progress
        if self.game_started and not self.game_over and not self.game_completed:
            self.draw_pause_play_icon()
    
    def draw_pause_play_icon(self):
        # Calculate position (middle of the screen at the top)
        icon_x = SCREEN_WIDTH // 2
        icon_y = 20
        icon_size = 15
        
        # Set color based on mode
        icon_color = BLACK if self.bw_mode else WHITE
        
        if self.game_paused:
            # Draw play triangle icon (pointing right)
            points = [
                (icon_x - icon_size//2, icon_y - icon_size//2),
                (icon_x - icon_size//2, icon_y + icon_size//2),
                (icon_x + icon_size//2, icon_y)
            ]
            pygame.draw.polygon(screen, icon_color, points)
        else:
            # Draw pause icon (two vertical bars)
            bar_width = icon_size // 3
            gap = bar_width
            
            # Left bar
            left_bar = pygame.Rect(icon_x - bar_width - gap//2, icon_y - icon_size//2, bar_width, icon_size)
            pygame.draw.rect(screen, icon_color, left_bar)
            
            # Right bar
            right_bar = pygame.Rect(icon_x + gap//2, icon_y - icon_size//2, bar_width, icon_size)
            pygame.draw.rect(screen, icon_color, right_bar)
    
    def generate_obstacles(self):
        # Clear previous obstacles
        self.obstacles = []
        
        grid_width = get_grid_width()
        grid_height = get_grid_height()
        
        # Limit the maximum number of obstacles to prevent impossible gameplay
        max_obstacles = min(self.obstacle_count, 10)
        
        # Generate obstacles based on obstacle_count
        for _ in range(max_obstacles):
            attempts = 0
            while attempts < 100:  # Limit attempts to prevent infinite loop
                attempts += 1
                
                # Generate random position
                x = random.randint(0, grid_width - 1)
                y = random.randint(2, grid_height - 1)  # Start from row 2 to avoid score area
                pos = Vector2(x, y)
                
                # Make sure obstacle doesn't overlap with snake, food, or other obstacles
                if (pos not in self.snake.body and 
                    pos != self.food.pos and 
                    pos not in self.obstacles):
                    self.obstacles.append(pos)
                    break
    
    def draw_obstacles(self):
        obstacle_color = BLACK if self.bw_mode else (255, 0, 0)  # Red in normal mode, black in B&W
        
        for pos in self.obstacles:
            obstacle_rect = pygame.Rect(pos.x * CELL_SIZE, pos.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, obstacle_color, obstacle_rect)
    
    def get_game_speed(self):
        # Return game speed based on score
        if self.score < 50:
            return FPS / 2  # Half speed at start (50%)
        elif self.score < 100:
            return FPS * 0.75  # 75% speed at score 50
        elif self.score < 200:
            return FPS  # Normal speed at score 100 (100%)
        else:
            return FPS * 2  # Double speed at score 200 (200%)

    def draw_username_input(self):
        # Draw title
        title_text = font.render("Hungry Snake's Megalomania", True, BLACK if self.bw_mode else WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
        screen.blit(title_text, title_rect)
        
        # Draw input prompt
        prompt_text = font.render("Enter your name:", True, BLACK if self.bw_mode else WHITE)
        prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 40))
        screen.blit(prompt_text, prompt_rect)
        
        # Draw input box
        input_box_width = 300
        input_box_height = 40
        input_box_x = SCREEN_WIDTH/2 - input_box_width/2
        input_box_y = SCREEN_HEIGHT/2
        input_box = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)
        
        # Draw box outline
        pygame.draw.rect(screen, BLACK if self.bw_mode else WHITE, input_box, 2)
        
        # Draw username text
        username_text = font.render(self.username, True, BLACK if self.bw_mode else WHITE)
        # Center text in box
        text_x = input_box_x + 10
        text_y = input_box_y + (input_box_height - username_text.get_height()) / 2
        screen.blit(username_text, (text_x, text_y))
        
        # Draw cursor
        if pygame.time.get_ticks() % 1000 < 500:  # Blink cursor every 0.5 seconds
            cursor_x = text_x + username_text.get_width()
            cursor_y = text_y
            cursor_height = username_text.get_height()
            pygame.draw.line(screen, BLACK if self.bw_mode else WHITE, 
                            (cursor_x, cursor_y), 
                            (cursor_x, cursor_y + cursor_height), 
                            2)
        
        # Draw instructions
        instructions_text = font.render("Press ENTER to play", True, BLACK if self.bw_mode else WHITE)
        instructions_rect = instructions_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 60))
        screen.blit(instructions_text, instructions_rect)

    def draw_main_menu(self):
        # Draw title
        title_text = font.render("Hungry Snake's Megalomania", True, BLACK if self.bw_mode else WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
        screen.blit(title_text, title_rect)
        
        # Draw menu options
        play_text = font.render("Press p to Play", True, BLACK if self.bw_mode else WHITE)
        play_rect = play_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 30))
        screen.blit(play_text, play_rect)
        
        rules_text = font.render("Press r to View Rules", True, BLACK if self.bw_mode else WHITE)
        rules_rect = rules_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        screen.blit(rules_text, rules_rect)
        
        leaderboard_text = font.render("Press l to View Leaderboard", True, BLACK if self.bw_mode else WHITE)
        leaderboard_rect = leaderboard_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 30))
        screen.blit(leaderboard_text, leaderboard_rect)
    
    def draw_rules(self):
        # Draw title
        title_text = font.render("Game Rules", True, BLACK if self.bw_mode else WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/6))
        screen.blit(title_text, title_rect)
        
        # Draw rules
        rules = [
            "Use WASD or Arrow keys to control the snake",
            "Eat food to grow and earn points",
            "Each food is worth 10 points (20 in B&W mode)",
            "Game turns B&W at 100 points",
            "Obstacles appear at 200 points",
            "Complete the game at 300 points",
            "Game over if snake hits itself or top/bottom walls",
            "Press SHIFT to pause/resume the game"
        ]
        
        y_pos = SCREEN_HEIGHT/4
        for rule in rules:
            rule_text = font.render(rule, True, BLACK if self.bw_mode else WHITE)
            rule_rect = rule_text.get_rect(center=(SCREEN_WIDTH/2, y_pos))
            screen.blit(rule_text, rule_rect)
            y_pos += 30
        
        # Back to menu instruction
        back_text = font.render("Press 'ESC' to return to menu", True, BLACK if self.bw_mode else WHITE)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 50))
        screen.blit(back_text, back_rect)
    
    def draw_leaderboard(self):
        # Draw title with Blox BRK font
        title_text = font.render("LEADERBOARD", True, BLACK if self.bw_mode else WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/8))
        screen.blit(title_text, title_rect)
        
        if not self.scores_history:
            no_scores_text = font.render("NO SCORES YET!", True, BLACK if self.bw_mode else WHITE)
            no_scores_rect = no_scores_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/3))
            screen.blit(no_scores_text, no_scores_rect)
        else:
            # Find highest score
            highest_score = max(score['score'] for score in self.scores_history)
            
            # Draw column headers with Blox BRK font
            headers = ["PLAYER", "SCORE", "DATE & TIME"]
            header_positions = [SCREEN_WIDTH/4, SCREEN_WIDTH/2, 3*SCREEN_WIDTH/4]
            for header, x_pos in zip(headers, header_positions):
                header_text = font.render(header, True, BLACK if self.bw_mode else WHITE)
                header_rect = header_text.get_rect(center=(x_pos, SCREEN_HEIGHT/4))
                screen.blit(header_text, header_rect)
            
            # Draw scores with Blox BRK font
            y_start = SCREEN_HEIGHT/3
            for i, score_data in enumerate(sorted(self.scores_history, key=lambda x: x['score'], reverse=True)):
                if i >= 10:  # Show only top 10 scores on screen
                    break
                
                y_pos = y_start + i * 30
                
                # Highlight background if this is the highest score
                if score_data['score'] == highest_score:
                    highlight_rect = pygame.Rect(SCREEN_WIDTH/8, y_pos - 15, 3*SCREEN_WIDTH/4, 30)
                    highlight_color = (200, 200, 200) if self.bw_mode else (100, 150, 50)
                    pygame.draw.rect(screen, highlight_color, highlight_rect)
                
                # Draw username
                name_text = font.render(score_data['username'], True, BLACK if self.bw_mode else WHITE)
                name_rect = name_text.get_rect(center=(SCREEN_WIDTH/4, y_pos))
                screen.blit(name_text, name_rect)
                
                # Draw score
                score_text = font.render(str(score_data['score']), True, BLACK if self.bw_mode else WHITE)
                score_rect = score_text.get_rect(center=(SCREEN_WIDTH/2, y_pos))
                screen.blit(score_text, score_rect)
                
                # Draw date/time
                date_text = font.render(score_data['date_time'], True, BLACK if self.bw_mode else WHITE)
                date_rect = date_text.get_rect(center=(3*SCREEN_WIDTH/4, y_pos))
                screen.blit(date_text, date_rect)
        
        # Back to menu instruction with game font (Blox BRK)
        back_text = font.render("Press ESC to return to menu", True, BLACK if self.bw_mode else WHITE)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 50))
        screen.blit(back_text, back_rect)

def main():
    game = Game()
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen
    
    # Game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Handle window resize
            elif event.type == pygame.VIDEORESIZE:
                old_width, old_height = SCREEN_WIDTH, SCREEN_HEIGHT
                SCREEN_WIDTH, SCREEN_HEIGHT = event.size
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                
                # If game is in progress, scale all positions
                if game.game_started and not game.game_over and not game.game_completed:
                    game.handle_resize(SCREEN_WIDTH, SCREEN_HEIGHT)
            
            # Handle key presses
            elif event.type == pygame.KEYDOWN:
                # Handle main menu
                if game.main_menu:
                    if event.key == pygame.K_p:
                        # Go to username input
                        game.main_menu = False
                        game.input_active = True
                    elif event.key == pygame.K_r:
                        # Show rules
                        game.main_menu = False
                        game.show_rules = True
                    elif event.key == pygame.K_l:
                        # Show leaderboard
                        game.main_menu = False
                        game.show_leaderboard = True
                # Handle rules and leaderboard screens
                elif game.show_rules or game.show_leaderboard:
                    if event.key == pygame.K_ESCAPE:
                        # Return to main menu
                        game.show_rules = False
                        game.show_leaderboard = False
                        game.main_menu = True
                # Handle username input
                elif game.input_active:
                    if event.key == pygame.K_RETURN:
                        # Start game directly after username input
                        game.input_active = False
                        game.game_started = True
                    elif event.key == pygame.K_BACKSPACE:
                        # Remove last character
                        game.username = game.username[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        # Return to main menu
                        game.input_active = False
                        game.main_menu = True
                    else:
                        # Add character if it's a valid key and username isn't too long
                        if len(game.username) < game.max_username_length and event.unicode.isprintable():
                            game.username += event.unicode
                # Handle Shift key for pause/resume
                elif (event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT) and game.game_started and not game.game_over and not game.game_completed:
                    game.game_paused = not game.game_paused
                elif game.game_completed or game.game_over:
                    if event.key == pygame.K_SPACE:
                        # Save score before resetting
                        game.save_scores_history()
                        game.reset()
                        if game.game_completed:
                            game.main_menu = True  # Go back to main menu after completion
                            game.username = ""  # Clear username
                        else:
                            game.game_started = True  # Ensure game starts after reset
                    elif event.key == pygame.K_ESCAPE:
                        # Save score and return to main menu
                        game.save_scores_history()
                        game.game_over = False
                        game.main_menu = True
                        game.username = ""  # Clear username
                elif not game.game_paused:  # Only process movement keys if game is not paused
                    # WASD and Arrow keys for movement
                    if (event.key == pygame.K_UP or event.key == pygame.K_w) and game.snake.direction.y != 1:
                        game.snake.direction = Vector2(0, -1)
                    if (event.key == pygame.K_DOWN or event.key == pygame.K_s) and game.snake.direction.y != -1:
                        game.snake.direction = Vector2(0, 1)
                    if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and game.snake.direction.x != 1:
                        game.snake.direction = Vector2(-1, 0)
                    if (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and game.snake.direction.x != -1:
                        game.snake.direction = Vector2(1, 0)
        
        if not game.game_over and game.game_started and not game.game_completed and not game.game_paused:
            game.update()
        
        game.draw_elements()
        
        # Game over screen
        if game.game_over:
            # Display "GAME OVER!" on one line
            game_over_text = font.render('GAME OVER!', True, BLACK if game.bw_mode else WHITE)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 40))
            screen.blit(game_over_text, game_over_rect)
            
            # Display "Press SPACE to restart" on the line below
            restart_text = font.render('Press SPACE to restart', True, BLACK if game.bw_mode else WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 10))
            screen.blit(restart_text, restart_rect)
            
            # Display "Press ESC to quit" below restart text
            quit_text = font.render('Press ESC to quit', True, BLACK if game.bw_mode else WHITE)
            quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20))
            screen.blit(quit_text, quit_rect)
            
            # Display player score
            if game.username:
                player_score_text = font.render(f'{game.username} Scored {game.score}', True, BLACK if game.bw_mode else WHITE)
                player_score_rect = player_score_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50))
                screen.blit(player_score_text, player_score_rect)
        
        # Pause screen overlay
        if game.game_paused:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Black with 50% transparency
            screen.blit(overlay, (0, 0))
            
            # Pause text
            pause_text = font.render('PAUSED - Press SHIFT to resume', True, WHITE)
            text_rect = pause_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            screen.blit(pause_text, text_rect)
        
        pygame.display.update()
        clock.tick(game.get_game_speed())

if __name__ == "__main__":
    main() 