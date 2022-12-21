import pygame
import csv
import math

pygame.font.init()

# SQUARE_LENGTH should be dividable by PLAYER_VEL
PLAYER_VEL = 5
SQUARE_LENGTH = 40
TOP_BORDER = 50
LEFT_BORDER = 50
ROWS = 20
COLS = 20

WIDTH, HEIGHT = SQUARE_LENGTH * COLS + 2 * LEFT_BORDER, SQUARE_LENGTH * ROWS + 2 * TOP_BORDER
WIN = pygame.display.set_mode((HEIGHT, WIDTH))
pygame.display.set_caption("Pacman!")

PINK_GHOST = pygame.image.load("assets/pink_ghost_2.png")
PINK_GHOST = pygame.transform.scale(PINK_GHOST, (SQUARE_LENGTH + 20, SQUARE_LENGTH + 20))


def compute_angle(point_1, point_2, radius):
    """
    returns angle for function between point_1 and point_2 """
    if (point_2[0] - point_1[0]) == 0:
        if point_2[1] > point_1[1]:
            return point_1[0], point_1[1] + radius
        elif point_2[1] == point_1[1]:
            return point_1[0], point_1[1]
        if point_2[1] < point_1[1]:
            return point_1[0], point_1[1] - radius
    else:
        m = (point_2[1] - point_1[1]) / (point_2[0] - point_1[0])
        alpha = math.atan(m)
        delta_x = math.cos(alpha) * radius
        delta_y = math.sin(alpha) * radius
        if point_2[0] > point_1[0]:
            return point_1[0] + delta_x, point_1[1] + delta_y
        else:
            return point_1[0] - delta_x, point_1[1] - delta_y


class enemy:
    def __init__(self, start_x, start_y, vel, moon):
        self.x_index = start_x
        self.y_index = start_y
        # Position of upper point from picture
        self.x_pos = LEFT_BORDER + SQUARE_LENGTH * (start_x + 0.5)
        self.y_pos = TOP_BORDER + SQUARE_LENGTH * (start_y + 0.5)

        self.vel = vel
        self.player = moon

        self.dir = 0

        # mode means if the ghost is colored, blue or only eyes
        # 0 = normal color
        self.mode = 0

        self.width = SQUARE_LENGTH
        self.height = SQUARE_LENGTH + 10
        self.eye_width = 20
        self.eye_height = 10
        self.outer_radius = 17
        self.inner_radius = 9

    def draw(self, window):
        if self.mode == 0:
            pygame.draw.rect(window, (200, 150, 100), (self.x_pos - int(self.width / 2),
                                                       self.y_pos - int(self.height / 2),
                                                       self.width, self.height))
        self.draw_eyes(window)

    def draw_eyes(self, window):
        pygame.draw.circle(window, (255, 255, 255), (self.x_pos - self.eye_width,
                                                     self.y_pos - self.eye_height), self.outer_radius)
        pygame.draw.circle(window, (255, 255, 255), (self.x_pos + self.eye_width,
                                                     self.y_pos - self.eye_height), self.outer_radius)
        player_x = self.player.x_pos
        player_y = self.player.y_pos
        new_x, new_y = compute_angle((self.x_pos - self.eye_width, self.y_pos - self.eye_height),
                                     (player_x, player_y), self.inner_radius)
        pygame.draw.circle(window, (0, 0, 0), (new_x, new_y), self.inner_radius)
        pygame.draw.circle(window, (0, 0, 0), (new_x + 2 * self.eye_width, new_y), self.inner_radius)


