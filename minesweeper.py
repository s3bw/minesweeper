import pyxel

from consts import TILE_SIZE, GRID_PADDING, BOARD_X, BOARD_Y, NUM_MINES, STATUS_BAR_HEIGHT
from board import Board, TileType, Flag

WIDTH = GRID_PADDING * 2 + BOARD_X * TILE_SIZE
HEIGHT = GRID_PADDING * 2 + BOARD_Y * TILE_SIZE + STATUS_BAR_HEIGHT

NUM_COLORS = {
    1: 12,  # Blue
    2: 3,   # Green
    3: 8,   # Red
    4: 1,   # Dark Blue
    5: 4,   # Brown
    6: 3,   # Dark Green
    7: 0,   # Black
    8: 5,   # Dark Gray
}


class App:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Minesweeper")
        pyxel.mouse(True)
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.board = Board(BOARD_X, BOARD_Y, NUM_MINES)
        self.safe = True
        self.game_over = False

    def update(self):
        if pyxel.btnp(pyxel.KEY_R):
            self.reset()
            return

        if self.game_over:
            return

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            gx, gy = self._mouse_to_grid()
            if gx is not None:
                if self.safe:
                    self.safe = self.board.leftclick(gx, gy)
                    if not self.safe:
                        self.board.show_mines()
                        self.game_over = True

        if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            gx, gy = self._mouse_to_grid()
            if gx is not None and self.safe:
                self.board.rightclick(gx, gy)

        if self.safe and self.board.check_win():
            self.board.display_win()
            self.game_over = True

    def _mouse_to_grid(self):
        mx = pyxel.mouse_x - GRID_PADDING
        my = pyxel.mouse_y - GRID_PADDING
        gx = mx // TILE_SIZE
        gy = my // TILE_SIZE
        if 0 <= gx < BOARD_X and 0 <= gy < BOARD_Y:
            return gx, gy
        return None, None

    def draw(self):
        pyxel.cls(5)

        # Draw grid
        for gx in range(BOARD_X):
            for gy in range(BOARD_Y):
                px = GRID_PADDING + gx * TILE_SIZE
                py = GRID_PADDING + gy * TILE_SIZE
                self._draw_tile(px, py, gx, gy)

        # Grid lines
        for i in range(BOARD_X + 1):
            x = GRID_PADDING + i * TILE_SIZE
            pyxel.line(x, GRID_PADDING, x, GRID_PADDING + BOARD_Y * TILE_SIZE, 0)
        for i in range(BOARD_Y + 1):
            y = GRID_PADDING + i * TILE_SIZE
            pyxel.line(GRID_PADDING, y, GRID_PADDING + BOARD_X * TILE_SIZE, y, 0)

        # Status bar
        sy = GRID_PADDING * 2 + BOARD_Y * TILE_SIZE
        remaining = self.board.n_mines - len(self.board.flags)
        status = f"Mines:{remaining}"
        if self.game_over:
            if self.safe or self.board.check_win():
                status += " WIN!"
            else:
                status += " LOST"
            status += " R:retry"
        pyxel.text(GRID_PADDING, sy, status, 7)

    def _draw_tile(self, px, py, gx, gy):
        board = self.board
        if board.grid is None:
            pyxel.rect(px + 1, py + 1, TILE_SIZE - 1, TILE_SIZE - 1, 6)
            pyxel.line(px + 1, py, px + TILE_SIZE - 1, py, 7)
            pyxel.line(px, py + 1, px, py + TILE_SIZE - 1, 7)
            return

        tile = board.grid[gx][gy]

        if tile.flagged and not tile.visible:
            col = 6
            if tile._flag_colour == Flag.Green:
                col = 11
            elif tile._flag_colour == Flag.Yellow:
                col = 10
            pyxel.rect(px + 1, py + 1, TILE_SIZE - 1, TILE_SIZE - 1, col)
            pyxel.text(px + 3, py + 2, "F", 8)
            return

        if not tile.visible:
            pyxel.rect(px + 1, py + 1, TILE_SIZE - 1, TILE_SIZE - 1, 6)
            pyxel.line(px + 1, py, px + TILE_SIZE - 1, py, 7)
            pyxel.line(px, py + 1, px, py + TILE_SIZE - 1, 7)
            return

        # Revealed tile
        if tile.type == TileType.Detonation:
            pyxel.rect(px + 1, py + 1, TILE_SIZE - 1, TILE_SIZE - 1, 8)
            pyxel.text(px + 2, py + 2, "*", 0)
        elif tile.type == TileType.Mine:
            pyxel.rect(px + 1, py + 1, TILE_SIZE - 1, TILE_SIZE - 1, 13)
            pyxel.text(px + 2, py + 2, "*", 0)
        elif tile.type == TileType.Empty:
            pyxel.rect(px + 1, py + 1, TILE_SIZE - 1, TILE_SIZE - 1, 13)
        else:
            pyxel.rect(px + 1, py + 1, TILE_SIZE - 1, TILE_SIZE - 1, 13)
            n = tile.n
            pyxel.text(px + 3, py + 2, str(n), NUM_COLORS.get(n, 0))


App()
