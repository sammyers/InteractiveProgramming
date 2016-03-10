import pygame
import numpy as np
from model import BackgroundObject
from helpers import vector_add, vector_multiply

class GameView(object):
    """
    Creates the player's view of the game state. Slices the 3D grid appropriately depending on the state of the model.
    """
    def __init__(self, model, screen, square_size=10):
        self.model = model
        self.screen = screen
        self.square_size = square_size #Width/height in pixels of individual squares

    def get_slice(self):
        """Return a 2-dimensional array for the plane that the snake is currently moving in"""
        def map_origin(depth):
            """Return the location of the bottom-left corner of the plane, adjusted for orientation"""
            map_dict = {-1: len(cube) - 1, 1: 0, 0: depth}
            mapped = [map_dict[value] for value in direction_vector]
            return tuple(mapped)

        #Orientation vectors from the perspective of the player
        up_vector = np.array(self.model.plane.up)
        right_vector = np.array(self.model.plane.right)
        direction_vector = np.add(up_vector, right_vector)

        slice_depth = self.model.plane.depth
        cube = self.model.grid.grid
        grid = [[None for y in range(len(cube))] for x in range(len(cube))]     #Initialize empty 2D grid

        background_slices = [depth for depth in range(len(cube)) if depth != slice_depth] #All slice indices except the foreground
        for depth in background_slices:
            print 'slice' + str(depth)
            origin = map_origin(depth)      #Starting point (lower-right corner) for a given slice
            for i in range(len(cube)):
                for j in range(len(cube)):
                    #Move from the origin, in a direction determined by relative up and right
                    position = np.add(origin, np.add(np.multiply(i, right_vector), np.multiply(j, up_vector)))
                    x, y, z = (position[0], position[1], position[2])
                    if cube[x][y][z] is not None:
                        grid[i][j] = BackgroundObject(cube[x][y][z])    #Overlay background block onto the grid
        slice_origin = map_origin(slice_depth)
        #Overlay foreground blocks
        for i in range(len(cube)):
            for j in range(len(cube)):
                position = np.add(slice_origin, np.add(np.multiply(i, right_vector), np.multiply(j, up_vector)))
                x, y, z = (position[0], position[1], position[2])
                if cube[x][y][z] is not None:
                    grid[i][j] = cube[x][y][z]
        return grid

    def draw(self):
        """Print the current grid slice to the screen"""
        plane = self.get_slice()
        self.screen.fill(pygame.Color('black'))

        # Place the appropriate rectangle for every element of the grid (None, SnakeBodyPart, Wall or Food) 
        for i in range(len(plane)):
            for j in range(len(plane[i])):
                get_rect = pygame.Rect(*self.coord_to_pixels((i, j)))
                try: #Try to get color attribute
                    color = plane[i][j].color if not self.model.snake.dead else plane[i][j].dead_color
                except: #If the block is empty
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

