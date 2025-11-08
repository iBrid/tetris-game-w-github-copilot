import pygame
import sys
import random
from tetromino import SHAPES, COLORS, rotate_shape, shape_cells, clone_shape
import constants as C

pygame.init()

WIDTH = C.GRID_WIDTH * C.CELL_SIZE + 200
HEIGHT = C.GRID_HEIGHT * C.CELL_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont('Consolas', 20)

def create_grid():
    return [[None for _ in range(C.GRID_WIDTH)] for _ in range(C.GRID_HEIGHT)]

def valid_position(grid, shape, offset_x, offset_y):
    for x, y in shape_cells(shape, offset_x, offset_y):
        if x < 0 or x >= C.GRID_WIDTH or y >= C.GRID_HEIGHT:
            return False
        if y >= 0 and grid[y][x] is not None:
            return False
    return True


def can_piece_drop_somewhere(grid, shape):
    """Return True if there exists an x position such that the shape can drop
    to a y position within the visible grid (y >= 0) without overlapping.
    """
    # try all horizontal positions within the grid
    for x in range(0, C.GRID_WIDTH):
        y = -len(shape)
        # move shape down until it no longer fits
        while valid_position(grid, shape, x, y):
            y += 1
            # safety break
            if y > C.GRID_HEIGHT:
                break
        candidate_y = y - 1
        if candidate_y >= 0 and valid_position(grid, shape, x, candidate_y):
            return True
    return False

def lock_shape(grid, shape, offset_x, offset_y, color):
    for x, y in shape_cells(shape, offset_x, offset_y):
        if 0 <= y < C.GRID_HEIGHT and 0 <= x < C.GRID_WIDTH:
            grid[y][x] = color

def clear_lines(grid):
    new_grid = [row for row in grid if any(cell is None for cell in row)]
    lines_cleared = C.GRID_HEIGHT - len(new_grid)
    while len(new_grid) < C.GRID_HEIGHT:
        new_grid.insert(0, [None]*C.GRID_WIDTH)
    return new_grid, lines_cleared

def draw_grid(surface, grid):
    # background
    surface.fill(C.BG_COLOR)
    for r in range(C.GRID_HEIGHT):
        for c in range(C.GRID_WIDTH):
            rect = pygame.Rect(c*C.CELL_SIZE, r*C.CELL_SIZE, C.CELL_SIZE, C.CELL_SIZE)
            pygame.draw.rect(surface, C.GRID_COLOR, rect, 1)
            if grid[r][c] is not None:
                pygame.draw.rect(surface, grid[r][c], rect.inflate(-2, -2))

def next_shape():
    name = random.choice(list(SHAPES.keys()))
    return name, clone_shape(name)

