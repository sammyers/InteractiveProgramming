import pygame
from models import *
import time

square_width = 10
grid_width = 51

if __name__ == '__main__':
	pygame.init()
	size = (square_width * grid_width, square_width * grid_width)
	screen = pygame.display.set_mode(size)

	model = GameModel(grid_width)
	view = GameView(model, screen, square_width)
	controller = GameController(model)

	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			controller.handle_event(event)
		view.draw()
		time.sleep(.001)
