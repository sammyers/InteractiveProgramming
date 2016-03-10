import pygame
from linkedlist import Node, LinkedList
import random
import numpy as np

class GameView(object):
	def __init__(self, model, screen, square_size=10):
		self.model = model
		self.screen = screen
		self.square_size = square_size	

	def get_slice(self):
		
		def map_origin():
			map_dict = {-1: len(cube) - 1, 1: 0, 0: depth}
			mapped = [map_dict[value] for value in direction_vector]
			return tuple(mapped)
		
		up_vector = self.model.plane.up
		right_vector = self.model.plane.right
		direction_vector = np.add(up_vector, right_vector)
		depth = self.model.plane.depth
		cube = self.model.grid.grid
		origin = map_origin()

		grid = []
		for i in range(len(cube)):
			row = []
			for j in range(len(cube)):
				position = np.add(origin, np.add(np.multiply(i, right_vector), np.multiply(j, up_vector)))
				x, y, z = (position[0], position[1], position[2])
				row.append(cube[x][y][z])
			grid.append(row)
		return grid
		#xy = (1, 1, 0)
		#yz = (0, 1, 1)
		#xz = (1, 0, 1)
		#if tuple(np.abs(np.add(up, right))) == xy:
		#	z = self.model.plane.depth
		#	newgrid = [[y[z] for y in x] for x in cube]
		#if tuple(np.abs(np.add(up, right))) == xz:
		#	y = self.model.plane.depth
		#	newgrid = [[z for z in x[y]] for x in cube]
		#if tuple(np.abs(np.add(up, right))) == yz:
		#	x = self.model.plane.depth
		#	newgrid = [[z for z in y] for y in cube[x]]
		#return newgrid


	def draw(self):
		plane = self.get_slice()
		self.screen.fill(pygame.Color('black'))
		for i in range(len(plane)):
			for j in range(len(plane[i])):
				get_rect = pygame.Rect(*self.coord_to_pixels((i, j)))
				try: # try to get color attribute, if 
					color = plane[i][j].color
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

		directions = ['up', 'left', 'down', 'right']

		direction_keys = [pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT]
		control_dict = {key: value for key, value in zip(direction_keys, directions)}

		orientation_keys = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]
		orient_dict = {key: value for key, value in zip(orientation_keys, directions)}

		if event.key in direction_keys:
			self.model.snake.change_direction(control_dict[event.key])
		if event.key in orientation_keys:
			self.model.change_orientation(orient_dict[event.key])


class GameModel(object):
	def __init__(self, dimensions=50):
		self.grid = GameGrid(dimensions)
		self.snake = Snake(dimensions/2)
		self.grid.grid[dimensions/2][dimensions/2][0] = self.snake.head.data
		self.foods = []
		self.walls = []
		self.dead = False
		self.plane = Plane()
		#self.make_first_walls()
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
			z = 0 #random.randrange(1, len(self.grid.grid[x][y]) - 1)
			return (x, y, z)
		point = random_point()
		while SnakeBodyPart(*point) in self.snake.get_list():
			point = random_point()
		new_food = Food(*point)
		self.foods.append(new_food)
		self.grid.grid[point[0]][point[1]][point[2]] = new_food

	def move_snake(self, to_x, to_y, to_z):
		# Delete in the grid
		for part in self.snake.get_list():
			self.grid.grid[part.x][part.y][part.z] = None
		# Move snake internally
		grow = bool(self.snake.growth_counter)
		self.snake.move(to_x, to_y, to_z, grow)
		if grow:
			self.snake.growth_counter -= 1
		# Update in grid
		for part in self.snake.get_list():
			self.grid.grid[part.x][part.y][part.z] = part

	def update_snake(self):
		if self.snake.dead:
			return
		x = self.snake.head.data.x
		y = self.snake.head.data.y
		z = self.snake.head.data.z
		position = (x, y, z)
		if self.snake.direction == 'up':
			new_position = tuple(np.subtract(position, self.plane.up))
		elif self.snake.direction == 'left':
			new_position = tuple(np.subtract(position, self.plane.right))
		elif self.snake.direction == 'down':
			new_position = tuple(np.add(position, self.plane.up))
		elif self.snake.direction == 'right':
			new_position = tuple(np.add(position, self.plane.right))
		else:
			new_position = position
		self.move_snake(*new_position)
		print new_position

	def change_orientation(self, direction):
		getattr(self.plane, 'turn_' + direction)() # re-orient the plane accordingly
		head = self.snake.head.data
		position = (head.x, head.y, head.z)
		depth_vector = np.multiply((1, 1, 1) - abs(np.add(self.plane.up, self.plane.right)), position)
		self.plane.depth = [x for x in depth_vector if x != 0][0]

	def check_collision(self):
		"""
		Check if the Snake's head is hitting a wall or a food.
		Act on those.
		"""
		x = self.snake.head.data.x
		y = self.snake.head.data.y
		z = self.snake.head.data.z
	
		# Check for wall collision
		for a_wall in self.walls:
			if a_wall.x == x and a_wall.y == y:
				self.snake.die()		

		# Check for food collision
		for i, apple in enumerate(self.foods):
			if apple.x == x and apple.y == y and apple.z == z:
				self.snake.grow()
				del self.foods[i]
				self.make_food()

		# Check for snake collisions
		for part in self.snake.get_list()[1:]:		# Don't check against the head
			if part.x == x and part.y == y and part.z == z:
				self.snake.die()
	

