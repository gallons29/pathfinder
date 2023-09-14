import pygame
import math
from queue import PriorityQueue 

WIDTH = 1000
HEIGHT = 800
CELL_SIZE = 20

DEFAULT = (255, 255, 255) # White
WALL = (0, 0, 0) # Black
GREY = (173, 181, 189) 
CLOSED = (255, 89, 94) # Red
OPEN = (255, 202, 58) # Yellow
PATH = (138, 201, 38) # Green
START = (25, 130, 196) # Blue
END = (106, 76, 147) # Purple

class Cell:
  def __init__(self, row, col):
    self.row = row
    self.col = col
    self.color = DEFAULT
    self.g = math.inf
    self.h = math.inf
    self.f = math.inf
    self.came_from = None

  def get_pos(self):
    return self.row, self.col

  def get_color(self):
    return self.color
  
  def set(self, color):
    self.color = color
  
  def get_h(self):
    return self.h
  
  def get_g(self):
    return self.g
  
  def get_f(self):
    return self.f
  
  def set_h(self, val):
    self.h = val
    self.update_f()

  def set_g(self, val):
    self.g = val
    self.update_f()

  def update_f(self):
    self.f = self.h + self.g

  def get_cf(self):
    return self.came_from
  
  def set_cf(self, cf):
    self.came_from = cf

def h_score(p1, p2):
  # h score is calculated as manhattan distance
  x1, y1 = p1
  x2, y2 = p2
  return abs(x1 - x2) + abs(y1 - y2)

def generate_grid():
  grid = []
  rows = HEIGHT // CELL_SIZE
  cols = WIDTH // CELL_SIZE

  for i in range(rows):
    grid.append([])
    for j in range(cols):
      cell = Cell(i, j)
      grid[i].append(cell)

  return grid

def draw_grid(screen):
  rows = HEIGHT // CELL_SIZE
  cols = WIDTH // CELL_SIZE
  
  for i in range(rows):
    pygame.draw.line(screen, GREY, (0, i*CELL_SIZE), (WIDTH, i*CELL_SIZE))
    for j in range(cols):
      pygame.draw.line(screen, GREY, (j*CELL_SIZE, 0), (j*CELL_SIZE, HEIGHT))

def draw(screen, grid):
  for i, row in enumerate(grid):
    for j, cell in enumerate(row):
      x, y = j * CELL_SIZE, i * CELL_SIZE
      pygame.draw.rect(screen, cell.get_color(), (x, y, CELL_SIZE, CELL_SIZE))

  draw_grid(screen)
  pygame.display.update()

def get_click_pos(pos):
  x, y = pos
  row = y // CELL_SIZE
  col = x // CELL_SIZE
  return row, col

def get_neighbors(grid, cell):
  neighbors = []
  row, col = cell.get_pos()
  rows = HEIGHT // CELL_SIZE
  cols = WIDTH // CELL_SIZE

  # down neighbor = row+1, same col
  if row < rows - 1 and grid[row + 1][col].get_color() != WALL:
    neighbors.append(grid[row + 1][col])
  # upper neighbor = row-1, same col
  if row > 0 and  grid[row - 1][col].get_color() != WALL:
    neighbors.append(grid[row - 1][col])
  # right neighbor = same row, col+1
  if col < cols - 1 and grid[row][col + 1].get_color() != WALL:
    neighbors.append(grid[row][col + 1])
  # left neighbor = same row, col-1
  if col > 0 and grid[row][col - 1].get_color() != WALL:
    neighbors.append(grid[row][col - 1])

  return neighbors


def astar(draw, grid, start, end):
  counter = 0
  start.set_g(0)
  start.set_h(0)

  open_set = PriorityQueue()
  open_set.put((0, counter, start))

  open_set_hash = {start} # Keep track of closed cells
  
  while not open_set.empty():
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()

    current = open_set.get()[2]

    if current == end:
      path_cell = end.get_cf()
      while path_cell != start:
        path_cell.set(PATH)
        path_cell = path_cell.get_cf()
      end.set(END) # end has been overwritten
      return True
    
    for neighbor in get_neighbors(grid, current):
      temp_g = current.get_g() + 1 # all the edges have a cost of 1
      if temp_g < neighbor.get_g():
        temp_h = h_score(neighbor.get_pos(), end.get_pos())
        neighbor.set_g(temp_g)
        neighbor.set_h(temp_h)
        neighbor.set_cf(current)
      if neighbor not in open_set_hash:
        counter += 1
        open_set.put((neighbor.get_f(), counter, neighbor))
        open_set_hash.add(neighbor)
        neighbor.set(OPEN)

    if current != start:
      current.set(CLOSED)
    
    draw()

  return False



def main():

  # pygame setup
  pygame.init()
  screen = pygame.display.set_mode((WIDTH, HEIGHT))
  clock = pygame.time.Clock()
  
  running = True
  started = False

  start = None
  end = None

  grid = generate_grid()

  while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        '''
        Keybinds:
          First LMB: set start
          Second LMB: set end
          Third+ LMB: set wall
          RMB: delete wall
          F: start the path finder
          R: reset the board
        '''
        if pygame.mouse.get_pressed()[0]: # left mouse button pressed
          pos = pygame.mouse.get_pos()
          row, col = get_click_pos(pos)
          cell = grid[row][col]

          if not start: # first LMB -> make start
            start = cell
            start.set(START)

          elif not end and cell.get_color() != START: # second LMB -> make end
            end = cell
            cell.set(END)

          elif cell.get_color() != START and cell.get_color() != END and not started: # other LMB -> make wall
            cell.set(WALL)

        elif pygame.mouse.get_pressed()[2]: # right mouse button pressed
          pos = pygame.mouse.get_pos()
          row, col = get_click_pos(pos)
          cell = grid[row][col]
          if cell.get_color() == WALL and not started: # delete wall
            cell.set(DEFAULT)

        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_f and start and end:
            started = True
            astar(lambda: draw(screen, grid), grid, start, end)

          if event.key == pygame.K_r:
            started = False
            start = None
            end = None
            grid = generate_grid()  

    draw(screen, grid)


    # flip() the display to put your work on screen
    pygame.display.flip()
    clock.tick(60)  # limits FPS to 60

  pygame.quit()


main()
