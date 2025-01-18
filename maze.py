import time
from tkinter import Tk, Canvas
import random

BG_COLOR = "#d9d9d9"

class Window:

    def __init__(self, width, height):
        self.__root = Tk()
        self.__root.title = "Maze Solver"
        self.canvas = Canvas(width = width, height = height, bg = BG_COLOR)
        self.canvas.pack()
        self.is_running = False
        self.__root.protocol("WM_DELETE_WINDOW", self.close)

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self):
        self.is_running = True
        while self.is_running:
            self.redraw()

    def close(self):
        self.is_running = False

    def draw_line(self, line, fill_color = "black"):
        line.draw(self.canvas, fill_color)

class Point:

    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

class Line:

    def __init__(self, p, q):
        "Line between Point p and Point q"
        self.p = p
        self.q = q

    def draw(self, canvas, fill_color):
        canvas.create_line(self.p.x, self.p.y,
                           self.q.x, self.q.y,
                           fill = fill_color,
                           width = 2)

class Cell:

    LEFT = 0
    RIGHT = 1
    TOP = 2
    BOTTOM = 3
    DIRECTIONS = (LEFT, RIGHT, TOP, BOTTOM,)

    SIZE = 40

    SHOW_NOT_VISITED = False

    def __init__(self, p, win = None):
        self.p = p
        self.__win = win
        self.has_wall = [True, True, True, True]
        self.visited = False

    def _draw_line(self, p1, p2, visible):
        if visible:
            self.__win.draw_line(Line(p1, p2))
        else:
            self.__win.draw_line(Line(p1, p2), BG_COLOR)

    def draw(self):
        self._draw_line(
            self.p,
            Point(self.p.x, self.p.y + self.SIZE),
            self.has_wall[self.LEFT]
        )
        self._draw_line(
            self.p,
            Point(self.p.x + self.SIZE, self.p.y),
            self.has_wall[self.TOP]
        )
        self._draw_line(
            Point(self.p.x + self.SIZE, self.p.y),
            Point(self.p.x + self.SIZE, self.p.y + self.SIZE),
            self.has_wall[self.RIGHT]
        )
        self._draw_line(
            Point(self.p.x, self.p.y + self.SIZE),
            Point(self.p.x + self.SIZE, self.p.y + self.SIZE),
            self.has_wall[self.BOTTOM]
        )
        if Cell.SHOW_NOT_VISITED:
            self._draw_line(
                Point(self.p.x + self.SIZE//4, self.p.y + self.SIZE//4),
                Point(self.p.x + 3*self.SIZE//4, self.p.y + 3*self.SIZE//4),
                not self.visited
            )
            self._draw_line(
                Point(self.p.x + 3*self.SIZE//4, self.p.y + self.SIZE//4),
                Point(self.p.x + self.SIZE//4, self.p.y + 3*self.SIZE//4),
                not self.visited
            )

    def draw_move(self, to_cell, undo = False):
        center = Point(self.p.x + self.SIZE//2, self.p.y + self.SIZE//2)
        to_center = Point(to_cell.p.x + self.SIZE//2, to_cell.p.y + self.SIZE//2)
        self.__win.draw_line(Line(center, to_center), "grey" if undo else "red")

class Maze:

    def __init__(
        self,
        x1,
        y1,
        num_rows,
        num_cols,
        cell_size_x,
        cell_size_y,
        win = None,
        seed = None
    ):
        if seed is not None:
            random.seed(seed)
        self.x1 = x1
        self.y1 = y1
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cell_size_x = cell_size_x
        self.cell_size_y = cell_size_y
        self.__win = win
        self._create_cells()

    def _create_cells(self):
        self._cells = []
        for c in range(self.num_cols):
            self._cells.append([])
            for r in range(self.num_rows):
                p = Point(self.x1 + c * self.cell_size_x,
                          self.y1 + r * self.cell_size_y)
                self._cells[-1].append(Cell(p, self.__win))
        for c in range(self.num_cols):
            for r in range(self.num_rows):
                self._draw_cell(c, r)

    def _draw_cell(self, c, r):
        if self.__win is None:
            return
        self._cells[c][r].draw()

    def _wall_down(self, c, r, d):
        self._cells[c][r].has_wall[d] = False
        self._draw_cell(c, r)

    def _animate(self):
        self.__win.redraw()
        time.sleep(0.05)

    def _break_entrance_and_exit(self):
        self._wall_down(0, 0, Cell.TOP)
        self._wall_down(-1, -1, Cell.BOTTOM)

    def _next_cell(self, c, r, direction):
        if direction == Cell.LEFT:
            c -= 1
            d = Cell.RIGHT
        elif direction == Cell.RIGHT:
            c += 1
            d = Cell.LEFT
        elif direction == Cell.TOP:
            r -= 1
            d = Cell.BOTTOM
        elif direction == Cell.BOTTOM:
            r += 1
            d = Cell.TOP
        else:
            raise Exception(f"unknown direction {direction} ({c}, {r})")
        if 0 <= c < len(self._cells) and 0 <= r < len(self._cells[c]):
            return not self._cells[c][r].visited, c, r, d
        return False, 0, 0, 0

    def _break_walls_r(self, i = 0, j = 0):
        if self._cells[i][j].visited:
            raise Exception(f"({i}, {j}) already visited")
        self._cells[i][j].visited = True
        while True:
            cells_to_visit = []
            for d in Cell.DIRECTIONS:
                to_visit, ii, jj, dd = self._next_cell(i, j, d)
                if to_visit:
                    cells_to_visit.append((d, ii, jj, dd))
            if len(cells_to_visit) == 0:
                self._draw_cell(i, j)
                return
            d, ii, jj, dd = random.choice(cells_to_visit)
            self._wall_down(i, j, d)
            self._wall_down(ii, jj, dd)
            self._break_walls_r(ii, jj)


def main1():
    win = Window(800, 600)

    for i in range(17):
        for j in range(11):
            c = Cell(Point(10 + i*Cell.SIZE, 30 + j*Cell.SIZE), win)
            for side in range(4):
                if (i+j) & (1 << side):
                    c.has_wall[side] = False
            c.draw()

    i, j = 2, 3
    c1 = Cell(Point(10 + i*Cell.SIZE, 30 + j*Cell.SIZE), win)
    i, j = 2, 8
    c2 = Cell(Point(10 + i*Cell.SIZE, 30 + j*Cell.SIZE), win)
    c1.draw_move(c2)

    i, j = 12, 8
    c3 = Cell(Point(10 + i*Cell.SIZE, 30 + j*Cell.SIZE), win)
    c2.draw_move(c3)

    i, j = 12, 3
    c4 = Cell(Point(10 + i*Cell.SIZE, 30 + j*Cell.SIZE), win)
    c3.draw_move(c4)

    c4.draw_move(c1, undo=True)

    win.wait_for_close()

def main():
    win = Window(800, 600)

    maze = Maze(20, 25, 6, 10, Cell.SIZE, Cell.SIZE, win)
    maze._break_entrance_and_exit()
    maze._break_walls_r()

    win.wait_for_close()

if __name__ == "__main__":
    main()