class player:
    def __init__(self, start_x, start_y, vel, matrix):
        self.x_index = start_x
        self.y_index = start_y
        # circle center
        self.x_pos = LEFT_BORDER + SQUARE_LENGTH * (start_x + 0.5)
        self.y_pos = TOP_BORDER + SQUARE_LENGTH * (start_y + 0.5)

        self.radius = int(SQUARE_LENGTH / 2) + 10
        # eye position relative to center
        self.delta_eye = int(self.radius / 2)
        self.eye_radius = 5

        self.vel = vel

        self.playground = matrix
        self.playground.set_point(self.y_index, self.x_index)

        self.delta_x = 0
        self.delta_y = 0

        self.direction = 0

    def draw(self, window):
        pygame.draw.circle(window, (0, 255, 0),
                           (self.x_pos, self.y_pos), self.radius)

        # draw eye:
        if self.direction == 1:
            pygame.draw.circle(window, (50, 50, 50),
                               (self.x_pos - self.delta_eye, self.y_pos),
                               self.eye_radius)
        elif self.direction == 2:
            pygame.draw.circle(window, (50, 50, 50),
                               (self.x_pos, self.y_pos - self.delta_eye),
                               self.eye_radius)
        elif self.direction == 3:
            pygame.draw.circle(window, (50, 50, 50),
                               (self.x_pos + self.delta_eye, self.y_pos),
                               self.eye_radius)
        else:
            pygame.draw.circle(window, (50, 50, 50),
                               (self.x_pos, self.y_pos - self.delta_eye),
                               self.eye_radius)

        # animation: there are 2 levels: open and closed. self.delta describes the state
        # draw a polygon (triangle)
        if self.delta_x == 0 and self.delta_y == 0:
            pass
        elif self.delta_y == 0:
            length = 5 * self.delta_x
            if self.delta_x > (SQUARE_LENGTH / (2 * self.vel)):
                length = self.delta_x - 2*(self.delta_x - (SQUARE_LENGTH / (2 * self.vel)))
                length *= 5
            if self.direction == 2:
                pygame.draw.polygon(window, (0, 0, 0), ((self.x_pos, self.y_pos),
                                                        (self.x_pos + self.radius, self.y_pos + length),
                                                        (self.x_pos + self.radius, self.y_pos - length)))
            elif self.direction == 4:
                pygame.draw.polygon(window, (0, 0, 0), ((self.x_pos, self.y_pos),
                                                        (self.x_pos - self.radius, self.y_pos + length),
                                                        (self.x_pos - self.radius, self.y_pos - length)))
        elif self.delta_x == 0:
            length = 5 * self.delta_y
            if self.delta_y > (SQUARE_LENGTH / (2 * self.vel)):
                length = self.delta_y - 2*(self.delta_y - (SQUARE_LENGTH / (2 * self.vel)))
                length *= 5
            if self.direction == 1:
                pygame.draw.polygon(window, (0, 0, 0), ((self.x_pos, self.y_pos),
                                                        (self.x_pos + length, self.y_pos - self.radius),
                                                        (self.x_pos - length, self.y_pos - self.radius)))
            elif self.direction == 3:
                pygame.draw.polygon(window, (0, 0, 0), ((self.x_pos, self.y_pos),
                                                        (self.x_pos + length, self.y_pos + self.radius),
                                                        (self.x_pos - length, self.y_pos + self.radius)))

    def move_up(self, matrix):
        if (self.x_pos - LEFT_BORDER + 0.5 * SQUARE_LENGTH) % SQUARE_LENGTH == 0:
            self.direction = 1
            # if we are in the center of a new square we want to check the top
            if (self.y_pos - TOP_BORDER + 0.5 * SQUARE_LENGTH) % SQUARE_LENGTH == 0:
                self.delta_y = 0
                if matrix[(self.y_index - 1) % COLS][self.x_index] == 1 or \
                        matrix[(self.y_index - 1) % COLS][self.x_index] == 4:
                    return False
                else:
                    self.y_pos -= self.vel
            else:
                self.y_pos -= self.vel
            self.delta_y = (self.delta_y - 1) % (SQUARE_LENGTH / self.vel)
            if self.y_pos <= self.y_index * SQUARE_LENGTH + TOP_BORDER:
                self.y_index = (self.y_index - 1) % COLS
                self.playground.set_point(self.y_index, self.x_index)

                if self.y_index == COLS - 1:
                    self.y_pos = TOP_BORDER + SQUARE_LENGTH * (self.y_index + 0.5)
            return True

    def move_down(self, matrix):
        if (self.x_pos - LEFT_BORDER + 0.5 * SQUARE_LENGTH) % SQUARE_LENGTH == 0:
            self.direction = 3
            # if we are in the center of a new square we want to check the top
            if (self.y_pos - TOP_BORDER + 0.5 * SQUARE_LENGTH) % SQUARE_LENGTH == 0:
                self.delta_y = 0
                if matrix[(self.y_index + 1) % COLS][self.x_index] == 1 or \
                        matrix[(self.y_index + 1) % COLS][self.x_index] == 4:
                    return False
                else:
                    self.y_pos += self.vel
            else:
                self.y_pos += self.vel
            self.delta_y = (self.delta_y + 1) % (SQUARE_LENGTH / self.vel)
            if self.y_pos >= (self.y_index + 1) * SQUARE_LENGTH + TOP_BORDER:
                self.y_index = (self.y_index + 1) % COLS
                self.playground.set_point(self.y_index, self.x_index)

                if self.y_index == 0:
                    self.y_pos = TOP_BORDER + SQUARE_LENGTH * (self.y_index + 0.5)
            return True

    def move_right(self, matrix):
        if (self.y_pos - TOP_BORDER + 0.5 * SQUARE_LENGTH) % SQUARE_LENGTH == 0:
            self.direction = 2
            # if we are in the center of a new square we want to check the top
            if (self.x_pos - LEFT_BORDER + 0.5 * SQUARE_LENGTH) % SQUARE_LENGTH == 0:
                self.delta_x = 0
                if matrix[self.y_index][(self.x_index + 1) % ROWS] == 1 or \
                        matrix[self.y_index][(self.x_index + 1) % ROWS] == 4:
                    return False
                else:
                    self.x_pos += self.vel
            else:
                self.x_pos += self.vel
            self.delta_x = (self.delta_x + 1) % (SQUARE_LENGTH / self.vel)
            if self.x_pos >= (self.x_index + 1) * SQUARE_LENGTH + TOP_BORDER:
                self.x_index = (self.x_index + 1) % ROWS
                self.playground.set_point(self.y_index, self.x_index)

                if self.x_index == 0:
                    self.x_pos = LEFT_BORDER + SQUARE_LENGTH * (self.x_index + 0.5)
            return True

    def move_left(self, matrix):
        if (self.y_pos - TOP_BORDER + 0.5 * SQUARE_LENGTH) % SQUARE_LENGTH == 0:
            self.direction = 4
            # if we are in the center of a new square we want to check the top
            if (self.x_pos - TOP_BORDER + 0.5 * SQUARE_LENGTH) % SQUARE_LENGTH == 0:
                self.delta_x = 0
                if matrix[self.y_index][(self.x_index - 1) % ROWS] == 1 or \
                        matrix[self.y_index][(self.x_index - 1) % ROWS] == 4:
                    return False
                else:
                    self.x_pos -= self.vel
            else:
                self.x_pos -= self.vel
            self.delta_x = (self.delta_x - 1) % (SQUARE_LENGTH / self.vel)
            if self.x_pos <= self.x_index * SQUARE_LENGTH + TOP_BORDER:
                self.x_index = (self.x_index - 1) % ROWS
                self.playground.set_point(self.y_index, self.x_index)

                if self.x_index == ROWS - 1:
                    self.x_pos = LEFT_BORDER + SQUARE_LENGTH * (self.x_index + 0.5)
            return True


