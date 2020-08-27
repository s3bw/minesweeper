import argparse

import pygame

from consts import GRIDPADDING
from consts import BLOCK_SIZE

parser = argparse.ArgumentParser()
parser.add_argument("-x", type=int, default=16)
parser.add_argument("-y", type=int, default=16)
parser.add_argument("-m", "--mines", type=int, default=40)

args = parser.parse_args()


BACKGROUND_COLOUR = (204, 204, 204)
FLAG_COUNT = 20

dx = (GRIDPADDING * 2) + (args.x * BLOCK_SIZE)
dy = (GRIDPADDING * 2) + (args.y * BLOCK_SIZE) + FLAG_COUNT

GUESS_TEXT_LENGTH = 40

fx = (dx / 2) - GUESS_TEXT_LENGTH
fy = dy - FLAG_COUNT

pygame.init()
win = pygame.display.set_mode((dx, dy))

import sprites
from board import Board


pygame.display.set_caption("Minesweeper")
font = pygame.font.SysFont("monospace", 15)


def _render_flg_count(mines: int, flags: int):
    return font.render(
        f"Mines: {mines - flags}", 1, (0, 0, 0)
    )


board = Board(args.x, args.y, mines=args.mines)
flag_count = _render_flg_count(board.n_mines, len(board.flags))


def render():
    win.fill(BACKGROUND_COLOUR)
    board.render(win)
    win.blit(flag_count, (fx, fy))

    pygame.display.update()


safe = True
playing = True
while playing:

    pos = None
    event = pygame.event.wait()

    if not safe:
        board.show_mines()

    if event.type == pygame.MOUSEBUTTONDOWN:
        leftclick, _, rightclick = pygame.mouse.get_pressed()
        pos = pygame.mouse.get_pos()

        if rightclick:
            board.rightclick(pos)
            flag_count = _render_flg_count(
                board.n_mines, len(board.flags)
            )

        elif leftclick and not safe:
            playing = False

        elif leftclick:
            safe = board.leftclick(pos)

    if event.type == pygame.QUIT:
        playing = False

    render()


pygame.quit()
