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
pygame.display.set_caption("Tetris Breaker v2")

# Tetris-like shapes (list of (x, y) offsets from center)
SHAPES = [
    [(0, 0), (0, -25), (0, 25), (50, 25)],  # L-shape
    [(0, 0), (0, -25), (-50, 0), (50, 0)],  # T-shape
    [(0, 0), (0, -25), (25, 0), (25, -25)]  # Square
]

class Block:
    def __init__(self, x, y):
        self.shape = random.choice(SHAPES)
        self.rects = [pygame.Rect(x + dx, y + dy, 25, 25) for dx, dy in self.shape]
        self.speed = 0.5  # Slower fall
        self.landed = False

    def update(self):
        if not self.landed:
            for rect in self.rects:
                rect.y += self.speed
            if any(rect.bottom >= SIZE[1] for rect in self.rects):
                self.landed = True

    def draw(self, screen):
        for rect in self.rects:
            pygame.draw.rect(screen, WHITE, rect)

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(350, 400, 10, 10)
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
        self.speed = 10

    def update(self):
        pos = pygame.mouse.get_pos()
        target_x = pos[0] - 50
        if abs(self.rect.centerx - target_x) > self.speed:
            self.rect.x += self.speed if target_x > self.rect.x else -self.speed
        else:
            self.rect.x = target_x
        self.rect.clamp_ip(screen.get_rect())

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)

class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.blocks = [Block(random.randint(0, 12) * 50, -50) for _ in range(3)]  # Fewer blocks
        self.ball = Ball()
        self.paddle = Paddle()
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.game_over = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def update(self):
        if self.game_over:
            return False

        self.paddle.update()
        self.ball.update()

        # Ball physics
        if self.ball.rect.left <= 0 or self.ball.rect.right >= SIZE[0]:
            self.ball.speed_x *= -1
        if self.ball.rect.top <= 0:
            self.ball.speed_y *= -1
        if self.ball.rect.colliderect(self.paddle.rect):
            self.ball.speed_y = -abs(self.ball.speed_y)
            hit_pos = (self.ball.rect.centerx - self.paddle.rect.centerx) / 50
            self.ball.speed_x = hit_pos * 3

        if self.ball.rect.top > SIZE[1]:
            self.game_over = True
            return False

        # Block updates
        for block in self.blocks[:]:
            block.update()
            if not block.landed:
                for rect in block.rects:
                    if self.ball.rect.colliderect(rect):
                        self.blocks.remove(block)
                        self.score += 10
                        self.ball.speed_y *= -1
                        break
            elif any(rect.bottom >= SIZE[1] - 50 for rect in block.rects):  # Stack limit
                self.game_over = True
                return False

        if random.random() < 0.005:  # Slower spawn
            self.blocks.append(Block(random.randint(0, 12) * 50, -50))

        return True

    def draw(self, screen):
        screen.fill(BLACK)
        for block in self.blocks:
            block.draw(screen)
        self.ball.draw(screen)
        self.paddle.draw(screen)
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        if self.game_over:
            game_over_text = self.font.render(f"Game Over! Score: {self.score}", True, WHITE)
            screen.blit(game_over_text, (SIZE[0]//2 - 100, SIZE[1]//2))

def main():
    game = Game()
    running = True
    while running:
        running = game.handle_events()
        if not game.update():
            running = False if game.game_over else True
        game.draw(screen)
        pygame.display.flip()
        game.clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()