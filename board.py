from enum import Enum
from random import randrange


TRANSFORMS = [
    (-1, 0), (1, 0), (-1, -1), (1, 1),
    (0, -1), (0, 1), (-1, 1), (1, -1),
]


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def _around(pos):
    for t in TRANSFORMS:
        yield add(pos, t)


class TileType(Enum):
    Empty = 0
    One = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Mine = "mine"
    Detonation = "detonation"


class Flag:
    Red = "red"
    Green = "green"
    Yellow = "yellow"


class Tile:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.n = 0
        self.type = type
        self.flagged = False
        self._flag_colour = Flag.Red
        self.visible = False

    def toggle_visible(self):
        if not self.visible:
            self.visible = True

    def toggle_flag(self):
        self.flagged = not self.flagged

    def set_type(self, type):
        self.type = type

    def set_green(self):
        self._flag_colour = Flag.Green

    def set_yellow(self):
        self._flag_colour = Flag.Yellow

    def increment(self):
        if self.type == TileType.Mine:
            raise ValueError("Can't increment a mine")
        self.n += 1
        self.type = TileType(self.n)

    def around(self):
        yield from _around((self.x, self.y))


class Board:
    def __init__(self, x, y, mines):
        self.x = x
        self.y = y
        self.n_visible = x * y
        self.n_mines = mines
        self.flags = set()
        self.grid = None
        self._grid_constructed = False
        self._revealed = False
        self.mines = set()

    def _inside_board(self, x, y):
        return 0 <= x < self.x and 0 <= y < self.y

    def _construct_grid(self, x, y, first_pos):
        exclude = set(_around(first_pos))
        exclude.add(first_pos)

        grid = [
            [Tile(rx, ry, TileType.Empty) for ry in range(y)]
            for rx in range(x)
        ]

        mines = set()
        while len(mines) < self.n_mines:
            mx, my = randrange(self.x), randrange(self.y)
            if (mx, my) not in mines and (mx, my) not in exclude:
                mines.add((mx, my))
                grid[mx][my].set_type(TileType.Mine)

        for mx, my in mines:
            tile = grid[mx][my]
            for ox, oy in tile.around():
                if self._inside_board(ox, oy):
                    other = grid[ox][oy]
                    if other.type != TileType.Mine:
                        other.increment()

        self.mines = mines
        return grid

    def rightclick(self, gx, gy):
        if not self._inside_board(gx, gy):
            return
        if not self._grid_constructed:
            return
        tile = self.grid[gx][gy]
        if tile.visible:
            return
        tile.toggle_flag()
        if tile.flagged:
            self.flags.add((gx, gy))
        else:
            self.flags.remove((gx, gy))

    def leftclick(self, gx, gy):
        if not self._inside_board(gx, gy):
            return True
        if not self._grid_constructed:
            self._grid_constructed = True
            self.grid = self._construct_grid(self.x, self.y, (gx, gy))
        tile = self.grid[gx][gy]
        if tile.flagged:
            return True
        if tile.type == TileType.Mine:
            tile.type = TileType.Detonation
            return False
        if tile.visible:
            return True
        searched = set()
        tile.toggle_visible()
        self.n_visible -= 1
        self._zero_search(tile, searched)
        return True

    def _zero_search(self, tile, searched):
        if tile.n != 0 or tile.type == TileType.Mine or tile.flagged:
            return searched
        for pos in tile.around():
            px, py = pos
            if self._inside_board(px, py):
                t = self.grid[px][py]
                if t not in searched:
                    searched.add(t)
                    searched = self._zero_search(t, searched)
                if not t.visible:
                    t.toggle_visible()
                    self.n_visible -= 1
        return searched

    def check_win(self):
        return self.n_visible == self.n_mines

    def display_win(self):
        if not self._revealed:
            self._revealed = True
            for mx, my in self.mines:
                tile = self.grid[mx][my]
                tile.set_yellow()
                if not tile.flagged:
                    tile.toggle_flag()
                    self.flags.add((mx, my))

    def show_mines(self):
        if not self._revealed:
            self._revealed = True
            for pos in self.mines:
                mx, my = pos
                tile = self.grid[mx][my]
                if pos not in self.flags:
                    tile.toggle_visible()
                else:
                    tile.set_green()
