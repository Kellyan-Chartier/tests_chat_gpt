#!/usr/bin/env python3
"""Simple terminal-based Snake game using curses.

Use arrow keys to control the snake. Eat food to grow.
The game ends when the snake runs into itself or the wall.
"""

import curses
import random
from collections import deque

# Direction vectors
DIRECTIONS = {
    curses.KEY_UP: (-1, 0),
    curses.KEY_DOWN: (1, 0),
    curses.KEY_LEFT: (0, -1),
    curses.KEY_RIGHT: (0, 1),
}


def main(stdscr):
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(True)
    stdscr.timeout(100)  # Refresh every 100ms

    sh, sw = stdscr.getmaxyx()
    snake = deque([(sh // 2, sw // 2 + i) for i in range(3)])
    direction = curses.KEY_LEFT

    food = create_food(sh, sw, snake)

    while True:
        key = stdscr.getch()
        if key in DIRECTIONS:
            direction = key
        elif key == ord("q"):
            break

        new_head = move(snake[0], DIRECTIONS[direction])

        if (
            new_head[0] in {0, sh - 1}
            or new_head[1] in {0, sw - 1}
            or new_head in snake
        ):
            break

        snake.appendleft(new_head)

        if new_head == food:
            food = create_food(sh, sw, snake)
        else:
            snake.pop()

        draw(stdscr, snake, food)

    stdscr.nodelay(False)
    stdscr.addstr(sh // 2, sw // 2 - 5, "Game Over!")
    stdscr.getch()

def move(pos, vector):
    return pos[0] + vector[0], pos[1] + vector[1]


def create_food(sh, sw, snake):
    while True:
        food = (random.randint(1, sh - 2), random.randint(1, sw - 2))
        if food not in snake:
            return food


def draw(stdscr, snake, food):
    stdscr.clear()
    sh, sw = stdscr.getmaxyx()
    for y in range(sh):
        stdscr.addch(y, 0, "#")
        stdscr.addch(y, sw - 1, "#")
    for x in range(sw):
        stdscr.addch(0, x, "#")
        stdscr.addch(sh - 1, x, "#")

    stdscr.addch(food[0], food[1], "*")

    for y, x in snake:
        stdscr.addch(y, x, "O")

    stdscr.refresh()


if __name__ == "__main__":
    curses.wrapper(main)
