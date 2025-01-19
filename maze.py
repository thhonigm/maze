import time
from tkinter import Tk, Canvas
import random

CELL_COLOR = "black"
BG_COLOR = "#d9d9d9"
MOVE_COLOR = "red"
SHOW_NOT_VISITED = False
DRAW_INVISIBLE = False


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

    def animate(self):
        self.redraw()
        time.sleep(0.05)

    def wait_for_close(self):
        self.is_running = True
        while self.is_running:
            self.redraw()

    def close(self):
        self.is_running = False

    def draw_line(self, line, fill_color):
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
    DIRECTIONS = (RIGHT, BOTTOM, LEFT, TOP,)

    SIZE = 41

    def __init__(self, p):
        self.p = p
        self.has_wall = [True, True, True, True]
        self.visited = False

    def draw(self, win, animate = False):
        if win is None:
            return
        lines = {True: [], False: []}
        lines[self.has_wall[self.LEFT]].append((
            Point(self.p.x, self.p.y),
            Point(self.p.x, self.p.y + self.SIZE),
        ))
        lines[self.has_wall[self.TOP]].append((
            Point(self.p.x, self.p.y),
            Point(self.p.x + self.SIZE, self.p.y),
        ))
        lines[self.has_wall[self.RIGHT]].append((
            Point(self.p.x + self.SIZE, self.p.y),
            Point(self.p.x + self.SIZE, self.p.y + self.SIZE),
        ))
        lines[self.has_wall[self.BOTTOM]].append((
            Point(self.p.x, self.p.y + self.SIZE),
            Point(self.p.x + self.SIZE, self.p.y + self.SIZE),
        ))
        if DRAW_INVISIBLE:
            for p, q in lines[False]:
                if p.x == q.x:
                    p.y += 1
                    q.y -= 1
                else:
                    p.x += 1
                    q.x -= 1
                win.draw_line(Line(p, q), BG_COLOR)
        for p, q in lines[True]:
            win.draw_line(Line(p, q), CELL_COLOR)
        if SHOW_NOT_VISITED:
            for line in ((
                Line(Point(self.p.x + self.SIZE//4, self.p.y + self.SIZE//4),
                     Point(self.p.x + 3*self.SIZE//4, self.p.y + 3*self.SIZE//4)),
                Line(Point(self.p.x + 3*self.SIZE//4, self.p.y + self.SIZE//4),
                    Point(self.p.x + self.SIZE//4, self.p.y + 3*self.SIZE//4))
            )):
                if self.visited:
                    if DRAW_INVISIBLE:
                        win.draw_line(line, BG_COLOR)
                else:
                    win.draw_line(line, CELL_COLOR)
        if animate:
            win.animate()

    def draw_move(self, to_cell, win, undo = False, animate = False):
        if win is None:
            return
        center = Point(self.p.x + self.SIZE//2, self.p.y + self.SIZE//2)
        to_center = Point(to_cell.p.x + self.SIZE//2, to_cell.p.y + self.SIZE//2)
        win.draw_line(Line(center, to_center), BG_COLOR if undo else MOVE_COLOR)
        if animate:
            win.animate()


class Maze:

    ANIMATE_INIT = False

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
        self._break_entrance_and_exit()
        self._break_walls_r()
        self._reset_cells_visited()

    def _create_cells(self):
        self._cells = []
        for c in range(self.num_cols):
            self._cells.append([])
            for r in range(self.num_rows):
                cell = Cell(
                    Point(self.x1 + c * self.cell_size_x,
                          self.y1 + r * self.cell_size_y))
                self._cells[-1].append(cell)
                if self.ANIMATE_INIT:
                    cell.draw(self.__win, True)

    def _wall_down(self, c, r, d):
        self._cells[c][r].has_wall[d] = False
        if self.ANIMATE_INIT:
            self._cells[c][r].draw(self.__win, True)

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
        self._cells[i][j].visited = True
        while True:
            cells_to_visit = []
            for d in Cell.DIRECTIONS:
                to_visit, ii, jj, dd = self._next_cell(i, j, d)
                if to_visit:
                    cells_to_visit.append((d, ii, jj, dd))
            if len(cells_to_visit) == 0:
                if self.ANIMATE_INIT:
                    self._cells[i][j].draw(self.__win, True)
                return
            d, ii, jj, dd = random.choice(cells_to_visit)
            self._wall_down(i, j, d)
            self._wall_down(ii, jj, dd)
            self._cells[i][j].draw_move(self._cells[ii][jj], self.__win,
                                        animate = self.ANIMATE_INIT)
            self._break_walls_r(ii, jj)
            self._cells[i][j].draw_move(self._cells[ii][jj], self.__win, undo = True,
                                        animate = self.ANIMATE_INIT)

    def _reset_cells_visited(self):
        for c in self._cells:
            for cr in c:
                cr.visited = False
                cr.draw(self.__win, animate = self.ANIMATE_INIT)

    def solve(self):
        return self._solve_r(0, 0)

    def _solve_r(self, i, j):
        cell = self._cells[i][j]
        cell.visited = True
        cell.draw(self.__win, animate = True)
        if  i == len(self._cells) - 1 and j == len(self._cells[i]) - 1:
            return True
        for d in Cell.DIRECTIONS:
            if cell.has_wall[d]:
                continue
            ii, jj = i, j
            if d == Cell.LEFT:
                ii -= 1
            elif d == Cell.RIGHT:
                ii += 1
            elif d == Cell.TOP:
                jj -= 1
            elif d == Cell.BOTTOM:
                jj += 1
            if not (0 <= ii < len(self._cells) and 0 <= jj < len(self._cells[ii])):
                continue
            next_cell = self._cells[ii][jj]
            if next_cell.visited:
                continue;
            cell.draw_move(next_cell, self.__win, animate = True)
            if self._solve_r(ii ,jj):
                return True
            cell.draw_move(next_cell, self.__win, animate = True, undo = True)
        return False


def main1():
    win = Window(800, 600)
    win.animate()

    for i in range(17):
        for j in range(11):
            c = Cell(Point(10 + i*Cell.SIZE, 30 + j*Cell.SIZE))
            for side in range(4):
                if (i+j) & (1 << side):
                    c.has_wall[side] = False
            c.draw(win)

    i, j = 2, 3
    c1 = Cell(Point(10 + i*Cell.SIZE, 30 + j*Cell.SIZE))
    i, j = 2, 8
    c2 = Cell(Point(10 + i*Cell.SIZE, 30 + j*Cell.SIZE))
    c1.draw_move(c2, win, animate = True)

    i, j = 12, 8
    c3 = Cell(Point(10 + i*Cell.SIZE, 30 + j*Cell.SIZE))
    c2.draw_move(c3, win, animate = True)

    i, j = 12, 3
    c4 = Cell(Point(10 + i*Cell.SIZE, 30 + j*Cell.SIZE))
    c3.draw_move(c4, win, animate = True)
    c4.draw_move(c1, win, animate = True)
    time.sleep(2.5)

    c4.draw_move(c1, win, undo=True, animate = True)
    c3.draw_move(c4, win, undo=True, animate = True)
    c2.draw_move(c3, win, undo=True, animate = True)
    c1.draw_move(c2, win, undo=True, animate = True)

    win.wait_for_close()

def main():
    win = Window(800, 600)
    maze = Maze(20, 25, 13, 18, Cell.SIZE, Cell.SIZE, win)
    maze.solve()
    win.wait_for_close()

if __name__ == "__main__":
    main()
