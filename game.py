import pygame
from model import GameModel
from view import GameView
from controller import GameController
import time

square_width = 10 # pixels
grid_width = 51
pixels_wide = square_width * grid_width
ms_per_block = 2 # screen refreshes per move
score_font_size = 14

if __name__ == '__main__':
	pygame.init()
	size = (pixels_wide, int(pixels_wide*1.08) )# + score_font_size + 14)
	screen = pygame.display.set_mode(size)

	model = GameModel(grid_width)
	view = GameView(model, screen, square_width)
	controller = GameController(model)

	running = True
	count = 0
	while running:
		view.draw()
		for event in pygame.event.get():
			# if event.type == pygame.QUIT:
			# 	running = False
			running = controller.handle_event(event)
		count += 1
		if count == ms_per_block:
			model.update_snake()
			model.check_collision()
			count = 0

		time.sleep(.001)
	pygame.QUIT
