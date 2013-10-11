#!/usr/bin/env python
# encoding: utf-8

from sys import stdout
import os
TERM_CHAR = { "ERASE_UP"      : chr(27) + "[1J",
              "ERASE_DOWN"    : chr(27) + "[J",
              "ERASE_LINE"    : chr(27) + "[2K",
              "ERASE_SCREEN"  : chr(27) + "[2J",
              "CURSOR_HOME"   : chr(27) + "[h",
              "SAVE_CURSOR"   : chr(27) + "[s",
              "UNSAVE_CURSOR" : chr(27) + "[u" }
TERM_FOREGROUND_COLOR = { 'BLACK'   : 30,
                          'RED'     : 31,
                          'GREEN'   : 32,
                          'YELLOW'  : 33,
                          'BLUE'    : 34,
                          'MAGENTA' : 35,
                          'CYAN'    : 36,
                          'WHITE'   : 37}

TERM_BACKGROUND_COLOR = { 'BLACK'   : 40,
                          'RED'     : 41,
                          'GREEN'   : 42,
                          'YELLOW'  : 43,
                          'BLUE'    : 44,
                          'MAGENTA' : 45,
                          'CYAN'    : 46,
                          'WHITE'   : 47 }

# This will not refresh when terminal size is changed
ROWS, COLUMNS = [int(x) for x in os.popen('stty size', 'r').read().split()]

def TERM_CURSOR_UP(count=1):
    __TERM_CURSOR_MOVE('A', count)

def TERM_CURSOR_DOWN(count=1):
    __TERM_CURSOR_MOVE('B', count)

def TERM_CURSOR_FORWARD(count=1):
    __TERM_CURSOR_MOVE('C', count)

def TERM_CURSOR_BACK(count=1):
    __TERM_CURSOR_MOVE('D', count)

# NEXT_LINE and PREVIOUS_LINE should not be used
def TERM_NEXT_LINE(count=1):
    TERM_NEWLINE()  # Quick fix
    # __TERM_CURSOR_MOVE('E', count)

def TERM_PREVIOUS_LINE(count=1):
    TERM_CURSOR_UP(count)  # Quick fix
    # __TERM_CURSOR_MOVE('F', count)

def __TERM_CURSOR_MOVE(move, count):
    stdout.write(chr(27) + "[" + str(count) + move if count > 0 else '')

def TERM_HOME():
    # Hack to bring cursor back to beginning of line

    # TERM_NEXT_LINE()      # NOTE: This will not work in some terminals
    # TERM_PREVIOUS_LINE()  # (works on TMUX for some reason however)

    # TERM_NEWLINE()        # NOTE: This WILL break the line, but it will work
    # TERM_CURSOR_UP()      # for more terminals

    TERM_CURSOR_BACK(COLUMNS)  # Less of a hack

def TERM_ERASE_UP():
    stdout.write(chr(27) + "[1J")

def TERM_ERASE_DOWN():
    stdout.write(chr(27) + "[J")

def TERM_ERASE_LINE():
    stdout.write(chr(27) + "[2K")

def TERM_ERASE_SCREEN():
    stdout.write(chr(27) + "[2J")

def TERM_CURSOR_HOME():
    stdout.write(chr(27) + "[h")

def TERM_SAVE_CURSOR():
    stdout.write(chr(27) + "[s")

def TERM_UNSAVE_CURSOR():
    stdout.write(chr(27) + "[u")

def TERM_NEWLINE(count=1):
    stdout.write("\n"*count)

def TERM_HIGHLIGHT(line):
    return TERM_DISPLAY_ATTR(line, 7)

def TERM_UNDERLINE(line):
    return TERM_DISPLAY_ATTR(line, 4)

def TERM_BOLD(line):
    return TERM_DISPLAY_ATTR(line, 1)

def TERM_DISPLAY_ATTR(line, attr):
    return (chr(27) + "[" + str(attr) + "m") + (line) + (chr(27) + "[0m")
