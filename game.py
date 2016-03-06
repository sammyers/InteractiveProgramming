import pygame
from models import *
import time

square_width = 10 #pixels
grid_width = 51
pixels_wide = square_width * grid_width
ms_per_block = 6 # screen refreshes per move

if __name__ == '__main__':
	pygame.init()
	size = (pixels_wide, pixels_wide)
	screen = pygame.display.set_mode(size)

	model = GameModel(grid_width)
	view = GameView(model, screen, square_width)
	controller = GameController(model)

	running = True
	count = 0
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			controller.handle_event(event)
		count += 1
		if count == ms_per_block:
			model.update_snake()
			model.check_collision()
			count = 0
		view.draw()
		time.sleep(.001)
