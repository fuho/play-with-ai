"""
Create a game using pygame, it should combine elements of Tetris and Arkanoid.
"""
import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 600
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Blockanoid Tris")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
gray = (200, 200, 200)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)
yellow = (255, 255, 0)
cyan = (0, 255, 255)
magenta = (255, 0, 255)
orange = (255, 165, 0)
tetris_colors = [gray, cyan, yellow, green, red, blue, orange, magenta] # Include gray for background blocks


# Paddle properties
paddle_width = 100
paddle_height = 15
paddle_x = (screen_width - paddle_width) // 2
paddle_y = screen_height - 50
paddle_speed = 10

# Ball properties
ball_radius = 10
ball_x = screen_width // 2
ball_y = screen_height // 2
ball_speed_x = 5 * random.choice([-1, 1])
ball_speed_y = -5

# Brick properties (for Arkanoid part - initially Tetris blocks will act as bricks)
brick_width = 60
brick_height = 20
brick_rows = 5
brick_cols = screen_width // brick_width
bricks = [] # Initially bricks will be Tetris blocks


# Tetris block properties
block_size = brick_width # Use brick width for tetris block size
grid_width = 10 # Tetris grid width in blocks
grid_height = 20 # Tetris grid height in blocks
grid = [[0] * grid_width for _ in range(grid_height)] # 0 means empty, 1-7 represent different tetris colors/types
tetromino_shapes = [
    [[1, 1, 1, 1]],  # I
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1], [1, 1]],      # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 1, 1], [0, 1, 0]]   # T
]

current_tetromino = None
current_tetromino_pos = None
current_tetromino_rotation = 0
next_tetromino = None

