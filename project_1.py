import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# --- Game Constants ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
GROUND_HEIGHT = 100
PIPE_GAP = 150  # Gap between top and bottom pipes
PIPE_WIDTH = 50
PIPE_SPEED = 3
BIRD_GRAVITY = 0.5
BIRD_JUMP_STRENGTH = -8
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0) # Bird color

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flying Bird Game")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Font for score and messages
font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 30)

# --- Bird Class ---
class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([30, 30])
        self.image.fill(YELLOW) # Simple yellow square for the bird
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
        self.velocity = 0

    def jump(self):
        """Makes the bird jump upwards."""
        self.velocity = BIRD_JUMP_STRENGTH

    def update(self):
        """Updates the bird's position based on gravity."""
        self.velocity += BIRD_GRAVITY
        self.rect.y += self.velocity

        # Prevent bird from going off the top of the screen
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity = 0 # Stop upward movement if it hits the ceiling

    def draw(self, screen):
        """Draws the bird on the screen."""
        screen.blit(self.image, self.rect)

# --- Pipe Class ---
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, height):
        super().__init__()
        self.x = x
        self.height = height
        self.passed = False # To check if the bird has passed this pipe for scoring

        # Top pipe
        self.top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.height)
        # Bottom pipe
        self.bottom_rect = pygame.Rect(self.x, self.height + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - (self.height + PIPE_GAP) - GROUND_HEIGHT)

    def update(self):
        """Moves the pipe to the left."""
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, screen):
        """Draws the pipes on the screen."""
        pygame.draw.rect(screen, GREEN, self.top_rect)
        pygame.draw.rect(screen, GREEN, self.bottom_rect)

    def off_screen(self):
        """Checks if the pipe has moved off the screen."""
        return self.x + PIPE_WIDTH < 0

# --- Game Functions ---
def draw_ground(screen):
    """Draws the ground at the bottom of the screen."""
    pygame.draw.rect(screen, BROWN, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))

def display_message(message, color, y_offset=0):
    """Displays a message on the screen."""
    text_surface = font.render(message, True, color)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    screen.blit(text_surface, text_rect)

def display_score(score):
    """Displays the current score."""
    score_text = font.render(str(score), True, BLACK)
    screen.blit(score_text, (SCREEN_WIDTH - 60, 20))

def reset_game():
    """Resets all game variables for a new game."""
    bird = Bird()
    pipes = []
    score = 0
    game_over = False
    return bird, pipes, score, game_over

# --- Main Game Loop ---
def game_loop():
    bird, pipes, score, game_over = reset_game()
    running = True
    start_screen = True
    pipe_spawn_timer = 0
    pipe_spawn_interval = 90 # Frames between pipe spawns (approx 1.5 seconds at 60 FPS)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if start_screen and event.key == pygame.K_SPACE:
                    start_screen = False
                elif not game_over and event.key == pygame.K_SPACE:
                    bird.jump()
                elif game_over and event.key == pygame.K_SPACE:
                    bird, pipes, score, game_over = reset_game()
                    start_screen = False # Start playing immediately after reset

        # --- Game Logic (only when not on start screen and not game over) ---
        if not start_screen and not game_over:
            bird.update()

            # Spawn new pipes
            pipe_spawn_timer += 1
            if pipe_spawn_timer >= pipe_spawn_interval:
                pipe_height = random.randint(100, SCREEN_HEIGHT - GROUND_HEIGHT - PIPE_GAP - 100) # Ensure pipes are not too short or too tall
                pipes.append(Pipe(SCREEN_WIDTH, pipe_height))
                pipe_spawn_timer = 0

            # Update and remove pipes
            for pipe in list(pipes): # Iterate over a copy to allow modification
                pipe.update()
                if pipe.off_screen():
                    pipes.remove(pipe)

                # Check if bird passed the pipe for scoring
                if not pipe.passed and pipe.x + PIPE_WIDTH < bird.rect.x:
                    score += 1
                    pipe.passed = True

            # Collision detection
            # Bird hits ground
            if bird.rect.bottom >= SCREEN_HEIGHT - GROUND_HEIGHT:
                game_over = True
                bird.rect.bottom = SCREEN_HEIGHT - GROUND_HEIGHT # Snap to ground

            # Bird hits pipes
            for pipe in pipes:
                if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                    game_over = True

        # --- Drawing ---
        screen.fill(WHITE) # Clear screen

        for pipe in pipes:
            pipe.draw(screen)

        bird.draw(screen)
        draw_ground(screen)
        display_score(score)

        if start_screen:
            display_message("Flying Bird", BLACK, -50)
            display_message("Press SPACE to Start", BLACK, 20)
        elif game_over:
            display_message("Game Over!", BLACK, -50)
            display_message(f"Score: {score}", BLACK, 0)
            display_message("Press SPACE to Restart", BLACK, 50)

        # Update the full display surface to the screen
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()
pygame.savefile("game")