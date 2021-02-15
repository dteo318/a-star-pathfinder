import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Pathfinding Algorithm")

# Display colors for nodes
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.width = width
        self.x = col * width
        self.y = row * width
        self.total_rows = total_rows
        self.neighbors = []
        self.color = WHITE

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
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])
        
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
            self.neighbors.append(grid[self.row - 1][self.col])
        
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])
        
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

    def __lt__(self, other):
        return False


# Heuristic function for calculating distance between 2 points 
# using Manhatten formula
def h(point_1, point_2):
    x1, y1 = point_1
    x2, y2 = point_2

    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

# A* Algorithm
def algorithm(draw, grid, start, end):
    count = 0
    open_list = PriorityQueue()
    open_list.put((0, count, start)) # Placing start node in open list
    came_from = {}

    g_score = {node : float('inf') for row in grid for node in row}
    g_score[start] = 0

    f_score = {node : float('inf') for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_list_hash = {start}

    while not open_list.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current_node = open_list.get()[2]
        open_list_hash.remove(current_node)

        if current_node == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True # Draw path

        for neighbor in current_node.neighbors:
            temp_g_score = g_score[current_node] + 1 # g_score of neighbor to current node is 1 node away

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current_node
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())

                if neighbor not in open_list_hash:
                    count += 1 
                    open_list.put((f_score[neighbor], count, neighbor))
                    open_list_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current_node != start:
            current_node.make_closed()
        
    return False



# Creating the map/grid using a 2D-array
def make_grid(rows, width):
    grid = []
    node_width = width // rows

    for i in range(rows):
        grid.append([])

        for j in range(rows):
            # Creating node for each block of the grid/map
            node = Node(i, j, node_width, rows)
            grid[i].append(node)

    return grid

# To draw the grid lines on the pygame window
def draw_grid_lines(window, rows, width):
    node_width = width // rows

    for i in range(rows):
        pygame.draw.line(window, GREY, (0, i * node_width), (width, i * node_width))

        for j in range(rows):
            pygame.draw.line(window, GREY, (j * node_width, 0), (j* node_width, width))

# Overall draw function
def draw(window, rows, width, grid):
    window.fill(WHITE)

    # Drawing each node within our grid
    for row in grid:
        for node in row:
            node.draw(window)

    draw_grid_lines(window, rows, width)
    pygame.display.update()

# To get the row, width of the position clicked by mouse
def get_clicked_position(position, rows, width):
    node_width = width // rows
    x, y = position # The position given by the click

    # Converting position to grid coordinates
    col = x // node_width
    row = y // node_width

    return row, col

def main(window, width):
    ROWS = 50 # Can be changed to adjust grid size

    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    started = False
    while run:
        draw(window, ROWS, width, grid) # Continuously draw the window
        for event in pygame.event.get():

            # To close the window and quit program when window 'close' button is clicked
            if event.type == pygame.QUIT:
                run = False

            # To prevent changing the grid drawn when algorithm is running
            if started:
                continue

            if pygame.mouse.get_pressed()[0]: # If left button is clicked
                # Extracting grid coordinates clicked
                position = pygame.mouse.get_pos()
                row, col = get_clicked_position(position, ROWS, width)
                node = grid[row][col]
                
                if not start and node != end: # If starting node has not been placed, place starting node 
                    start = node
                    start.make_start()

                elif not end and node != start: # If ending node has not been placed, place ending node 
                    end = node
                    end.make_end()

                elif node != start and node != end: # If starting and ending nodes were not clicked, place barrier
                    node.make_barrier()
                    print(node.color)

            elif pygame.mouse.get_pressed()[2]: # If right button is clicked
                position = pygame.mouse.get_pos()
                row, col = get_clicked_position(position, ROWS, width)
                node = grid[row][col]
                node.reset()

                if node == start:
                    start = None
                if node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    algorithm(lambda: draw(window, ROWS, width, grid), grid, start, end)
                
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)


    pygame.quit()
        
main(WINDOW, WIDTH)