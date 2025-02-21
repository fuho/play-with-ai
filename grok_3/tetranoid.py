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
pygame.display.set_caption("Tetris Breaker v4")

# Tetris-like shapes
SHAPES = [
    [(0, 0), (0, -25), (0, 25), (50, 25)],  # L-shape
    [(0, 0), (0, -25), (-50, 0), (50, 0)],  # T-shape
    [(0, 0), (0, -25), (25, 0), (25, -25)]  # Square
]

class Block:
    def __init__(self, x, y):
        self.shape = random.choice(SHAPES)
        self.rects = [pygame.Rect(x + dx, y + dy, 25, 25) for dx, dy in self.shape]
        self.speed = 0.5
        self.landed = False

    def update(self):
        if not self.landed:
            for rect in self.rects:
                rect.y += self.speed
            if any(rect.bottom >= SIZE[1] for rect in self.rects):
                self.landed = True
                for rect in self.rects:
                    if rect.bottom > SIZE[1]:
                        rect.bottom = SIZE[1]

    def draw(self, screen):
        for rect in self.rects:
            pygame.draw.rect(screen, WHITE, rect)

    def hit(self, ball_rect):
        for i, rect in enumerate(self.rects[:]):
            if ball_rect.colliderect(rect):
                del self.rects[i]
                # Bump remaining rects up
                for r in self.rects:
                    r.y -= 10
                return True
        return False

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(350, 400, 10, 10)
        self.speed_x = random.choice([-2, 2])
        self.speed_y = -3

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.left <= 0:
            self.rect.left = 0
            self.speed_x *= -1
        elif self.rect.right >= SIZE[0]:
            self.rect.right = SIZE[0]
            self.speed_x *= -1
        if self.rect.top <= 0:
            self.rect.top = 0
            self.speed_y = abs(self.speed_y)

    def draw(self, screen):
        pygame.draw.ellipse(screen, RED, self.rect)

class Paddle:
    def __init__(self):
        self.rect = pygame.Rect(300, 450, 100, 10)

    def update(self):
        pos = pygame.mouse.get_pos()
        self.rect.centerx = pos[0]
        self.rect.clamp_ip(screen.get_rect())

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.clock = pygame.time.Clock()
        self.blocks = [Block(random.randint(0, 12) * 50, 0) for _ in range(3)]  # Start at y=0
        self.ball = Ball()
        self.paddle = Paddle()
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.game_over = False
        # Sounds
        self.bounce_sound = pygame.mixer.Sound(pygame.mixer.Sound(buffer=b'\x00\x00\x80\x00\x00\x00\x80\x00' * 10))  # Simple beep
        self.break_sound = pygame.mixer.Sound(pygame.mixer.Sound(buffer=b'\x00\xFF\x00\x80' * 5))  # Shorter zap
        self.bounce_sound.set_volume(0.5)
        self.break_sound.set_volume(0.5)

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

        if self.ball.rect.colliderect(self.paddle.rect) and self.ball.speed_y > 0:
            self.ball.speed_y = -abs(self.ball.speed_y)
            hit_pos = (self.ball.rect.centerx - self.paddle.rect.centerx) / 50
            self.ball.speed_x = hit_pos * 3
            pygame.mixer.Sound.play(self.bounce_sound)

        if self.ball.rect.top > SIZE[1]:
            self.game_over = True
            return False

        for block in self.blocks[:]:
            block.update()
            if not block.landed:
                if block.hit(self.ball.rect):
                    self.score += 10
                    self.ball.speed_y *= -1
                    pygame.mixer.Sound.play(self.break_sound)
                    if not block.rects:  # Remove if all rects gone
                        self.blocks.remove(block)
            elif any(rect.bottom >= SIZE[1] - 50 for rect in block.rects):
                self.game_over = True
                return False

        if random.random() < 0.005:  # Spawn 2 blocks
            for _ in range(2):
                self.blocks.append(Block(random.randint(0, 12) * 50, 0))

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