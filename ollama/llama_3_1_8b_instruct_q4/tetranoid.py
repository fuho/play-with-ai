"""
Create a game using pygame, it should combine elements of Tetris and Arkanoid.
"""
import sys

import pygame
import random

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Set the width and height of the screen (width, height).
size = (700, 500)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Block Blast")

class Block:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, 7) * 50, random.randint(-150, -50), 50, 50)

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(350, 250, 10, 10)
        self.speed_x = random.choice([-1, 1]) * 2
        self.speed_y = -3

    def draw(self, screen):
        pygame.draw.ellipse(screen, WHITE, self.rect)

class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.blocks = [Block() for _ in range(50)]
        self.ball = Ball()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def update(self):
        self.ball.rect.x += self.ball.speed_x
        self.ball.rect.y += self.ball.speed_y

        # Collision with top and bottom of screen
        if self.ball.rect.top < 0 or self.ball.rect.bottom > size[1]:
            self.ball.speed_y *= -1

        # Collision with left and right of screen
        for block in self.blocks:
            if self.ball.rect.colliderect(block.rect):
                print("Ball hit block!")
                return False
            elif self.ball.rect.left < 0 or self.ball.rect.right > size[0]:
                return True

        # If ball hits the bottom, game over!
        if self.ball.rect.bottom > size[1]:
            return True

        return False

    def draw(self, screen):
        for block in self.blocks:
            block.draw(screen)
        self.ball.draw(screen)

def main():
    pygame.init()
    game = Game()

    running = True
    while running:
        game.handle_events()
        if not running:
            print("Game Over!")
            break

        # Add new blocks every 2 seconds
        if random.random() < 0.01:
            game.blocks.append(Block())

        screen.fill(BLACK)
        game.draw(screen)
        pygame.display.flip()

        game.clock.tick(60)

    # pygame.quit()

if __name__ == "__main__":
    main()
