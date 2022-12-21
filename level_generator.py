import pygame
import csv

pygame.font.init()
WIDTH, HEIGHT = 1400, 900
ROW, COL = 20, 20
SQUARE_LENGTH = 40
LEFT_BORDER = 20
TOP_BORDER = 20
BORDER_COLOR = (255, 255, 255)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Level Creation")


class Button:
    BUTTON_FONT = pygame.font.SysFont("comicSans", 50)

    def __init__(self, x, y, width, height, color, textcolor, text):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.textcolor = textcolor
        self.text = text

    def draw(self, window):
        button = self.BUTTON_FONT.render(self.text, True, self.textcolor)
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))
        window.blit(button, (self.x + self.width / 2 - button.get_width() / 2,
                             self.y + self.height / 2 - button.get_height() / 2))

    def clicked(self, x_pos, y_pos):
        if self.x <= x_pos <= self.x + self.width and self.y <= y_pos <= self.y + self.height:
            return True
        else:
            return False


class field:
    def __init__(self):
        self.thickness = 4
        self.normal_point = 5
        self.saving_point = 7
        self.matrix = [[2 for i in range(COL)] for j in range(ROW)]
        for i in range(0, ROW):
            self.matrix[i][0] = 1
            self.matrix[i][-1] = 1
        for j in range(1, COL - 1):
            self.matrix[0][j] = 1
            self.matrix[-1][j] = 1

        self.cage_pos = int(ROW / 2)
        self.build_cage()

    def build_cage(self):
        if COL % 2 == 0:
            for i in [0, 2]:
                for j in range(-4, 4):
                    self.matrix[self.cage_pos + i][int(COL / 2) + j] = 1

            for j in range(-3, 3):
                self.matrix[self.cage_pos + 1][int(COL / 2) + j] = 0

            self.matrix[self.cage_pos + 1][int(COL / 2) - 4] = 1
            self.matrix[self.cage_pos + 1][int(COL / 2) + 3] = 1

            self.matrix[self.cage_pos][int(COL / 2)] = 4
            self.matrix[self.cage_pos][int(COL / 2) - 1] = 4
        else:
            print("COL has to be even!")

    def change(self, x_pos, y_pos, key, window):
        row = int((y_pos - TOP_BORDER) / SQUARE_LENGTH)
        col = int((x_pos - LEFT_BORDER) / SQUARE_LENGTH)

        # cant edit cage area
        if int(COL / 2) - 5 < col < int(COL / 2) + 4 and self.cage_pos - 1 < row < self.cage_pos + 3:
            pass
        else:
            if 0 < row < ROW - 1 and 0 < col < COL - 1:
                self.matrix[row][col] = key
            elif (row == 0 or row == ROW - 1) and (0 < col < COL - 1):
                self.matrix[0][col] = key
                self.matrix[ROW - 1][col] = key
            elif (col == 0 or col == COL - 1) and (0 < row < ROW - 1):
                self.matrix[row][0] = key
                self.matrix[row][COL - 1] = key
        self.draw(window, True)

    def draw(self, window, first=False):
        if first:
            pygame.draw.rect(window, (0, 0, 0), (0, 0,
                                                 SQUARE_LENGTH * (ROW + 1), SQUARE_LENGTH * (COL + 1)))
            for row in range(ROW):
                for col in range(COL):
                    if self.matrix[row][col] == 1:
                        self.draw_tile(row, col, window)
        else:
            for row in range(ROW):
                for col in range(COL):
                    # 1 is borderline
                    # 2 point
                    # 3 saving point
                    # 4 no entry for player (ghost border)
                    if self.matrix[row][col] == 2:
                        self.draw_normal_point(row, col, window)
                    elif self.matrix[row][col] == 3:
                        self.draw_saving_point(row, col, window)

    def draw_tile(self, row, col, window):
        # compute center point
        center = ((row + 0.5) * SQUARE_LENGTH + TOP_BORDER, (col + 0.5) * SQUARE_LENGTH + LEFT_BORDER)
        # define and get point value around
        if row == 0 and 0 < col < COL - 1 and self.matrix[row][col + 1] != 1:
            self.draw_north(center, WIN)
            self.draw_south((ROW * SQUARE_LENGTH, center[1]), window)
        if row == 0 and 0 < col < COL - 1 and self.matrix[row][col - 1] != 1:
            self.draw_north(center, WIN)
            self.draw_south((ROW * SQUARE_LENGTH, center[1]), window)
        if col == 0 and 0 < row < ROW - 1 and self.matrix[row - 1][col] != 1:
            self.draw_west(center, WIN)
            self.draw_east((center[0], COL * SQUARE_LENGTH), window)
        if col == 0 and 0 < row < ROW - 1 and self.matrix[row + 1][col] != 1:
            self.draw_west(center, WIN)
            self.draw_east((center[0], COL * SQUARE_LENGTH), window)

        if self.matrix[(row - 1) % ROW][col] == 1 and row != 0:
            self.draw_north(center, window)
        if self.matrix[row][(col + 1) % COL] == 1 and col != COL - 1:
            self.draw_east(center, window)
        if self.matrix[(row + 1) % ROW][col] == 1 and row != ROW - 1:
            self.draw_south(center, window)
        if self.matrix[row][(col - 1) % COL] == 1 and col != 0:
            self.draw_west(center, window)
        if self.matrix[(row - 1) % ROW][col] != 1 and self.matrix[row][(col - 1) % COL] != 1 and self.matrix[row][(col + 1) % COL] != 1 and \
                self.matrix[(row + 1) % ROW][col] != 1:
            pygame.draw.rect(window, (255, 0, 0),
                             (LEFT_BORDER + SQUARE_LENGTH * (col + 0.5), TOP_BORDER + SQUARE_LENGTH * (row + 0.5),
                             2 * self.thickness, 2 * self.thickness))

    def draw_north(self, center, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (center[1] - int(self.thickness / 2), center[0] + int(self.thickness / 2) - SQUARE_LENGTH,
                          self.thickness, SQUARE_LENGTH))

    def draw_east(self, center, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (center[1] - int(self.thickness / 2), center[0] - int(self.thickness / 2),
                          SQUARE_LENGTH, self.thickness))

    def draw_south(self, center, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (center[1] - int(self.thickness / 2), center[0] - int(self.thickness / 2),
                          self.thickness, SQUARE_LENGTH))

    def draw_west(self, center, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (center[1] + int(self.thickness / 2) - SQUARE_LENGTH, center[0] - int(self.thickness / 2),
                          SQUARE_LENGTH, self.thickness))

    def draw_normal_point(self, row, col, window):
        center = ((col + 0.5) * SQUARE_LENGTH + LEFT_BORDER, (row + 0.5) * SQUARE_LENGTH + TOP_BORDER)
        pygame.draw.circle(window, (0, 0, 200), center, self.normal_point)

    def draw_saving_point(self, row, col, window):
        center = ((col + 0.5) * SQUARE_LENGTH + LEFT_BORDER, (row + 0.5) * SQUARE_LENGTH + TOP_BORDER)
        pygame.draw.circle(window, (50, 50, 200), center, self.saving_point)

    def clear(self):
        self.matrix = [[2 for i in range(COL)] for j in range(ROW)]
        for i in range(0, ROW):
            self.matrix[i][0] = 1
            self.matrix[i][-1] = 1
        for j in range(1, COL - 1):
            self.matrix[0][j] = 1
            self.matrix[-1][j] = 1

        self.build_cage()

    def save_as_csv(self, name):
        with open(f'levels/{name}.csv', 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            for row in self.matrix:
                csv_writer.writerow(row)


def main():
    FPS = 60
    run = True
    clock = pygame.time.Clock()
    env = field()
    env.draw(WIN, True)
    pygame.display.update()

    clear_button = Button(WIDTH - 300, 100, 200, 100, (50, 50, 50), (255, 255, 255), "Clear")
    save_button = Button(WIDTH - 300, 500, 200, 100, (50, 50, 50), (255, 255, 255), "save")

    def redraw_window():
        env.draw(WIN)
        clear_button.draw(WIN)
        save_button.draw(WIN)

        pygame.display.update()

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x_pos, y_pos = pygame.mouse.get_pos()
                if clear_button.clicked(x_pos, y_pos):
                    env.clear()
                elif save_button.clicked(x_pos, y_pos):
                    env.save_as_csv("level")

        keys = pygame.key.get_pressed()
        if keys[pygame.K_0]:
            x_pos, y_pos = pygame.mouse.get_pos()
            env.change(x_pos, y_pos, 0, WIN)
        elif keys[pygame.K_1]:
            x_pos, y_pos = pygame.mouse.get_pos()
            env.change(x_pos, y_pos, 1, WIN)
        elif keys[pygame.K_2]:
            x_pos, y_pos = pygame.mouse.get_pos()
            env.change(x_pos, y_pos, 2, WIN)
        elif keys[pygame.K_3]:
            x_pos, y_pos = pygame.mouse.get_pos()
            env.change(x_pos, y_pos, 3, WIN)
        elif keys[pygame.K_4]:
            x_pos, y_pos = pygame.mouse.get_pos()
            env.change(x_pos, y_pos, 4, WIN)
        elif keys[pygame.K_5]:
            x_pos, y_pos = pygame.mouse.get_pos()
            env.change(x_pos, y_pos, 5, WIN)
        elif keys[pygame.K_6]:
            x_pos, y_pos = pygame.mouse.get_pos()
            env.change(x_pos, y_pos - SQUARE_LENGTH, 6, WIN)

        redraw_window()


main()