def main():
    def init_state():
        grid = create_grid()
        bag = []
        score = 0
        level = 1
        fall_time = 0
        fall_speed = 500  # ms
        cur_name, cur_shape = next_shape()
        cur_color = COLORS[cur_name]
        cur_x = C.GRID_WIDTH // 2 - 2
        cur_y = -2
        next_name, next_shape_mat = next_shape()
        return (grid, bag, score, level, fall_time, fall_speed,
                cur_name, cur_shape, cur_color, cur_x, cur_y,
                next_name, next_shape_mat)

    (grid, bag, score, level, fall_time, fall_speed,
     cur_name, cur_shape, cur_color, cur_x, cur_y,
     next_name, next_shape_mat) = init_state()

    game_over = False
    running = True

    def spawn_next_as_current():
        nonlocal cur_name, cur_shape, cur_color, cur_x, cur_y, next_name, next_shape_mat, game_over
        cur_name, cur_shape = next_name, next_shape_mat
        cur_color = COLORS[cur_name]
        cur_x = C.GRID_WIDTH // 2 - 2
        cur_y = -2
        next_name, next_shape_mat = next_shape()
        # if the board has blocks in the top row and the newly spawned piece is not visible, game over
        top_blocked = any(cell is not None for cell in grid[0])
        spawn_visible = any(y >= 0 for (_, y) in shape_cells(cur_shape, cur_x, cur_y))
        if top_blocked and not spawn_visible:
            game_over = True

    def reset_game():
        nonlocal grid, bag, score, level, fall_time, fall_speed
        nonlocal cur_name, cur_shape, cur_color, cur_x, cur_y
        nonlocal next_name, next_shape_mat, game_over
        (grid, bag, score, level, fall_time, fall_speed,
         cur_name, cur_shape, cur_color, cur_x, cur_y,
         next_name, next_shape_mat) = init_state()
        game_over = False

    # initial spawn visibility check
    top_blocked = any(cell is not None for cell in grid[0])
    spawn_visible = any(y >= 0 for (_, y) in shape_cells(cur_shape, cur_x, cur_y))
    if top_blocked and not spawn_visible:
        game_over = True

    while running:
        dt = clock.tick(C.FPS)
        fall_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        reset_game()
                        continue
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                        break
                    else:
                        # ignore other keys while game over
                        continue

                if event.key == pygame.K_LEFT:
                    if valid_position(grid, cur_shape, cur_x-1, cur_y):
                        cur_x -= 1
                elif event.key == pygame.K_RIGHT:
                    if valid_position(grid, cur_shape, cur_x+1, cur_y):
                        cur_x += 1
                elif event.key == pygame.K_DOWN:
                    if valid_position(grid, cur_shape, cur_x, cur_y+1):
                        cur_y += 1
                elif event.key == pygame.K_UP:
                    rotated = rotate_shape(cur_shape)
                    if valid_position(grid, rotated, cur_x, cur_y):
                        cur_shape = rotated
                elif event.key == pygame.K_SPACE:
                    # hard drop
                    while valid_position(grid, cur_shape, cur_x, cur_y+1):
                        cur_y += 1
                    lock_shape(grid, cur_shape, cur_x, cur_y, cur_color)
                    grid, lines = clear_lines(grid)
                    score += lines * 100
                    spawn_next_as_current()

        # automatic fall (only if not game over)
        if not game_over and fall_time > fall_speed:
            fall_time = 0
            if valid_position(grid, cur_shape, cur_x, cur_y+1):
                cur_y += 1
            else:
                lock_shape(grid, cur_shape, cur_x, cur_y, cur_color)
                grid, lines = clear_lines(grid)
                score += lines * 100
                spawn_next_as_current()

        draw_grid(screen, grid)

        # draw current shape
        for x, y in shape_cells(cur_shape, cur_x, cur_y):
            if y >= 0:
                rect = pygame.Rect(x*C.CELL_SIZE, y*C.CELL_SIZE, C.CELL_SIZE, C.CELL_SIZE)
                pygame.draw.rect(screen, cur_color, rect.inflate(-2, -2))

        # sidebar: score
        sidebar_x = C.GRID_WIDTH*C.CELL_SIZE + 20
        score_surf = font.render(f"Score: {score}", True, (220,220,220))
        screen.blit(score_surf, (sidebar_x, 20))

        # draw next-piece preview below score
        preview_label = font.render("Next:", True, (220,220,220))
        preview_x = sidebar_x
        preview_y = 60
        screen.blit(preview_label, (preview_x, preview_y))

        # preview grid (4x4) using smaller cells
        preview_cell = max(6, C.CELL_SIZE // 2)
        px = preview_x
        py = preview_y + 24
        # draw small border for preview
        pygame.draw.rect(screen, (60,60,70), pygame.Rect(px-4, py-4, preview_cell*4+8, preview_cell*4+8), 1)
        if 'next_shape_mat' in locals():
            for x, y in shape_cells(next_shape_mat, 0, 0):
                rect = pygame.Rect(px + x*preview_cell, py + y*preview_cell, preview_cell, preview_cell)
                pygame.draw.rect(screen, COLORS[next_name], rect.inflate(-2, -2))

        # if game over, draw overlay with restart instructions
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            screen.blit(overlay, (0,0))
            go_surf = font.render("Game Over", True, (255,80,80))
            instr_surf = font.render("Press R to restart or Esc to quit", True, (220,220,220))
            score_final = font.render(f"Final Score: {score}", True, (220,220,220))
            screen.blit(go_surf, (WIDTH//2 - go_surf.get_width()//2, HEIGHT//2 - 40))
            screen.blit(score_final, (WIDTH//2 - score_final.get_width()//2, HEIGHT//2 - 10))
            screen.blit(instr_surf, (WIDTH//2 - instr_surf.get_width()//2, HEIGHT//2 + 20))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