class GameGrid(object):
	def __init__(self, dimensions):
		self.grid = []
		for i in range(dimensions):
			self.grid.append([])
			for j in range(dimensions):
				self.grid[i].append([])
				for k in range(dimensions):
					self.grid[i][j].append(None)
				
	def __repr__(self):
		repr_string = ''
		for i in range(len(self.grid)):
			repr_string += str(self.grid[i])
			if i != len(self.grid) - 1:
				repr_string += ('\n')
		return repr_string


class Plane(object):
	def __init__(self):
		self.up = (0, -1, 0) 	#default 'up' direction is -y
		self.right = (1, 0, 0)  #default 'right' direction is +x
		self.depth = 0

	def turn_up(self):
		self.up = tuple(np.cross(self.up, self.right))

	def turn_right(self):
		self.right = tuple(np.cross(self.up, self.right))

	def turn_down(self):
		self.up = tuple(np.cross(self.right, self.up))

	def turn_left(self):
		self.right = tuple(np.cross(self.right, self.up))


class SnakeBodyPart(object):
	color = 'green'
	def __init__(self, x, y, z, index=0):
		self.x, self.y, self.z = (x, y, z)
		self.index = index


class Snake(LinkedList):
	def __init__(self, position, direction=None, growth_rate=4):
		head = Node(SnakeBodyPart(position, position, z=0))
		super(Snake, self).__init__(head)
		self.direction = direction
		self.growth_counter = 0
		self.growth_rate = growth_rate
		self.dead = False

	def change_direction(self, new_direction):	
		opposites = {'up': 'down',
					 'left': 'right',
					 'down': 'up',
					 'right': 'left',
					 None: None}
		if new_direction != opposites[self.direction] or self.size() == 1:
			self.direction = new_direction

	def move(self, to_x, to_y, to_z, eaten=False):
		""" Takes a tuple of position"""
		# Move internally
		new_head = SnakeBodyPart(to_x, to_y, to_z)
		self.insert(new_head)
		if not eaten:
			self.delete()

	def grow(self):
		self.growth_counter += self.growth_rate
		
	def die(self):
		self.dead = True


class Food(object):
	color = 'yellow'

	def __init__(self, x, y, z):
		self.x, self.y, self.z = (x, y, z)

	def __repr__(self):
		return 'Food'


class Wall(object):
	color = 'red'

	def __init__(self, x, y, z):
		self.x, self.y, self.z = (x, y, z)

	def __repr__(self):
		return 'Wall'

