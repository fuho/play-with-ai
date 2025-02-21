"""
Create a game using pygame, it should combine elements of Tetris and Arkanoid.
"""
import pygame
import random

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Screen setup
SIZE = (700, 500)
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Tetris Breaker")

# Classes
class Block:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 25)
        self.speed = 1  # Falling speed

    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(350, 400, 10, 10)  # Start above paddle
        self.speed_x = random.choice([-2, 2])
        self.speed_y = -3

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

    def draw(self, screen):
        pygame.draw.ellipse(screen, RED, self.rect)

class Paddle:
    def __init__(self):
        self.rect = pygame.Rect(300, 450, 100, 10)

    def update(self):
        pos = pygame.mouse.get_pos()
        self.rect.x = pos[0] - 50  # Center paddle on mouse
        self.rect.clamp_ip(screen.get_rect())  # Keep paddle on screen

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)

class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.blocks = [Block(random.randint(0, 13) * 50, -25) for _ in range(5)]  # Start with 5 blocks
        self.ball = Ball()
        self.paddle = Paddle()
        self.score = 0
        self.font = pygame.font.Font(None, 36)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def update(self):
        # Update paddle
        self.paddle.update()

        # Update ball
        self.ball.update()
        # Bounce off walls
        if self.ball.rect.left <= 0 or self.ball.rect.right >= SIZE[0]:
            self.ball.speed_x *= -1
        if self.ball.rect.top <= 0:
            self.ball.speed_y *= -1
        # Bounce off paddle
        if self.ball.rect.colliderect(self.paddle.rect):
            self.ball.speed_y = -abs(self.ball.speed_y)  # Ensure upward bounce
            # Adjust angle based on hit position
            hit_pos = (self.ball.rect.centerx - self.paddle.rect.centerx) / 50
            self.ball.speed_x = hit_pos * 3

        # Ball falls off bottom
        if self.ball.rect.top > SIZE[1]:
            return False

        # Update blocks
        for block in self.blocks[:]:
            block.update()
            # Ball hits block
            if self.ball.rect.colliderect(block.rect):
                self.blocks.remove(block)
                self.score += 10
                self.ball.speed_y *= -1
                break
            # Block hits bottom
            if block.rect.top > SIZE[1]:
                return False

        # Spawn new blocks
        if random.random() < 0.02:  # ~1 block every 50 frames
            self.blocks.append(Block(random.randint(0, 13) * 50, -25))

        return True

    def draw(self, screen):
        screen.fill(BLACK)
        for block in self.blocks:
            block.draw(screen)
        self.ball.draw(screen)
        self.paddle.draw(screen)
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

def main():
    game = Game()
    running = True
    while running:
        running = game.handle_events()
        if not game.update():
            print(f"Game Over! Final Score: {game.score}")
            running = False
        game.draw(screen)
        pygame.display.flip()
        game.clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()