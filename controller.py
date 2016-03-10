import pygame
import numpy as np

class GameController(object):
    """
    Manipulates the model according to user input.

    Actions:
        * Change direction of the snake
        * Change orientation of the axes
        * Quit or restart game after death
    """
    def __init__(self, model):
        self.model = model

    def handle_event(self, event):
        """Respond to key presses, return boolean for whether to continue running the program"""
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
                self.model.restart()
                return True

        old_direction = self.model.snake.direction

        directions = ['up', 'left', 'down', 'right']

        direction_keys = [pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT]
        control_dict = {key: value for key, value in zip(direction_keys, directions)}

        orientation_keys = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]
        orient_dict = {key: value for key, value in zip(orientation_keys, directions)}

        if event.key in direction_keys: #Change direction of the snake, decrease score by 1
            self.model.snake.change_direction(control_dict[event.key])
            if old_direction is not None and old_direction != self.model.snake.direction:
                self.model.score2 -= 1

        if event.key in orientation_keys: #Change orientation of the model, decrease score by 1
            self.model.change_orientation(orient_dict[event.key])
            if old_direction is not None:
                self.model.score2 -= 1
        return True

