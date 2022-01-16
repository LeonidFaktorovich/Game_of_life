import pygame
from pygame.locals import *


class GameOfLife:

    def __init__(self, width=640, height=480, button_height=40, button_width=80, cell_size=10, speed=10):
        # create width of window
        self.width = width
        # create height of window
        self.height = height
        # create size of cells
        self.cell_size = cell_size
        # size of window
        self.screen_size = (width, height + button_height)
        # create a window
        self.screen = pygame.display.set_mode(self.screen_size)
        # width of cell
        self.cell_width = self.width // self.cell_size
        # height of cell
        self.cell_height = self.height // self.cell_size
        # speed of game
        self.speed = speed
        # matrix of entities which will be live in cells
        self.matrix_entities = []
        # width of button
        self.button_width = button_width
        # height of button
        self.button_height = button_height
        # create a button
        self.button1 = Button(position=(self.width // 2, self.height + self.cell_size),
                              size=(self.button_width, self.button_height),
                              clr=[220, 220, 220], cngclr=(255, 0, 0),
                              func=self.button_pressed_1,
                              text='Start')
        # button status shows stage of the game, if status == 0 then the game hasn't started yet, if status == 1 then
        # the game is in progress, if status == 2 then the game is on pause
        self.button1_status = 0

    def button_pressed_1(self):
        # if the game hasn't started or the game is on pause then starting the game
        if self.button1_status == 0 or self.button1_status == 2:
            self.button1 = Button(position=(self.width // 2, self.height + self.cell_size),
                                  size=(self.button_width, self.button_height),
                                  clr=[220, 220, 220], cngclr=(255, 0, 0),
                                  func=self.button_pressed_1,
                                  text='Pause')
            self.button1_status = 1
        # else we stopping the game
        else:
            self.button1 = Button(position=(self.width // 2, self.height + self.cell_size),
                                  size=(self.button_width, self.button_height),
                                  clr=[220, 220, 220], cngclr=(255, 0, 0),
                                  func=self.button_pressed_1,
                                  text='Continue')
            self.button1_status = 2

    # draw lines on display
    def draw_lines(self):
        for x in range(0, self.width, self.cell_size):
            # draw lines
            pygame.draw.line(self.screen, pygame.Color('black'),
                             (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color('black'),
                             (0, y), (self.width, y))

    # run the game
    def run(self):
        # create a clock to determine the time after which to update the entities
        clock = pygame.time.Clock()
        # setting the name and color of the window
        pygame.display.set_caption('Game of Life')
        self.screen.fill(pygame.Color('white'))
        # create entities
        self.create_entities()
        running = True
        # draw lines
        self.draw_lines()
        while running:
            # processing events
            for event in pygame.event.get():
                # if the cross was pressed, we quit the game
                if event.type == QUIT:
                    running = False
                # if the left mouse button was pressed, then look where you clicked
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # find the coordinates where you clicked
                        pos = pygame.mouse.get_pos()
                        # if the button was pressed, it changes the state of the game
                        if self.button1.rect.collidepoint(pos):
                            self.button1.call_back()
                        # if the entity was clicked and the game did not continue,
                        # then we change the state of the entity
                        elif self.button1_status != 1 and pos[0] < self.width and pos[1] < self.height:
                            row = pos[1] // self.cell_size + 1
                            col = pos[0] // self.cell_size + 1
                            self.update_entity(row, col)
                            self.draw_entities()
            # updating the button
            self.button1.draw(self.screen)
            # if the game continues, then we update the entities
            if self.button1_status == 1:
                self.update_entities()
                self.draw_entities()
            pygame.display.flip()
            clock.tick(self.speed)

        pygame.quit()

    # creating entities
    def create_entities(self):
        self.matrix_entities = [[None] * (self.cell_width + 2) for _ in range(self.cell_height + 2)]
        for row in range(self.cell_height + 2):
            for col in range(self.cell_width + 2):
                self.matrix_entities[row][col] = Entity((col - 1) * self.cell_size, (row - 1) * self.cell_size, 0)

    # updating one entity if clicked on
    def update_entity(self, row, col):
        if self.matrix_entities[row][col].last_alive == 0:
            self.matrix_entities[row][col].last_alive = 1
            self.matrix_entities[row][col].color = pygame.Color('blue')
        else:
            self.matrix_entities[row][col].last_alive = 0
            self.matrix_entities[row][col].color = pygame.Color('white')

    # updating the number of neighbors of each entity
    def new_neighbors(self):
        for row in range(1, self.cell_height + 1):
            for col in range(1, self.cell_width + 1):
                counter_neighbors = 0
                for cur_row in [row - 1, row, row + 1]:
                    for cur_col in [col - 1, col, col + 1]:
                        counter_neighbors += self.matrix_entities[cur_row][cur_col].last_alive
                counter_neighbors -= self.matrix_entities[row][col].last_alive
                self.matrix_entities[row][col].update_neighbors(counter_neighbors)

    # updating the status of each entity by counting the number of neighbors
    def update_entities(self):
        self.new_neighbors()
        for row in range(1, self.cell_height + 1):
            for col in range(1, self.cell_width + 1):
                self.matrix_entities[row][col].counting_status()
                self.matrix_entities[row][col].change_alive()

    # draw entities
    def draw_entities(self):
        for row in range(1, self.cell_height + 1):
            for col in range(1, self.cell_width + 1):
                color = self.matrix_entities[row][col].color
                x = self.matrix_entities[row][col].x
                y = self.matrix_entities[row][col].y
                pygame.draw.rect(self.screen, color, (x + 1, y + 1, self.cell_size - 1, self.cell_size - 1))


class Entity:
    # we set the coordinates of each entity, as well as its state
    def __init__(self, x, y, alive):
        self.x = x
        self.y = y
        # by last_alive we mean the state that is displayed in the window
        self.last_alive = alive
        # the state that will be after the update
        self.current_alive = 0
        if alive == 1:
            self.color = pygame.Color('blue')
        else:
            self.color = pygame.Color('white')
        self.neighbors = 0

    # update number of neighbors
    def update_neighbors(self, new_neighbors):
        self.neighbors = new_neighbors

    # based on the number of neighbors, we conclude what will happen to the cell
    def counting_status(self):
        if self.neighbors == 3:
            self.current_alive = 1
        elif self.last_alive == 1 and self.neighbors == 2:
            self.current_alive = 1
        else:
            self.current_alive = 0

    # changing the status of each entity
    def change_alive(self):
        self.last_alive = self.current_alive
        if self.last_alive == 1:
            self.color = pygame.Color('blue')
        else:
            self.color = pygame.Color('white')
        self.current_alive = 0


class Button:
    def __init__(self, position, size, clr=[100, 100, 100], cngclr=None, func=None, text='', font="Segoe Print",
                 font_size=16, font_clr=[0, 0, 0]):
        # setting the button parameters
        self.clr = clr
        self.size = size
        self.func = func
        self.surf = pygame.Surface(size)
        self.rect = self.surf.get_rect(center=position)
        if cngclr:
            self.cngclr = cngclr
        else:
            self.cngclr = clr

        if len(clr) == 4:
            self.surf.set_alpha(clr[3])

        self.font = pygame.font.SysFont(font, font_size)
        self.txt = text
        self.font_clr = font_clr
        self.txt_surf = self.font.render(self.txt, 1, self.font_clr)
        self.txt_rect = self.txt_surf.get_rect(center=[wh // 2 for wh in self.size])
    # draw a button
    def draw(self, screen):
        self.mouseover()

        self.surf.fill(self.curclr)
        self.surf.blit(self.txt_surf, self.txt_rect)
        screen.blit(self.surf, self.rect)
    # we change the color of the button if the cursor is hovered over it
    def mouseover(self):
        self.curclr = self.clr
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.curclr = self.cngclr
    # calling the function if the button was pressed
    def call_back(self, *args):
        if self.func:
            return self.func(*args)


if __name__ == '__main__':
    pygame.init()
    game = GameOfLife(640, 480, 20)
    game.run()
