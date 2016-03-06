import pygame
from linkedlist import Node, LinkedList
import random

class GameView(object):
	def __init__(self, model, screen, square_size=10):
		self.model = model
		self.screen = screen
		self.square_size = square_size

	def draw(self):
		self.screen.fill(pygame.Color('black'))
		for i in range(len(self.model.grid.grid)):
			for j in range(len(self.model.grid.grid[i])):
				get_rect = pygame.Rect(*self.coord_to_pixels((i, j)))
				try: # try to get color attribute, if 
					color = self.model.grid.grid[i][j].color
				except:
					color = 'black'
				pygame.draw.rect(self.screen, pygame.Color(color), get_rect)
		pygame.display.update()	

	def coord_to_pixels(self, coords):
		"""Take a coordinate pair on the grid and convert to pygame rectangle parameters"""
		left = self.square_size * coords[0]
		top = self.square_size * coords[1]
		width, height = (self.square_size, self.square_size)
		return (left, top, width, height)


class GameController(object):
	def __init__(self, model):
		self.model = model

	def handle_event(self, event):
		if event.type != pygame.KEYDOWN:
			return
		control_dict = {
						pygame.K_LEFT: 'left',
						pygame.K_RIGHT: 'right',
						pygame.K_UP: 'up',
						pygame.K_DOWN: 'down'
						}
		opposite = {
					'up': 'down',
					'down': 'up',
					'left': 'right',
					'right': 'left',
					None: None
					}
		new_direction = control_dict[event.key]
		if new_direction != opposite[self.model.snake.direction]:
			self.model.snake.direction = new_direction


class GameModel(object):
	def __init__(self, dimensions=50):
		self.grid = GameGrid(dimensions)
		self.snake = Snake(dimensions/2)
		self.grid.grid[dimensions/2][dimensions/2] = self.snake.head.data
		self.foods = []
		self.walls = []
		self.dead = False
		self.make_first_walls()
		self.make_food()

	def make_first_walls(self):
		for i in range(len(self.grid.grid)):
			first_wall = Wall(i, 0)
			last_wall = Wall(i, len(self.grid.grid[i])-1)
			self.grid.grid[i][0] = first_wall					# Make top and bottom lines 
			self.grid.grid[i][-1] = last_wall
			self.walls.extend((first_wall, last_wall))
		for j in range(1, len(self.grid.grid[0])):				# Make side walls
			first_wall = Wall(0, j)
			last_wall = Wall(len(self.grid.grid[j])-1, j)
			self.grid.grid[0][j] = first_wall
			self.grid.grid[-1][j] = last_wall
			self.walls.extend((first_wall, last_wall))

	def make_food(self):
		def random_point():
			x = random.randrange(1, len(self.grid.grid) - 1)
			y = random.randrange(1, len(self.grid.grid[x]) - 1)
			return (x, y)
		point = random_point()
		while SnakeBodyPart(*point) in self.snake.get_list():
			point = random_point()
		new_food = Food(*point)
		self.foods.append(new_food)
		self.grid.grid[point[0]][point[1]] = new_food

	def move_snake(self, to_x, to_y):
		# Delete in the grid
		for part in self.snake.get_list():
			self.grid.grid[part.x][part.y] = None
		# Move snake internally
		grow = bool(self.snake.growth_counter)
		self.snake.move(to_x, to_y, grow)
		if grow:
			self.snake.growth_counter -= 1
		# Update in grid
		for part in self.snake.get_list():
			self.grid.grid[part.x][part.y] = part

	def update_snake(self):
		if self.snake.dead:
			return
		x = self.snake.head.data.x
		y = self.snake.head.data.y
		if self.snake.direction == 'left':
			self.move_snake(x - 1, y)
		if self.snake.direction == 'right':
			self.move_snake(x + 1, y)
		if self.snake.direction == 'up':
			self.move_snake(x, y - 1)
		if self.snake.direction == 'down':
			self.move_snake(x, y + 1)

	def check_collision(self):
		"""
		Check if the Snake's head is hitting a wall or a food.
		Act on those.
		"""
		x = self.snake.head.data.x
		y = self.snake.head.data.y
	
		# Check for wall collision
		for a_wall in self.walls:
			if a_wall.x == x and a_wall.y == y:
				self.snake.die()		

		# Check for food collision
		for i, apple in enumerate(self.foods):
			if apple.x == x and apple.y == y:
				self.snake.grow()
				del self.foods[i]
				self.make_food()

		# Check for snake collisions
		for part in self.snake.get_list()[1:]:		# Don't check against the head
			if part.x == x and part.y == y:
				self.snake.die()		
	

class GameGrid(object):
	def __init__(self, dimensions):
		self.grid = []
		for i in range(dimensions):
			self.grid.append([])
			for j in range(dimensions):
				self.grid[i].append(None)
				
	def __repr__(self):
		repr_string = ''
		for i in range(len(self.grid)):
			repr_string += str(self.grid[i])
			if i != len(self.grid) - 1:
				repr_string += ('\n')
		return repr_string

class SnakeBodyPart(object):
	color = 'green'
	def __init__(self, x, y, index=0):
		self.x, self.y = (x, y)
		self.index = index

class Snake(LinkedList):
	def __init__(self, position, direction=None, growth_rate=4):
		head = Node(SnakeBodyPart(position, position))
		super(Snake, self).__init__(head)
		self.direction = direction
		self.growth_counter = 0
		self.growth_rate = growth_rate
		self.dead = False
	
	def move(self, to_x, to_y, eaten=False):
		""" Takes a tuple of position"""
		# Move internally
		new_head = SnakeBodyPart(to_x, to_y)
		self.insert(new_head)
		if not eaten:
			self.delete()

	def grow(self):
		self.growth_counter += self.growth_rate
		
	def die(self):
		self.dead = True


class Food(object):
	color = 'yellow'

	def __init__(self, x, y):
		self.x, self.y = (x, y)

	def __repr__(self):
		return 'Food'

class Wall(object):
	color = 'red'

	def __init__(self, x, y):
		self.x, self.y = (x, y)

	def __repr__(self):
		return 'Wall'

if __name__ == '__main__':
	grid = GameGrid(11)
	print grid
