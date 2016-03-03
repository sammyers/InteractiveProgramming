import pygame

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
			x = self.model.snake.parts[0].x
			y = self.model.snake.parts[0].y
			self.model.move_snake(x - 1, y)
		if event.key == pygame.K_RIGHT:
			x = self.model.snake.parts[0].x
			y = self.model.snake.parts[0].y
			self.model.move_snake(x + 1, y)
		if event.key == pygame.K_UP:
			x = self.model.snake.parts[0].x
			y = self.model.snake.parts[0].y
			self.model.move_snake(x, y - 1)
		if event.key == pygame.K_DOWN:
			x = self.model.snake.parts[0].x
			y = self.model.snake.parts[0].y
			self.model.move_snake(x, y + 1)

class GameModel(object):
	def __init__(self, dimensions=50):
		self.grid = GameGrid(dimensions)
		self.snake = Snake(dimensions/2)
		self.grid.grid[dimensions/2][dimensions/2] = self.snake

	def move_snake(self, to_x, to_y):
		# Delete in the grid
		self.grid.grid[self.snake.parts[0].x][self.snake.parts[0].y] = None   # Be careful in the future when implementing more snake per snake
		self.snake.move(to_x, to_y)
		# Update in grid
		self.grid.grid[to_x][to_y] = self.snake.parts[0]

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

	def update(self, snake):
		for part in snake.parts:
			x = part.x
			y = part.y
			self.grid[x][y] = part

class SnakeBodyPart(object):
	color = 'green'
	def __init__(self, x, y):
		self.x, self.y = (x, y)

class Snake(object):
	def __init__(self, position):
		self.parts = [SnakeBodyPart(position, position)]
	
	def move(self, to_x, to_y):
		""" Takes a tuple of position"""
		# Move internally
		self.parts[0].x = to_x
		self.parts[0].y = to_y

class Food(object):
	pass

class Wall(object):
	color = 'red'

	def __repr__(self):
		return 'Wall'

if __name__ == '__main__':
	grid = GameGrid(11)
	print grid
