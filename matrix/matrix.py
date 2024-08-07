import shutil
import sys
import time
from random import choice, randrange, paretovariate

# Constants
MAX_CASCADES = 600
MAX_COLS = 20
FRAME_DELAY = 0.03
MAX_SPEED = 5

# ANSI escape codes
CSI = "\x1b["
HIDE_CURSOR = "?25l"
SHOW_CURSOR = "?25h"
SAVE_CURSOR = "s"
RESTORE_CURSOR = "u"
RESET_ATTRS = "m"
CLEAR_SCREEN = "2J"

# Colors
BLACK = "30"
GREEN = "32"
WHITE = "37"

# Character ranges
def getchars(start, end):
    return [chr(i) for i in range(start, end)]

latin = getchars(0x30, 0x80)
greek = getchars(0x390, 0x3d0)
hebrew = getchars(0x5d0, 0x5eb)
cyrillic = getchars(0x400, 0x50)

chars = latin + greek + hebrew + cyrillic

def pareto(limit, lines):
    scale = lines // 2
    number = (paretovariate(1.16) - 1) * scale
    return max(0, limit - number)

def pr(command):
    print(f"{CSI}{command}", end="")

def init():
    global cols, lines
    cols, lines = shutil.get_terminal_size()
    pr(HIDE_CURSOR)
    pr(SAVE_CURSOR)

def end():
    pr(RESET_ATTRS)
    pr(CLEAR_SCREEN)
    pr(RESTORE_CURSOR)
    pr(SHOW_CURSOR)

def print_at(char, x, y, color="", bright="0"):
    pr(f"{y};{x}f")
    pr(f"{bright};{color}m")
    print(char, end="", flush=True)

def update_line(speed, counter, line):
    counter += 1
    if counter >= speed:
        line += 1
        counter = 0
    return counter, line

def cascade(col, lines):
    speed = randrange(1, MAX_SPEED)
    espeed = randrange(1, MAX_SPEED)
    line = counter = ecounter = 0
    oldline = eline = -1
    erasing = False
    bright = "1"
    limit = pareto(lines, lines)
    
    while True:
        counter, line = update_line(speed, counter, line)
        if randrange(10 * speed) < 1:
            bright = "0"
        if 1 < line <= limit and oldline != line:
            print_at(choice(chars), col, line - 1, GREEN, bright)
        if line < limit:
            print_at(choice(chars), col, line, WHITE, "1")
        if erasing:
            ecounter, eline = update_line(espeed, ecounter, eline)
            print_at(" ", col, eline, BLACK)
        else:
            erasing = randrange(line + 1) > (lines / 2)
            eline = 0
        yield
        oldline = line
        if eline >= limit:
            print_at(" ", col, oldline, BLACK)
            break

def main():
    cascading = set()
    while True:
        while add_new(cascading): pass
        stopped = iterate(cascading)
        sys.stdout.flush()
        cascading.difference_update(stopped)
        time.sleep(FRAME_DELAY)

def add_new(cascading):
    if randrange(MAX_CASCADES + 1) > len(cascading):
        col = randrange(cols)
        for i in range(randrange(MAX_COLS)):
            cascading.add(cascade((col + i) % cols, lines))
        return True
    return False

def iterate(cascading):
    stopped = set()
    for c in cascading:
        try:
            next(c)
        except StopIteration:
            stopped.add(c)
    return stopped

def begin():
    try:
        init()
        main()
    except KeyboardInterrupt:
        pass
    finally:
        end()

if __name__ == "__main__":
    begin()
