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
SIZE = (400, 600)  # Taller, narrower
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Tetris Breaker v5")

# Tetris tetrominoes (25x25 units each)
TETROMINOES = {
    'I': [(0, 0), (0, -25), (0, 25), (0, 50)],
    'O': [(0, 0), (0, -25), (25, 0), (25, -25)],
    'T': [(0, 0), (0, -25), (-25, 0), (25, 0)],
    'S': [(0, 0), (25, 0), (0, -25), (-25, -25)],
    'Z': [(0, 0), (-25, 0), (0, -25), (25, -25)],
    'J': [(0, 0), (0, -25), (0, 25), (-25, 25)],
    'L': [(0, 0), (0, -25), (0, 25), (25, 25)]
}

class Tetromino:
    def __init__(self, x, y, shape_key):
        self.shape_key = shape_key
        self.rects = [pygame.Rect(x + dx, y + dy, 25, 25) for dx, dy in TETROMINOES[shape_key]]
        self.speed = -0.5  # Fall upward
        self.settled = False

    def update(self, paddle_x):
        if not self.settled:
            # Move with paddle horizontally
            paddle_center = paddle_x + 50  # Paddle width/2
            self_center = sum(r.centerx for r in self.rects) / len(self.rects)
            dx = paddle_center - self_center
            for rect in self.rects:
                rect.x += dx
                rect.y += self.speed
            # Clamp to screen edges
            for rect in self.rects:
                rect.clamp_ip(screen.get_rect())
            # Settle at top
            if any(rect.top <= 0 for rect in self.rects):
                self.settled = True
                for rect in self.rects:
                    if rect.top < 0:
                        rect.top = 0

    def rotate(self):
        if self.settled:
            return
        # Rotate around center
        cx = sum(r.centerx for r in self.rects) / len(self.rects)
        cy = sum(r.centery for r in self.rects) / len(self.rects)
        new_rects = []
        for rect in self.rects:
            dx = rect.centerx - cx
            dy = rect.centery - cy
            new_dx = -dy  # 90-degree clockwise
            new_dy = dx
            new_rect = pygame.Rect(0, 0, 25, 25)
            new_rect.center = (cx + new_dx, cy + new_dy)
            new_rect.clamp_ip(screen.get_rect())
            new_rects.append(new_rect)
        self.rects = new_rects

    def drop(self):
        if not self.settled:
            self.settled = True
            for rect in self.rects:
                rect.top = 0

    def draw(self, screen):
        for rect in self.rects:
            pygame.draw.rect(screen, WHITE, rect)

    def hit(self, ball_rect):
        if not self.settled:
            return False
        for i, rect in enumerate(self.rects[:]):
            if ball_rect.colliderect(rect):
                del self.rects[i]
                return True
        return False

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(200, 500, 10, 10)
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
        self.rect = pygame.Rect(150, 550, 100, 10)
        self.speed = 5

    def update(self, keys, mouse_pos):
        # Mouse control
        self.rect.centerx = mouse_pos[0]
        # Key control
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        self.rect.clamp_ip(screen.get_rect())

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.clock = pygame.time.Clock()
        self.tetrominoes = [Tetromino(175, 525, random.choice(list(TETROMINOES.keys())))]
        self.ball = Ball()
        self.paddle = Paddle()
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.game_over = False
        self.bounce_sound = pygame.mixer.Sound(pygame.mixer.Sound(buffer=b'\x00\x00\x80\x00\x00\x00\x80\x00' * 10))
        self.break_sound = pygame.mixer.Sound(pygame.mixer.Sound(buffer=b'\x00\xFF\x00\x80' * 5))
        self.bounce_sound.set_volume(0.5)
        self.break_sound.set_volume(0.5)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.tetrominoes[-1].rotate()
                elif event.button == 3:  # Right click
                    self.tetrominoes[-1].drop()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.tetrominoes[-1].rotate()
        if keys[pygame.K_UP]:
            self.tetrominoes[-1].drop()
        return True

    def update(self):
        if self.game_over:
            return False

        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        self.paddle.update(keys, mouse_pos)
        self.ball.update()

        if self.ball.rect.colliderect(self.paddle.rect) and self.ball.speed_y > 0:
            self.ball.speed_y = -abs(self.ball.speed_y)
            hit_pos = (self.ball.rect.centerx - self.paddle.rect.centerx) / 50
            self.ball.speed_x = hit_pos * 3
            pygame.mixer.Sound.play(self.bounce_sound)

        if self.ball.rect.top > SIZE[1]:
            self.game_over = True
            return False

        # Update active tetromino with paddle position
        if self.tetrominoes[-1].settled:
            self.tetrominoes.append(Tetromino(175, 525, random.choice(list(TETROMINOES.keys()))))
        else:
            self.tetrominoes[-1].update(self.paddle.rect.x)

        # Ball hits settled tetrominoes
        for tet in self.tetrominoes[:-1]:  # Exclude active one
            if tet.hit(self.ball.rect):
                self.score += 10
                self.ball.speed_y *= -1
                pygame.mixer.Sound.play(self.break_sound)
                if not tet.rects:
                    self.tetrominoes.remove(tet)

        # Game over if stack too low
        if any(any(r.bottom >= 550 for r in tet.rects) for tet in self.tetrominoes[:-1]):
            self.game_over = True
            return False

        return True

    def draw(self, screen):
        screen.fill(BLACK)
        for tet in self.tetrominoes:
            tet.draw(screen)
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