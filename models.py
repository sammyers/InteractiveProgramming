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
		if event.key == pygame.K_LEFT:
			self.model.snake.direction = 'left'
			#self.model.move_snake(x - 1, y)
		if event.key == pygame.K_RIGHT:
			self.model.snake.direction = 'right'
			#self.model.move_snake(x + 1, y)
		if event.key == pygame.K_UP:
			self.model.snake.direction = 'up'
			#self.model.move_snake(x, y - 1)
		if event.key == pygame.K_DOWN:
			self.model.snake.direction = 'down'
			#self.model.move_snake(x, y + 1)

class GameModel(object):
	def __init__(self, dimensions=50):
		self.grid = GameGrid(dimensions)
		self.snake = Snake(dimensions/2)
		self.grid.grid[dimensions/2][dimensions/2] = self.snake.head.data
		self.make_food()

	def move_snake(self, to_x, to_y):
		# Delete in the grid
		for part in self.snake.get_list():
			self.grid.grid[part.x][part.y] = None
		# Move snake internally
		self.snake.move(to_x, to_y)
		# Update in grid
		for part in self.snake.get_list():
			self.grid.grid[part.x][part.y] = part

	def make_food(self):
		x = random.randrange(len(self.grid.grid))
		y = random.randrange(len(self.grid.grid[x]))
		self.grid.grid[x][y] = Food()

	def update_snake(self):
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

class GameGrid(object):
	def __init__(self, dimensions):
		self.grid = []
		for i in range(dimensions):
			self.grid.append([])
			for j in range(dimensions):
				self.grid[i].append(None)
				if i == 0 or i == dimensions - 1 or j == 0 or j == dimensions - 1:
					self.grid[i][j] = Wall()

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
	def __init__(self, position, direction=None):
		head = Node(SnakeBodyPart(position, position))
		super(Snake, self).__init__(head)
		self.direction = direction
	
	def move(self, to_x, to_y):
		""" Takes a tuple of position"""
		# Move internally
		new_head = SnakeBodyPart(to_x, to_y)
		self.insert(new_head)
		self.delete()

class Food(object):
	color = 'yellow'

	def __repr__(self):
		return 'Food'

class Wall(object):
	color = 'red'

	def __repr__(self):
		return 'Wall'

if __name__ == '__main__':
	grid = GameGrid(11)
	print grid
