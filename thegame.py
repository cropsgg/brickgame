import pygame
import random

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker")
FPS = 60
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Paddle settings
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 10
paddle = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - 40, PADDLE_WIDTH, PADDLE_HEIGHT)

# Ball settings
BALL_RADIUS = 10
ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_RADIUS * 2, BALL_RADIUS * 2)
ball_dx = 5 * random.choice((-1, 1))
ball_dy = -5

# Brick settings
BRICK_WIDTH, BRICK_HEIGHT = 80, 30
BRICK_COLS = WIDTH // BRICK_WIDTH

# Sound effects (optional, replace with your paths)
try:
    paddle_sound = pygame.mixer.Sound("paddle_hit.wav")
    brick_sound = pygame.mixer.Sound("brick_hit.wav")
    game_over_sound = pygame.mixer.Sound("game_over.wav")
except FileNotFoundError:
    print("Sound files not found. Running without sound.")
    paddle_sound = brick_sound = game_over_sound = None

# Level definitions
LEVELS = [
    {"rows": 3, "hits": [1, 2, 3]},  # Level 1
    {"rows": 4, "hits": [1, 1, 2, 3]},  # Level 2
    {"rows": 5, "hits": [1, 2, 2, 3, 3]}  # Level 3
]

# Game variables
current_level = 0
lives = 3
score = 0
game_over = False
game_won = False
bricks = []

def load_level(level_idx):
    global bricks
    bricks.clear()
    level = LEVELS[level_idx]
    for row in range(level["rows"]):
        for col in range(BRICK_COLS):
            hits = level["hits"][row]
            brick = pygame.Rect(col * BRICK_WIDTH, row * BRICK_HEIGHT + 50, BRICK_WIDTH - 2, BRICK_HEIGHT - 2)
            bricks.append({"rect": brick, "hits": hits, "max_hits": hits})  # Store max_hits for scoring

# Load initial level
load_level(current_level)

# Font setup
font = pygame.font.SysFont(None, 36)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEMOTION and not game_over and not game_won:
            paddle.centerx = event.pos[0]
            paddle.clamp_ip(screen.get_rect())

    if not game_over and not game_won:
        # Move ball
        ball.x += ball_dx
        ball.y += ball_dy

        # Ball collision with walls
        if ball.left <= 0 or ball.right >= WIDTH:
            ball_dx *= -1
        if ball.top <= 0:
            ball_dy *= -1
        if ball.bottom >= HEIGHT:
            lives -= 1
            ball.center = (WIDTH // 2, HEIGHT // 2)
            ball_dx = 5 * random.choice((-1, 1))
            ball_dy = -5
            if lives <= 0:
                game_over = True
                if game_over_sound:
                    game_over_sound.play()

        # Ball collision with paddle
        if ball.colliderect(paddle):
            ball_dy *= -1
            offset = (ball.centerx - paddle.centerx) / (PADDLE_WIDTH / 2)
            ball_dx = min(max(ball_dx + offset * 2, -8), 8)  # Cap ball speed
            if paddle_sound:
                paddle_sound.play()
            score += 10

        # Ball collision with bricks
        for brick in bricks[:]:
            if ball.colliderect(brick["rect"]):
                brick["hits"] -= 1
                if brick_sound:
                    brick_sound.play()
                if brick["hits"] <= 0:
                    score += 50 * brick["max_hits"]  # Use max_hits for consistent scoring
                    bricks.remove(brick)
                ball_dy *= -1
                break

        # Check level completion
        if not bricks:
            current_level += 1
            if current_level >= len(LEVELS):
                game_won = True
            else:
                load_level(current_level)
                ball.center = (WIDTH // 2, HEIGHT // 2)
                ball_dx = 5 * random.choice((-1, 1))
                ball_dy = -5

    # Drawing
    screen.fill(BLACK)
    pygame.draw.rect(screen, GREEN, paddle)
    pygame.draw.circle(screen, WHITE, ball.center, BALL_RADIUS)

    # Draw bricks with color based on hits
    for brick in bricks:
        if brick["hits"] == 3:
            color = RED
        elif brick["hits"] == 2:
            color = BLUE
        else:
            color = GREEN
        pygame.draw.rect(screen, color, brick["rect"])

    # HUD
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {current_level + 1}", True, YELLOW)
    screen.blit(lives_text, (10, 10))
    screen.blit(score_text, (10, 40))
    screen.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))

    # Game over or win message
    if game_over:
        text = font.render("Game Over! Press Q to quit or R to restart", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
        if pygame.key.get_pressed()[pygame.K_r]:
            lives, score, current_level = 3, 0, 0
            game_over = False
            load_level(current_level)
            ball.center = (WIDTH // 2, HEIGHT // 2)
            ball_dx = 5 * random.choice((-1, 1))
            ball_dy = -5
    elif game_won:
        text = font.render(f"You Win! Score: {score} Press Q to quit or R to restart", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
        if pygame.key.get_pressed()[pygame.K_r]:
            lives, score, current_level = 3, 0, 0
            game_won = False
            load_level(current_level)
            ball.center = (WIDTH // 2, HEIGHT // 2)
            ball_dx = 5 * random.choice((-1, 1))
            ball_dy = -5

    if pygame.key.get_pressed()[pygame.K_q]:
        running = False

    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()