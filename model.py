import pygame
from linkedlist import Node, LinkedList
import random
import numpy as np

class GameModel(object):
	"""
	Stores all information about the current state of the game.

	Data:
		grid: 3D array containing all of the blocks in the game.
		snake: The snake itself, which stores its own direction and the positions of its component parts.
		foods: A list of the food objects currently contained in the model.
		walls: Same as above, for wall objects.
		plane: A plane object containing the state of the current slice the snake is moving in.
	"""
	def __init__(self, dimensions=50):
		self.grid = GameGrid(dimensions)
		self.snake = Snake(dimensions/2)
		self.grid.grid[dimensions/2][dimensions/2][0] = self.snake.head.data
		self.foods = []
		self.walls = []
		self.dead = False
		self.plane = Plane()
		#self.make_random_walls()
		self.make_blob_walls(6, 9)
		self.make_food()
		self.score = 0
		self.score2 = 0	

	def make_random_walls(self):
		"""Procedurally generate obstacles in 3 dimensions at the start of the game"""
		square_dimensions = len(self.grid.grid[0][0])
		num_blocks = 1000
		block_length = 200
		directions = [(1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1)]

		# Number of block walls
		for block in range(num_blocks):
			#print 'block:', block
			stagnate = 100

			# Select a random start point (that isn't a wall)
			origin = self.rand_3tuple(0, square_dimensions-1)
			x,y,z = origin

			# Make sure there is nothing there
			while self.grid.grid[x][y][z] != None:				
				origin = self.rand_3tuple(0, square_dimensions-1)

			# Sequentially choose where the next walls will be, add them to the grid and the list of walls
			block_count = block_length
			while block_length:

				one_direction = random.choice(directions)
				n_x,n_y,n_z = tuple(np.add(origin,one_direction) % square_dimensions)
				cell_content = self.grid.grid[n_x][n_y][n_z]

				for a_wall in self.walls:
					#print 'wall check'
					if a_wall == cell_content:
						origin = (a_wall.x, a_wall.y, a_wall.z) 
						block_length -= 1
						stagnate -= 1

				if cell_content == None:
					origin = (n_x,n_y,n_z)
					new_wall = Wall(n_x,n_y,n_z)
					self.walls.append(new_wall)
					self.grid.grid[n_x][n_y][n_z] = new_wall
					block_length -= 1

				if stagnate == 0:
					block_length = 0
		#print 'Number of Walls:', len(self.walls)

	def make_blob_walls(self, num_blobs, size_blobs):
		square_dimensions = len(self.grid.grid[0][0])
		# Generate a bunch of points (blob centers)
		for a_blob in range(num_blobs):
			origin = self.rand_3tuple(0, square_dimensions-1)

			# Make sure there is nothing there
			while self.grid.tuple_get(origin) != None:				
				origin = self.rand_3tuple(0, square_dimensions-1)

			# Make blobs off of those
			self.make_blob(origin, 0.6, size_blobs)

		#print len(self.walls)


	def make_blob(self, origin, proba, depth):
		square_dimensions = len(self.grid.grid[0][0])

		#print 'Recursing'

		if depth == 0:
			#print 'Stopping Condition'
			return

		directions = [(1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1)]
		for one_direction in directions:
			new_origin = tuple(np.add(origin,one_direction))

		#	print self.grid.tuple_get(new_origin) != None
		#	print self.tuple_in_range(new_origin, 0, square_dimensions-1)
		#	print random.random() < proba
		#	print


			if (self.grid.tuple_get(new_origin) == None) and self.tuple_in_range(new_origin, 0, square_dimensions-1) and (random.random() < proba):
				#print 'Making new wall'

				# Set walls in internal list of walls
				new_wall = Wall(*new_origin)
				self.walls.append(new_wall)
				# Set wall in the grid
				self.grid.tuple_set(new_origin, new_origin)
				# Recurse
				#self.make_blob(new_origin, proba*(1-1/float(depth)), depth-1)
				self.make_blob(new_origin, proba, depth-1)

	def tuple_in_range(self, your_tuple, a, b):
		"""
		Return true if each element of the tuple is within the range (a,b) inclusive
		"""
		for element in your_tuple:
			if not (a <= element and element <= b):
				return False
		return True

	def make_food(self):
		"""Generate a new food block in a random location; invoked at start of game or when the snake eats"""
		def random_point():
			x = random.randrange(1, len(self.grid.grid) - 1)
			y = random.randrange(1, len(self.grid.grid[x]) - 1)
			z = random.randrange(1, len(self.grid.grid[x][y]) - 1)
			return (x, y, z)
		point = random_point()
		while SnakeBodyPart(*point) in self.snake.get_list() or Wall(*point) in self.walls: #Retry if it overlaps with the snake or with a wall block
			point = random_point()
		new_food = Food(*point)
		self.foods.append(new_food)		#Update the model's food list
		self.grid.grid[point[0]][point[1]][point[2]] = new_food		#Update the grid
		print point

	def move_snake(self, to_x, to_y, to_z):
		"""Move the head of the snake to a given point"""
		if any(x < 0 or x > (len(self.grid.grid) - 1) for x in [to_x, to_y, to_z]):
			#Wrap the snake around the edge when it reaches a corner
			self.change_orientation(self.snake.direction)
			return
		# Delete in the grid
		for part in self.snake.get_list():
			self.grid.grid[part.x][part.y][part.z] = None
		# Move snake internally
		grow = bool(self.snake.growth_counter)		#If the snake is in the process of growing
		self.snake.move(to_x, to_y, to_z, grow)		#Pass this to the snake's internal move function
		if grow:
			self.snake.growth_counter -= 1
		# Update in grid
		for part in self.snake.get_list():
			self.grid.grid[part.x][part.y][part.z] = part

	def update_snake(self):
		"""Incrementally move the snake in whichever direction it's currently moving"""
		if self.snake.dead:
			return
		x = self.snake.head.data.x
		y = self.snake.head.data.y
		z = self.snake.head.data.z
		position = (x, y, z)
		#Use the plane's direction vectors to find the snake's next position
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
		self.move_snake(*new_position)		#Move the snake to the new position	

	def change_orientation(self, direction):
		"""Re-orient the plane by rotating the view in a given direction"""
		getattr(self.plane, 'turn_' + direction)()
		head = self.snake.head.data
		direction_vector = tuple(np.add(self.plane.up, self.plane.right))
		position_vector = (head.x, head.y, head.z)
		#Re-set the depth to the position value of the coordinate not contained in the new direction vector
		#(e.g. if in the xy plane, depth is the current z position)
		depth_index = direction_vector.index(0)
		depth = position_vector[depth_index]
		self.plane.depth = depth

	def check_collision(self):
		"""
		Check if the Snake's head is hitting anything. Act accordingly.
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
				self.score += 10   # Have the score based off of len(snake)?
				self.score2 += 10

		# Check for snake collisions
		for part in self.snake.get_list()[1:]:		# Don't check against the head
			if part.x == x and part.y == y and part.z == z:
				self.snake.die()

	def restart(self):
		"""Restart the game by re-initializing the model to default values"""
		self.__init__()

	def rand_3tuple(self, lower, higher):
		"""Return random 3-tuple (N_0, N_1, N_2) where lower <= N_x <= higher"""
		return (random.randint(lower, higher),random.randint(lower, higher) ,random.randint(lower, higher))
	

class GameGrid(object):
	"""
	Coordinate array that stores the positional data for all of the game blocks
	"""
	def __init__(self, dimensions):
		self.grid = np.array([[[None for z in range(dimensions)] for y in range(dimensions)] for x in range(dimensions)])
				
	def __repr__(self):
		repr_string = ''
		for i in range(len(self.grid)):
			repr_string += str(self.grid[i])
			if i != len(self.grid) - 1:
				repr_string += ('\n')
		return repr_string

	def tuple_get(self, xyz):
		x, y, z = xyz
		return self.grid[x][y][z]

	def tuple_set(self, xyz, value):
		x, y, z = xyz
		self.grid[x][y][z] = value
		return


class Plane(object):
	"""
	Stores information about the slice of the grid with the snake's current position. 
	Contains methods for rotating itself in all four directions.
	"""
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
	"""
	Snake component block to be stored in the grid or contained in a Snake object.
	"""
	color = pygame.Color('green')
	dead_color = pygame.Color(78, 78, 78, 255)
	background_color = pygame.Color(78, 78, 78, 100)

	def __init__(self, x, y, z):
		self.x, self.y, self.z = (x, y, z)


class Snake(LinkedList):
	"""
	Contains all of the individual snake components, as well as information about its own direction and state of growth.
	The snake's head is stored as the head of a linked list.
	"""
	def __init__(self, position, direction=None, growth_rate=4):
		head = Node(SnakeBodyPart(position, position, z=0))
		super(Snake, self).__init__(head)
		self.direction = direction
		self.growth_counter = 0
		self.growth_rate = growth_rate
		self.dead = False

	def change_direction(self, new_direction):
		"""Checks if a direction change is legal and acts on it if appropriate"""
		opposites = {'up': 'down',
					 'left': 'right',
					 'down': 'up',
					 'right': 'left',
					 None: None}
		if new_direction != opposites[self.direction] or self.size() == 1:
			self.direction = new_direction

	def move(self, to_x, to_y, to_z, eaten=False):
		"""Move the snake head to a given set of coordinates by creating a new head"""
		# Move internally
		new_head = SnakeBodyPart(to_x, to_y, to_z)
		self.insert(new_head)
		if not eaten:
			self.delete() 	#Shift the rest of the snake forward by deleting the tail.
							#If the snake has eaten, allow it to grow by just moving the head forward.

	def grow(self):
		"""Respond to the snake eating a food block by initializing an increase in length"""
		self.growth_counter += self.growth_rate
		
	def die(self):
		"""Pretty self-explanatory"""
		self.dead = True


class Food(object):
	"""A food block with its own position and color data, to be stored in the model and in the grid"""
	color = pygame.Color('yellow')
	dead_color = pygame.Color(210, 210, 210, 255)
	background_color = pygame.Color(210, 210, 210, 100)

	def __init__(self, x, y, z):
		self.x, self.y, self.z = (x, y, z)

	def __repr__(self):
		return 'Food'


class Wall(object):
	"""Wall block, used in the same manner as a food block"""
	color = pygame.Color('red')
	dead_color = pygame.Color(128, 128, 128, 255)
	background_color = pygame.Color(128, 128, 128, 100)

	def __init__(self, x, y, z):
		self.x, self.y, self.z = (x, y, z)

	def __repr__(self):
		return 'Wall'


class BackgroundObject(object):
	"""A mostly stateless object to be placed in the grid to represent an object outside of the current plane."""
	def __init__(self, block):
		"""Set this block's color based on the background color of the original block, so the view function can use it"""
		self.color = block.background_color

