import pygame
import math
from queue import PriorityQueue 

WIDTH = 1000
HEIGHT = 800
CELL_SIZE = 20

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (173, 181, 189)
RED = (255, 89, 94)
YELLOW = (255, 202, 58)
GREEN = (138, 201, 38)
BLUE = (25, 130, 196)
PURPLE = (106, 76, 147)

class Spot:
  def __init__(self, row, col, width):
    self.row = row
    self.col = col
    self.x = col * width
    self.y = row * width
    self.width = width
    self.color = WHITE
    self.neighbors = []
    self.h = math.inf
    self.g = math.inf
    self.f = math.inf
    self.came_from = None
  
  def get_pos(self):
    return self.row, self.col
  
  def get_color(self):
    return self.color
  
  def draw(self, screen):
    pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.width))
  
  def is_start(self):
    return self.color == BLUE
  
  def is_end(self):
    return self.color == PURPLE
  
  def is_wall(self):
    return self.color == BLACK

  def is_visited(self):
    return self.color == RED

  def is_open(self):
    return self.color == YELLOW

  def set_start(self):
    self.color = BLUE

  def set_end(self):
    self.color = PURPLE
  
  def set_wall(self):
    self.color = BLACK

  def set_visited(self):
    self.color = RED

  def set_open(self):
    self.color = YELLOW

  def set_path(self):
    self.color = GREEN

  def reset(self):
    self.color = WHITE

  def get_h(self):
    return self.h
  
  def get_g(self):
    return self.g
  
  def get_f(self):
    return self.f
  
  def set_h(self, val):
    self.h = val

  def set_g(self, val):
    self.g = val

  def update_f(self):
    self.f = self.h + self.g

  def get_cf(self):
    return self.came_from
  
  def set_cf(self, cf):
    self.came_from = cf

  def get_neighbors(self):
    return self.neighbors

  def update_neighbors(self, grid):
    self.neighbors = [] # First we reset the neighbors
    rows = HEIGHT // CELL_SIZE
    cols = WIDTH // CELL_SIZE

    # down neighbor = row+1, same col
    if self.row < rows - 1 and not grid[self.row + 1][self.col].is_wall():
      self.neighbors.append(grid[self.row + 1][self.col])
    
    # upper neighbor = row-1, same col
    if self.row > 0 and not grid[self.row - 1][self.col].is_wall():
      self.neighbors.append(grid[self.row - 1][self.col])

    # right neighbor = same row, col+1
    if self.col < cols - 1 and not grid[self.row][self.col + 1].is_wall():
      self.neighbors.append(grid[self.row][self.col + 1])

    # left neighbor = same row, col-1
    if self.col > 0 and not grid[self.row][self.col - 1].is_wall():
      self.neighbors.append(grid[self.row][self.col - 1])
  

def h_score(p1, p2):
  # h score is calculated as manhattan distance
  x1, y1 = p1
  x2, y2 = p2
  return abs(x1 - x2) + abs(y1 - y2)


def generate_grid(w, h, size):
  grid = []
  rows = h // size
  cols = w // size

  for i in range(rows):
    grid.append([])
    for j in range(cols):
      spot = Spot(i, j, size)
      grid[i].append(spot)

  return grid
  
def draw_grid(screen, w, h, size):
  rows = h // size
  cols = w // size
  
  for i in range(rows):
    pygame.draw.line(screen, GREY, (0, i*size), (w, i*size))
    for j in range(cols):
      pygame.draw.line(screen, GREY, (j*size, 0), (j*size, h))

def draw(screen, grid):
  for row in grid:
    for spot in row:
      spot.draw(screen)

  draw_grid(screen, WIDTH, HEIGHT, CELL_SIZE)
  pygame.display.update()

def get_click_pos(pos, size):
  x, y = pos
  row = y // size
  col = x // size
  return row, col

def astar(draw, grid, start, end):
  counter = 0
  start.set_g(0)
  start.set_h(0)
  start.update_f()

  open_set = PriorityQueue()
  open_set.put((0, counter, start))

  open_set_hash = {start}
  
  while not open_set.empty():
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()

    current = open_set.get()[2]
    # open_set_hash.remove(current)

    if current == end:
      path_spot = end.get_cf()
      while path_spot != start:
        path_spot.set_path()
        path_spot = path_spot.get_cf()
      end.set_end() # end has been overwritten
      return True
    
    for neighbor in current.get_neighbors():
      temp_g = current.get_g() + 1 # all the edges have a cost of 1
      if temp_g < neighbor.get_g():
        temp_h = h_score(neighbor.get_pos(), end.get_pos())
        neighbor.set_g(temp_g)
        neighbor.set_h(temp_h)
        neighbor.update_f()
        neighbor.set_cf(current)
      if neighbor not in open_set_hash:
        counter += 1
        open_set.put((neighbor.get_f(), counter, neighbor))
        open_set_hash.add(neighbor)
        neighbor.set_open()

    if current != start:
      current.set_visited()
    
    draw()

  return False



def main():

  # pygame setup
  pygame.init()
  screen = pygame.display.set_mode((WIDTH, HEIGHT))
  clock = pygame.time.Clock()
  
  running = True
  started = False

  start_spot = None
  end_spot = None

  grid = generate_grid(WIDTH, HEIGHT, CELL_SIZE)

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
          row, col = get_click_pos(pos, CELL_SIZE)
          spot = grid[row][col]

          if not start_spot: # first LMB -> make start
            start_spot = spot
            spot.set_start()

          elif not end_spot and not spot.is_start(): # second LMB -> make end
            end_spot = spot
            spot.set_end()

          elif not spot.is_start() and not spot.is_end() and not started: # other LMB -> make wall
            spot.set_wall()

        elif pygame.mouse.get_pressed()[2]: # right mouse button pressed
          pos = pygame.mouse.get_pos()
          row, col = get_click_pos(pos, CELL_SIZE)
          spot = grid[row][col]
          if spot.is_wall() and not started: # delete wall
            spot.reset()

        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_f and start_spot and end_spot:
            started = True
            for row in grid:
              for spot in row:
                spot.update_neighbors(grid)
            
            astar(lambda: draw(screen, grid), grid, start_spot, end_spot)

          if event.key == pygame.K_r:
            started = False
            start_spot = None
            end_spot = None
            grid = generate_grid(WIDTH, HEIGHT, CELL_SIZE)  

    draw(screen, grid)


    # flip() the display to put your work on screen
    pygame.display.flip()
    clock.tick(60)  # limits FPS to 60

  pygame.quit()


main()