def spawn_tetromino():
    global current_tetromino, current_tetromino_pos, current_tetromino_rotation, next_tetromino
    if next_tetromino is None:
        tetromino_type = random.randint(1, len(tetromino_shapes)) # 1 to 7, 0 is reserved for empty grid
    else:
        tetromino_type = next_tetromino
    next_tetromino = random.randint(1, len(tetromino_shapes))
    current_tetromino = tetromino_shapes[tetromino_type-1]
    current_tetromino_pos = [0, grid_width // 2 - len(current_tetromino[0]) // 2] # Start at top center
    current_tetromino_rotation = 0
    return tetromino_type, next_tetromino

def rotate_tetromino(tetromino):
    rotated_tetromino = [[0] * len(tetromino) for _ in range(len(tetromino[0]))]
    for y in range(len(tetromino)):
        for x in range(len(tetromino[0])):
            rotated_tetromino[x][len(tetromino) - 1 - y] = tetromino[y][x]
    return rotated_tetromino

def is_valid_position(tetromino, pos, rotation):
    rotated_tetromino = tetromino
    for _ in range(rotation):
        rotated_tetromino = rotate_tetromino(rotated_tetromino)

    for y in range(len(rotated_tetromino)):
        for x in range(len(rotated_tetromino[0])):
            if rotated_tetromino[y][x]:
                block_x = pos[1] + x
                block_y = pos[0] + y

                if block_x < 0 or block_x >= grid_width or block_y >= grid_height:
                    return False # Out of bounds
                if block_y >= 0 and grid[block_y][block_x] != 0: # Check grid only if y is not negative (above screen)
                    return False # Collision with existing block
    return True


def place_tetromino_on_grid(tetromino, pos, rotation, tetromino_type):
    rotated_tetromino = tetromino
    for _ in range(rotation):
        rotated_tetromino = rotate_tetromino(rotated_tetromino)
    for y in range(len(rotated_tetromino)):
        for x in range(len(rotated_tetromino[0])):
            if rotated_tetromino[y][x]:
                grid[pos[0] + y][pos[1] + x] = tetromino_type # Place block on grid with its color index

def clear_lines():
    lines_cleared = 0
    y = grid_height - 1
    while y >= 0:
        if all(grid[y]): # If row is full
            lines_cleared += 1
            del grid[y] # Remove the full row
            grid.insert(0, [0] * grid_width) # Insert new empty row at the top
        else:
            y -= 1
    return lines_cleared


# Game variables
game_over = False
score = 0
clock = pygame.time.Clock()
fall_speed = 60 # Frames per block fall
fall_counter = 0
level = 1
lines_to_level_up = 10
lines_cleared_total = 0

current_tetromino_type, next_tetromino_type = spawn_tetromino()


# --- Game functions ---
def game_intro():
    intro_text = ["Blockanoid Tris",
                  "A Pygame Mashup",
                  "Use LEFT/RIGHT to move paddle",
                  "UP to rotate Tetromino",
                  "DOWN to speed up fall",
                  "SPACE to start",
                  "Press SPACE to play!"]
    font = pygame.font.Font(None, 40)
    text_y_offset = 100
    screen.fill(black)
    for line in intro_text:
        text_surface = font.render(line, True, white)
        text_rect = text_surface.get_rect(center=(screen_width // 2, text_y_offset))
        screen.blit(text_surface, text_rect)
        text_y_offset += 50
    pygame.display.flip()

    waiting_for_start = True
    while waiting_for_start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting_for_start = False
                    return True # Game starts
    return False # Intro interrupted

def game_over_screen():
    game_over_text = ["Game Over!",
                     f"Score: {score}",
                     "Press SPACE to play again",
                     "Press ESC to quit"]
    font = pygame.font.Font(None, 50)
    text_y_offset = screen_height // 3
    screen.fill(black)
    for line in game_over_text:
        text_surface = font.render(line, True, white)
        text_rect = text_surface.get_rect(center=(screen_width // 2, text_y_offset))
        screen.blit(text_surface, text_rect)
        text_y_offset += 60
    pygame.display.flip()

    waiting_for_restart = True
    while waiting_for_restart:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True # Restart game
                if event.key == pygame.K_ESCAPE:
                    return False # Quit game
    return False # Should not reach here


def reset_game():
    global game_over, score, grid, ball_x, ball_y, ball_speed_x, ball_speed_y, paddle_x, bricks, fall_counter, level, lines_to_level_up, lines_cleared_total, current_tetromino_type, next_tetromino_type, current_tetromino, current_tetromino_pos, current_tetromino_rotation, next_tetromino

    game_over = False
    score = 0
    level = 1
    lines_to_level_up = 10
    lines_cleared_total = 0
    fall_speed = 60

    grid = [[0] * grid_width for _ in range(grid_height)]
    ball_x = screen_width // 2
    ball_y = screen_height // 2
    ball_speed_x = 5 * random.choice([-1, 1])
    ball_speed_y = -5
    paddle_x = (screen_width - paddle_width) // 2
    bricks = [] # Tetris blocks will act as bricks

    current_tetromino = None
    current_tetromino_pos = None
    current_tetromino_rotation = 0
    next_tetromino = None
    current_tetromino_type, next_tetromino_type = spawn_tetromino()


# --- Game loop ---

show_intro = True
running = True
while running:

    if show_intro:
        if game_intro():
            show_intro = False
            reset_game()
        else:
            running = False
            continue # Skip game loop if intro cancelled


    if game_over:
        if game_over_screen():
            reset_game()
            game_over = False # Reset game_over flag to start new game directly
        else:
            running = False
            continue # Skip game loop if game over screen cancelled


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                paddle_x -= paddle_speed
            if event.key == pygame.K_RIGHT:
                paddle_x += paddle_speed
            if event.key == pygame.K_UP:
                if current_tetromino:
                    test_rotation = (current_tetromino_rotation + 1) % 4
                    if is_valid_position(current_tetromino, current_tetromino_pos, test_rotation):
                        current_tetromino_rotation = test_rotation
            if event.key == pygame.K_DOWN:
                fall_counter = fall_speed # Speed up falling


    # Paddle movement boundaries
    if paddle_x < 0:
        paddle_x = 0
    if paddle_x > screen_width - paddle_width:
        paddle_x = screen_width - paddle_width

    # Ball movement
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # Ball collisions with walls
    if ball_x - ball_radius < 0 or ball_x + ball_radius > screen_width:
        ball_speed_x *= -1
    if ball_y - ball_radius < 0:
        ball_speed_y *= -1

    # Ball collision with paddle
    if ball_y + ball_radius > paddle_y and ball_y - ball_radius < paddle_y + paddle_height:
        if ball_x > paddle_x and ball_x < paddle_x + paddle_width:
            ball_speed_y *= -1
            ball_y = paddle_y - ball_radius # Prevent ball from going inside paddle


    # Tetromino falling logic
    fall_counter += 1
    if current_tetromino:
        if fall_counter >= fall_speed:
            fall_counter = 0
            test_pos = [current_tetromino_pos[0] + 1, current_tetromino_pos[1]]
            if is_valid_position(current_tetromino, test_pos, current_tetromino_rotation):
                current_tetromino_pos[0] += 1
            else: # Hit bottom or other blocks
                place_tetromino_on_grid(current_tetromino, current_tetromino_pos, current_tetromino_rotation, current_tetromino_type)
                lines = clear_lines()
                score += lines * lines * 100 * level # Score based on lines cleared and level
                lines_cleared_total += lines
                if lines_cleared_total >= lines_to_level_up:
                    level += 1
                    lines_to_level_up += 10 # Increase lines needed to level up
                    fall_speed = max(1, fall_speed - 5) # Increase fall speed, but not below 1
                current_tetromino_type, next_tetromino_type = spawn_tetromino()
                if not is_valid_position(current_tetromino, current_tetromino_pos, current_tetromino_rotation): # Game over check
                    game_over = True


    # Ball collision with Tetris blocks (grid)
    grid_y_block = (ball_y - ball_radius) // block_size
    grid_x_block = (ball_x - ball_radius) // block_size

    if 0 <= grid_y_block < grid_height and 0 <= grid_x_block < grid_width:
        if grid[grid_y_block][grid_x_block] != 0: # Hit a block
            grid[grid_y_block][grid_x_block] = 0 # Remove the block
            ball_speed_y *= -1 # Bounce back
            score += 10 # Score for breaking block


    # Game Over condition (ball misses paddle)
    if ball_y + ball_radius > screen_height:
        game_over = True


    # --- Drawing ---
    screen.fill(black)

    # Draw grid blocks
    for y in range(grid_height):
        for x in range(grid_width):
            if grid[y][x] != 0:
                pygame.draw.rect(screen, tetris_colors[grid[y][x]], (x * block_size, y * block_size, block_size, block_size), 0)
                pygame.draw.rect(screen, gray, (x * block_size, y * block_size, block_size, block_size), 1) # Grid lines


    # Draw falling tetromino
    if current_tetromino:
        rotated_tetromino = current_tetromino
        for _ in range(current_tetromino_rotation):
            rotated_tetromino = rotate_tetromino(rotated_tetromino)
        for y in range(len(rotated_tetromino)):
            for x in range(len(rotated_tetromino[0])):
                if rotated_tetromino[y][x]:
                    block_draw_x = (current_tetromino_pos[1] + x) * block_size
                    block_draw_y = (current_tetromino_pos[0] + y) * block_size
                    if block_draw_y >= 0: # Only draw if it's on screen
                        pygame.draw.rect(screen, tetris_colors[current_tetromino_type], (block_draw_x, block_draw_y, block_size, block_size), 0)
                        pygame.draw.rect(screen, gray, (block_draw_x, block_draw_y, block_size, block_size), 1) # Grid lines


    # Draw paddle
    pygame.draw.rect(screen, white, (paddle_x, paddle_y, paddle_width, paddle_height))

    # Draw ball
    pygame.draw.circle(screen, white, (int(ball_x), int(ball_y)), ball_radius)

    # Display score and level
    font = pygame.font.Font(None, 30)
    score_text = font.render(f"Score: {score}", True, white)
    level_text = font.render(f"Level: {level}", True, white)
    next_tetromino_label = font.render("Next:", True, white)

    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 40))
    screen.blit(next_tetromino_label, (screen_width - 100, 10))


    # Draw next tetromino preview
    if next_tetromino_type is not None:
        next_shape = tetromino_shapes[next_tetromino_type-1]
        start_x = screen_width - 90
        start_y = 40
        for y in range(len(next_shape)):
            for x in range(len(next_shape[0])):
                if next_shape[y][x]:
                    pygame.draw.rect(screen, tetris_colors[next_tetromino_type], (start_x + x * block_size * 0.5, start_y + y * block_size * 0.5, block_size * 0.5, block_size * 0.5), 0)
                    pygame.draw.rect(screen, gray, (start_x + x * block_size * 0.5, start_y + y * block_size * 0.5, block_size * 0.5, block_size * 0.5), 1) # Grid lines


    pygame.display.flip()
    clock.tick(60)

pygame.quit()