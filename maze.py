import time
from tkinter import Tk, Canvas

class Window:

    def __init__(self, width, height):
        self.__root = Tk()
        self.__root.title = "Maze Solver"
        self.canvas = Canvas(width = width, height = height, bg = "#d9d9d9")
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

    SIZE = 36

    def __init__(self, p, win = None):
        self.p = p
        self.__win = win
        self.has_wall = [True, True, True, True]

    def draw(self):
        if self.has_wall[self.LEFT]:
            self.__win.draw_line(Line(
                self.p, Point(self.p.x, self.p.y + self.SIZE)
            ))
        if self.has_wall[self.TOP]:
            self.__win.draw_line(Line(
                self.p, Point(self.p.x + self.SIZE, self.p.y)
            ))
        else:
            self.__win.draw_line(Line(
                self.p, Point(self.p.x + self.SIZE, self.p.y)
            ), "#d9d9d9")
        if self.has_wall[self.RIGHT]:
            self.__win.draw_line(Line(
                Point(self.p.x + self.SIZE, self.p.y),
                Point(self.p.x + self.SIZE, self.p.y + self.SIZE)
            ))
        if self.has_wall[self.BOTTOM]:
            self.__win.draw_line(Line(
                Point(self.p.x, self.p.y + self.SIZE),
                Point(self.p.x + self.SIZE, self.p.y + self.SIZE)
            ))
        else:
            self.__win.draw_line(Line(
                Point(self.p.x, self.p.y + self.SIZE),
                Point(self.p.x + self.SIZE, self.p.y + self.SIZE)
            ), "#d9d9d9")

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
    ):
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
        self._animate()

    def _animate(self):
        self.__win.redraw()
        time.sleep(0.05)

    def _break_entrance_and_exit(self):
        self._cells[0][0].has_wall[Cell.TOP] = False
        self._draw_cell(0, 0)
        self._cells[-1][-1].has_wall[Cell.BOTTOM] = False
        self._draw_cell(-1,-1)

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
    maze._animate()
    maze._break_entrance_and_exit()

    win.wait_for_close()

if __name__ == "__main__":
    main()