class board:
    def __init__(self, matrix):
        self.matrix = matrix
        self.row_count = len(self.matrix)
        self.col_count = len(self.matrix[0])
        self.thickness = 10
        self.normal_point = 5
        self.saving_point = 8
        self.count_points = 0
        for row in range(len(self.matrix)):
            for col in range(len(self.matrix[0])):
                if self.matrix[row][col] == 1:
                    self.count_points += 1

    def set_point(self, row, col):
        if self.matrix[row][col] == 2 or self.matrix[row][col] == 3:
            self.matrix[row][col] = 0
            self.count_points -= 1

    def draw_background(self, window):
        pygame.draw.rect(window, (0, 0, 0), (0, 0,
                                             SQUARE_LENGTH * ROWS + 2 * LEFT_BORDER,
                                             SQUARE_LENGTH * COLS + 2 * TOP_BORDER))
        for row in range(self.row_count):
            for col in range(self.col_count):
                # 1 is borderline
                # 2 point
                # 3 saving point
                # 4 no entry for player (ghost border)
                if self.matrix[row][col] == 1:
                    self.draw_tile(row, col, window)

    def draw(self, window):
        for row in range(self.row_count):
            for col in range(self.col_count):
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
        if row == 0 and 0 < col < self.col_count - 1 and self.matrix[row][col + 1] != 1:
            self.draw_north(center, WIN)
            self.draw_south(((self.row_count + 1) * SQUARE_LENGTH, center[1]), window)
        if row == 0 and 0 < col < self.col_count - 1 and self.matrix[row][col - 1] != 1:
            self.draw_north(center, WIN)
            self.draw_south(((self.row_count + 1) * SQUARE_LENGTH, center[1]), window)
        if col == 0 and 0 < row < self.row_count - 1 and self.matrix[row - 1][col] != 1:
            self.draw_west(center, WIN)
            self.draw_east((center[0], (self.col_count + 1) * SQUARE_LENGTH), window)
        if col == 0 and 0 < row < self.row_count - 1 and self.matrix[row + 1][col] != 1:
            self.draw_west(center, WIN)
            self.draw_east((center[0], (self.col_count + 1) * SQUARE_LENGTH), window)

        if self.matrix[(row - 1) % self.row_count][col] == 1 and row != 0:
            self.draw_north(center, window)
        if self.matrix[row][(col + 1) % self.col_count] == 1 and col != self.col_count - 1:
            self.draw_east(center, window)
        if self.matrix[(row + 1) % self.row_count][col] == 1 and row != self.row_count - 1:
            self.draw_south(center, window)
        if self.matrix[row][(col - 1) % self.col_count] == 1 and col != 0:
            self.draw_west(center, window)
        if self.matrix[(row - 1) % self.row_count][col] != 1 and self.matrix[row][(col - 1) % self.col_count] != 1 and \
                self.matrix[row][(col + 1) % self.col_count] != 1 and \
                self.matrix[(row + 1) % self.row_count][col] != 1:
            pygame.draw.rect(window, (255, 0, 0),
                             (LEFT_BORDER + SQUARE_LENGTH * (col + 0.5) - self.thickness,
                              TOP_BORDER + SQUARE_LENGTH * (row + 0.5) - self.thickness,
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


def load_csv():
    file = []
    with open("levels/level.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            new_row = []
            for element in row:
                new_row.append(int(element))
            file.append(new_row)
    return file


def main():
    csv_data = load_csv()
    fps = 60
    clock = pygame.time.Clock()
    run = True
    maze = board(csv_data)
    pacman = player(1, 1, PLAYER_VEL, maze)
    move = None
    win = False
    win_counter = 0

    ghost_1 = enemy(10, 10, 5, pacman)

    WIN.fill((100, 100, 100))
    pygame.display.update()

    def redraw_window():
        maze.draw_background(WIN)
        pacman.draw(WIN)
        ghost_1.draw(WIN)
        maze.draw(WIN)

        pygame.display.update()

    while run:
        if win:
            if win_counter <= 3 * fps:
                run = False
            else:
                win_counter += 1

        if move is not None:
            if move == 1:
                pacman.move_up(maze.matrix)
            elif move == 2:
                pacman.move_right(maze.matrix)
            elif move == 3:
                pacman.move_down(maze.matrix)
            elif move == 4:
                pacman.move_left(maze.matrix)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and move != 1:
            if pacman.move_up(maze.matrix):
                move = 1
        if keys[pygame.K_DOWN] and move != 3:
            if pacman.move_down(maze.matrix):
                move = 3
        if keys[pygame.K_RIGHT] and move != 2:
            if pacman.move_right(maze.matrix):
                move = 2
        if keys[pygame.K_LEFT] and move != 4:
            if pacman.move_left(maze.matrix):
                move = 4

        if maze.count_points == 0:
            win = True

        clock.tick(fps)
        redraw_window()


main()
