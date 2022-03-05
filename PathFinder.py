import pygame
import pickle
from queue import PriorityQueue

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == PURPLE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.row > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


class Visualization:

    def __init__(self):
        self.width = 800
        self.rows = 32
        self.grid = []
        self.bool_finding = False
        self.start = None
        self.end = None
        self.reconstructed_path = None
        self.finding_finished = False
        self.win = pygame.display.set_mode((self.width, self.width))
        pygame.display.set_caption("A* Path Finding Algorithm")

    def h(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        return abs(x1 - x2) + abs(y1 - y2)

    def reconstruct_path(self, came_from, current, draw):
        self.reconstructed_path = [current.get_pos()]
        while current in came_from:
            current = came_from[current]
            current.make_path()
            self.reconstructed_path.append(current.get_pos())
            draw()

        self.reconstructed_path.reverse()

        return self.reconstructed_path

    def algorithm(self, draw, grid, start, end):
        count = 0
        open_set = PriorityQueue()
        open_set.put((0, count, start))
        came_from = {}
        g_score = {spot: float("inf") for row in grid for spot in row}
        g_score[start] = 0
        f_score = {spot: float("inf") for row in grid for spot in row}
        f_score[start] = self.h(start.get_pos(), end.get_pos())

        open_set_hash = {start}

        while not open_set.empty():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            current = open_set.get()[2]
            open_set_hash.remove(current)

            if current == end:
                self.reconstruct_path(came_from, end, draw)
                end.make_end()
                return True

            for neighbor in current.neighbors:
                temp_g_score = g_score[current] + 1

                if temp_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    f_score[neighbor] = temp_g_score + self.h(neighbor.get_pos(), end.get_pos())
                    if neighbor not in open_set_hash:
                        count += 1
                        open_set.put((f_score[neighbor], count, neighbor))
                        open_set_hash.add(neighbor)
                        neighbor.make_open()

            draw()

            if current != start:
                current.make_closed()

        return False

    def make_grid(self, rows, width):
        grid = []
        gap = width // rows
        for i in range(rows):
            grid.append([])
            for j in range(rows):
                spot = Spot(i, j, gap, rows)
                grid[i].append(spot)

        return grid

    def draw_grid(self, win, rows, width):
        gap = width // rows
        for i in range(rows):
            pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
            for j in range(rows):
                pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

    def draw(self, win, grid, rows, width):
        win.fill(WHITE)

        for row in grid:
            for spot in row:
                spot.draw(win)

        self.draw_grid(win, rows, width)
        pygame.display.update()

    def hget_clicked_pos(self, pos, rows, width):
        gap = width // rows
        y, x = pos

        row = y // gap
        col = x // gap

        return row, col

    def write_grid(self, grid, file):
        grid_colors = []
        for index, row in enumerate(grid):
            grid_colors.append([])
            for spot in row:
                grid_colors[index].append(spot.color)

        with open(file, "wb") as filehandle:
            pickle.dump(grid_colors, filehandle)

    def read_grid(self, file):
        with open(file, "rb") as filehandle:
            grid = pickle.load(filehandle)
        for row in grid:
            print(row)

    def load_grid(self, rows, width, file):
        gap = width // rows
        new_grid = []
        with open(file, "rb") as filehandle:
            grid = pickle.load(filehandle)

        for index, row in enumerate(grid):
            new_grid.append([])
            for index2, spot in enumerate(row):

                if spot == WHITE:
                    spot = Spot(index, index2, gap, rows)
                    spot.reset()

                if spot == BLACK:
                    spot = Spot(index, index2, gap, rows)
                    spot.make_barrier()

                #            if spot == ORANGE:
                #                spot = Spot(index, index2, gap, rows)
                #                spot.make_start()

                #            if spot == RED:
                #                spot = Spot(index, index2, gap, rows)
                #                spot.make_closed()

                #            if spot == GREEN:
                #                spot = Spot(index, index2, gap, rows)
                #                spot.make_open()

                #            if spot == TURQUOISE:
                #                spot = Spot(index, index2, gap, rows)
                #                spot.make_end()

                #            if spot == PURPLE:
                #                spot = Spot(index, index2, gap, rows)
                #                spot.make_path()

                else:
                    spot = Spot(index, index2, gap, rows)
                    spot.reset()

                new_grid[index].append(spot)

        return new_grid

    def add_start(self, x, y):
        spot = self.grid[x][y]
        if spot.is_barrier():
            return 0
        else:
            self.start = spot
            spot.make_start()
            return 1

    def add_end(self, x, y):
        spot = self.grid[x][y]
        if spot.is_barrier():
            return 0
        else:
            self.end = spot
            spot.make_end()
            return 1

    def clear_path_and_load(self, file):
        self.start = None
        self.end = None
        self.reconstructed_path = None
        self.finding_finished = False
        self.grid = self.load_grid(self.rows, self.width, file)

    def start_finding(self):
        if not self.finding_finished:
            self.bool_finding = True

        return self.finding_finished

    def get_path(self):
        return self.reconstructed_path

    def main(self, load, file):
        win = self.win
        width = self.width

        self.start = None
        self.end = None

        run = True

        if load:
            self.grid = self.load_grid(self.rows, width, file)

        else:
            self.grid = self.make_grid(self.rows, width)

        while run:
            self.draw(win, self.grid, self.rows, width)

            if self.bool_finding and self.start and self.end:
                self.finding_finished = False
                for row in self.grid:
                    for spot in row:
                        spot.update_neighbors(self.grid)

                self.algorithm(lambda: self.draw(win, self.grid, self.rows, width), self.grid, self.start, self.end)
                self.bool_finding = False
                self.finding_finished = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if pygame.mouse.get_pressed()[0]:  # LEFT
                    pos = pygame.mouse.get_pos()
                    row, col = self.hget_clicked_pos(pos, self.rows, width)
                    spot = self.grid[row][col]
                    if not self.start and spot != self.end:
                        self.start = spot
                        self.start.make_start()

                    elif not self.end and spot != self.start:
                        self.end = spot
                        self.end.make_end()

                    elif spot != self.end and spot != self.start:
                        spot.make_barrier()

                elif pygame.mouse.get_pressed()[2]:  # RIGHT
                    pos = pygame.mouse.get_pos()
                    row, col = self.hget_clicked_pos(pos, self.rows, width)
                    spot = self.grid[row][col]
                    spot.reset()
                    if spot == self.start:
                        self.start = None

                    elif spot == self.end:
                        self.end = None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.start and self.end:
                        for row in self.grid:
                            for spot in row:
                                spot.update_neighbors(self.grid)

                        self.algorithm(lambda: self.draw(win, self.grid, self.rows, width), self.grid, self.start, self.end)

                    if event.key == pygame.K_c and not load:
                        self.start = None
                        self.end = None
                        self.grid = self.make_grid(self.rows, width)

                    if event.key == pygame.K_c and load:
                        self.start = None
                        self.end = None
                        self.grid = self.load_grid(self.rows, width, file)

        pygame.quit()
        return
