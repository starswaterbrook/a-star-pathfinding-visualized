from queue import PriorityQueue
import pygame

WIDTH = HEIGHT = 800
ROWS = COLS = 40

WHITE = (255,255,255)
BLACK = (0,0,0)
BLUE = (98, 159, 255)
LIGHT_BLUE = (148, 190, 255)
ORANGE = (255, 165, 0)
PURPLE = (221,160,221)
GREEN = (91, 255, 68)
GREY = (192,192,192)

class Square:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.width = width
        self.x = col * width
        self.y = row * width
        self.color = WHITE
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col
    def is_closed(self):
        return self.color == BLUE
    def is_open(self):
        return self.color == LIGHT_BLUE
    def is_barrier(self):
        return self.color == BLACK
    def is_start(self):
        return self.color == ORANGE
    def is_end(self):
        return self.color == PURPLE

    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = BLUE
    def make_open(self):
        self.color = LIGHT_BLUE
    def make_barrier(self):
        self.color = BLACK
    def make_end(self):
        self.color = PURPLE
    def make_start(self):
        self.color = ORANGE
    def make_path(self):
        self.color = GREEN
    
    def draw(self, scr):
        pygame.draw.rect(scr, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbours(self, grid):
        self.neighbours = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
            self.neighbours.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
            self.neighbours.append(grid[self.row - 1][self.col])
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
            self.neighbours.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
            self.neighbours.append(grid[self.row][self.col - 1])

        # WOULD REQUIRE EUCLIDIAN DISTANCE CALCULATION AND SQUARE SCORE TABLE (MAYBE LATER?)

        #if (self.col > 0 and self.row > 0) and not grid[self.row - 1][self.col - 1].is_barrier(): # TOP LEFT
        #    self.neighbours.append(grid[self.row-1][self.col - 1])
        #if (self.col < self.total_rows - 1 and self.row < self.total_rows - 1) and not grid[self.row+1][self.col + 1].is_barrier(): # BOTTOM RIGHT
        #    self.neighbours.append(grid[self.row + 1][self.col + 1])
        #if (self.col > self.total_rows - 1 and self.row > 0) and not grid[self.row-1][self.col+1].is_barrier(): # TOP RIGHT
        #    self.neighbours.append(grid[self.row-1][self.col+1])
        #if (self.col > 0 and self.row < self.total_rows - 1) and not grid[self.row+1][self.col-1].is_barrier(): # BOTTOM LEFT
        #    self.neighbours.append(grid[self.row+1][self.col-1])

    def __lt__(self, other):
        return False

def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def make_grid():
    grid = []
    gap = WIDTH // ROWS
    for x in range(ROWS):
        grid.append([])
        for y in range(COLS):
            square = Square(x, y, gap, ROWS)
            grid[x].append(square)

    return grid

def draw_grid(scr):
    gap = WIDTH // ROWS
    for x in range(ROWS):
        pygame.draw.line(scr, GREY, (0,x*gap), (WIDTH, x*gap))
    for y in range(ROWS):
        pygame.draw.line(scr, GREY, (y*gap,0), (y*gap,WIDTH))

def draw(scr, grid):
    scr.fill(WHITE)
    for row in grid:
        for sqr in row:
            sqr.draw(scr)
    draw_grid(scr)
    pygame.display.update()

def get_clicked_pos(pos):
    gap = WIDTH // ROWS
    x,y = pos
    row = y // gap
    col = x // gap
    return row, col

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        if current.color != ORANGE:
            current.make_path()
        draw()

def a_star(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {sqr: float("inf") for row in grid for sqr in row}
    g_score[start] = 0
    f_score = {sqr: float("inf") for row in grid for sqr in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)
        
        if current == end: #PATH FOUND
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbour in current.neighbours:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + h(neighbour.get_pos(), end.get_pos())
                if neighbour not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.make_open()
        draw()
        if current != start:
            current.make_closed()
    return False

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.flip()


def main(scr):
    grid = make_grid()

    Start = None
    End = None

    running = True
    started = False

    while running:
        draw(screen, grid)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if started:
                continue
            if pygame.mouse.get_pressed()[0]: #LPM
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos)
                square = grid[row][col]
                if not Start:
                    Start = square
                    Start.make_start()
                elif not End and square != Start:
                    End = square
                    End.make_end()
                elif square != End and square != Start:
                    square.make_barrier()
            if pygame.mouse.get_pressed()[2]: #RPM
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos)
                square = grid[row][col]
                if square == Start:
                    Start = None
                if square == End:
                    End = None
                square.reset()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for x in grid:
                        for sqr in x:
                            sqr.update_neighbours(grid)
                    a_star(lambda: draw(screen, grid), grid, Start, End)
                if event.key == pygame.K_r:
                    Start = None
                    End = None
                    grid = make_grid()
    pygame.quit()


main(screen)