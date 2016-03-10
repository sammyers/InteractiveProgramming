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

		# Place the appropriate rectangle for every element of the grid (None, SnakeBodyPart, Wall or Food)
		for i in range(len(self.model.grid.grid)):
			for j in range(len(self.model.grid.grid[i])):
				get_rect = pygame.Rect(*self.coord_to_pixels((i, j)))
				try: # try to get color attribute, if 
					color = self.model.grid.grid[i][j].color if not self.model.snake.dead else self.model.grid.grid[i][j].dead_color
				except:
					color = pygame.Color('black')
				pygame.draw.rect(self.screen, color, get_rect)

		self.print_score()

		# Blit the death screen if the snake is dead
		if self.model.snake.dead:
			self.print_death_text('Wasted', 64)

		pygame.display.update()	

	def coord_to_pixels(self, coords):
		"""Take a coordinate pair on the grid and convert to pygame rectangle parameters"""
		left = self.square_size * coords[0]
		top = self.square_size * coords[1]
		width, height = (self.square_size, self.square_size)
		return (left, top, width, height)

	def print_death_text(self, death_message, font_size):


		dead_font = pygame.font.Font(None, font_size)
		options_font = pygame.font.Font(None, font_size/2)
		options_color = (181, 180, 103)

		background = pygame.Surface(self.screen.get_size())
		background = background.convert()

		# Wasted
		text = dead_font.render(death_message, 1, (200, 0, 0, 1))
		textpos = text.get_rect()
		textpos.centerx = background.get_rect().centerx
		textpos.centery = background.get_rect().centerx  # centerx such that the text is at the center of the square field
		self.screen.blit(text, textpos)

		# Play Again
		replay = options_font.render("R: Play Again", 1, options_color)
		replay_pos = replay.get_rect()
		replay_pos.centerx = background.get_rect().centerx
		replay_pos.centery = background.get_rect().centerx + font_size*3/4  # centerx such that the text is at the center of the square field
		self.screen.blit(replay, replay_pos)

		# Play Again
		quit = options_font.render("Q: Quit", 1, options_color)
		quit_pos = quit.get_rect()
		quit_pos.centerx = background.get_rect().centerx
		quit_pos.centery = background.get_rect().centerx + font_size*3/4 + font_size/2  # centerx such that the text is at the center of the square field
		self.screen.blit(quit, quit_pos)


	def print_score(self):
		score_str = 'Score: ' + str(self.model.score2)

		screen_size = self.screen.get_size()
		font = pygame.font.Font(None, int(0.06*screen_size[0]))#20)  # How to pass font size?
		background = pygame.Surface( ( screen_size[0], screen_size[1]-screen_size[0] ) )
		background = background.convert()

		text = font.render(score_str, 1, (255, 255, 255, 1))
		textpos = text.get_rect()
		textpos.x = int(0.03*screen_size[0])
		textpos.centery = sum(screen_size)/2
		self.screen.blit(text, textpos)



class GameController(object):
	def __init__(self, model):
		self.model = model

	def handle_event(self, event):
		if event.type == pygame.QUIT:
			return False

		if event.type != pygame.KEYDOWN:
			return True

		if self.model.snake.dead:
			if event.key == pygame.K_q:
				# Quit
				return False
			elif event.key == pygame.K_r:
				# Restart the game.
				self.model.__init__()
				return True

		control_dict = {
						pygame.K_LEFT: 'left',
						pygame.K_RIGHT: 'right',
						pygame.K_UP: 'up',
						pygame.K_DOWN: 'down'
						}
		opposites = {
					'up': 'down',
					'down': 'up',
					'left': 'right',
					'right': 'left',
					None: None
					}

		new_direction = control_dict.get(event.key, None) # control_dict[event.key]
		if new_direction == None:
			return True
		if (new_direction != opposites[self.model.snake.direction] or self.model.snake.size() == 1):
			self.model.snake.direction = new_direction
			self.model.score2 -= 1

		return True



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
		self.score = 0
		self.score2 = 0

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
		while SnakeBodyPart(point[0], point[1]) in self.snake.get_list():
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
				self.score += 10   # Have the score based off of len(snake)?
				self.score2 += 10

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
	color = pygame.Color('green')
	dead_color = pygame.Color(78 ,78 ,78 ,255)
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
	color = pygame.Color('yellow')
	dead_color = pygame.Color(210, 210, 210, 255)

	def __init__(self, x, y):
		self.x, self.y = (x, y)

	def __repr__(self):
		return 'Food'


class Wall(object):
	color = pygame.Color('red')
	dead_color = pygame.Color(128, 128, 128, 255)	
	def __init__(self, x, y):
		self.x, self.y = (x, y)

	def __repr__(self):
		return 'Wall'
