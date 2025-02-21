"""
Create a game using pygame, it should combine elements of Tetris and Arkanoid.
"""
import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
BALL_RADIUS = 15
BRICK_WIDTH = 75
BRICK_HEIGHT = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


class Block:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = random.choice([RED, BLUE])


class Paddle:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2
        self.y = SCREEN_HEIGHT - 50
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT


class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(BALL_RADIUS, SCREEN_WIDTH - BALL_RADIUS)
        self.y = random.randint(100, 200)
        self.speed_x = random.choice([-5, 5])
        self.speed_y = 5


class Brick:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.color = RED


# Create game objects
blocks = []
paddle = Paddle()
ball = Ball()

bricks = [Brick(x * (BRICK_WIDTH + 5), y * (BRICK_HEIGHT + 5)) for x in range(10) for y in range(3)]
score = 0
game_over = False

# Initialize screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris-Arkanoid")
clock = pygame.time.Clock()


def draw_text(text, size, color, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))


def check_collision(ball, brick):
    return (ball.x + BALL_RADIUS > brick.x and
            ball.x - BALL_RADIUS < brick.x + brick.width and
            ball.y + BALL_RADIUS > brick.y and
            ball.y - BALL_RADIUS < brick.y + brick.height)


# Main game loop
running = True
while running:
    screen.fill(BLACK)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move paddle with arrow keys or WASD
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        paddle.x -= 5
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        paddle.x += 5

    # Keep paddle within screen bounds
    paddle.x = max(0, min(paddle.x, SCREEN_WIDTH - paddle.width))

    # Spawn new blocks
    if random.randint(1, 30) == 1:
        blocks.append(Block(random.randint(0, SCREEN_WIDTH - BLOCK_SIZE), 0))

    # Update blocks
    for i in reversed(range(len(blocks))):
        block = blocks[i]
        block.y += 2

        # Check if block hits paddle or another block
        if (block.x < paddle.x + paddle.width and
                block.x + BLOCK_SIZE > paddle.x and
                block.y + BLOCK_SIZE > paddle.y and
                block.y + BLOCK_SIZE < paddle.y + paddle.height):
            del blocks[i]
            continue

        # Check if block goes too high
        if block.y > SCREEN_HEIGHT:
            game_over = True

    # Update ball position
    ball.x += ball.speed_x
    ball.y += ball.speed_y

    # Ball collision with walls
    if ball.x + BALL_RADIUS >= SCREEN_WIDTH or ball.x - BALL_RADIUS <= 0:
        ball.speed_x *= -1

    # Ball collision with paddle
    if (ball.y + BALL_RADIUS > paddle.y and
            ball.x < paddle.x + paddle.width and
            ball.x > paddle.x):
        ball.speed_y = -5

    # Ball collision with bricks
    for i in reversed(range(len(bricks))):
        brick = bricks[i]
        if check_collision(ball, brick):
            del bricks[i]
            score += 10
            ball.speed_y *= -1
            break

    # Draw objects
    draw_text(f"Score: {score}", 24, WHITE, 10, 10)

    # Draw paddle
    pygame.draw.rect(screen, WHITE, (paddle.x, paddle.y, paddle.width, paddle.height))

    # Draw blocks
    for block in blocks:
        pygame.draw.rect(screen, block.color, (block.x, block.y, BLOCK_SIZE, BLOCK_SIZE))

    # Draw ball
    pygame.draw.circle(screen, WHITE, (ball.x, ball.y), BALL_RADIUS)

    # Draw bricks
    for brick in bricks:
        pygame.draw.rect(screen, brick.color, (brick.x, brick.y, brick.width, brick.height))

    # Check game over conditions
    if len(bricks) == 0 or game_over:
        draw_text("Game Over!", 48, RED, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2)
        draw_text(f"Final Score: {score}", 36, WHITE, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
