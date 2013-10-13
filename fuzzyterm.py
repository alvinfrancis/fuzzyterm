#!/usr/bin/env python
# encoding: utf-8

import re
import os
from sys import stdout
import subprocess
from getch import getch
from term import TERM_CURSOR_UP
from term import TERM_CURSOR_DOWN
# from term import TERM_CURSOR_FORWARD
# from term import TERM_ERASE_UP
# from term import TERM_ERASE_DOWN
from term import TERM_ERASE_LINE
# from term import TERM_ERASE_SCREEN
# from term import TERM_CURSOR_HOME
# from term import TERM_SAVE_CURSOR
# from term import TERM_UNSAVE_CURSOR
from term import TERM_NEWLINE
from term import TERM_HIGHLIGHT
from term import TERM_HOME
from term import TERM_BOLD
from term import TERM_CHAR
# from term import ROWS
from term import COLUMNS
from term import TERM_DISPLAY_ATTR
from term import TERM_FOREGROUND_COLOR
# from pipes import quote
import argparse
# import glob

def fuzzy_match_in_list(input, candidates=[f for f in os.listdir(os.getcwd())]):
    expr = ''.join(['[^' + i + ']*' + i for i in input])
    return [w for w in candidates if re.match(expr, w, re.IGNORECASE)]


class term_line:
    def __init__(self):
        self.line = ''

    def display(self):
        TERM_ERASE_LINE()
        TERM_HOME()
        stdout.write(self.line)

    def clear(self):
        TERM_ERASE_LINE()
        TERM_HOME()

    def __str__(self):
        return TERM_CHAR["ERASE_UP"] + self.prompt


class term_prompt:
    """
    Same as term_line, but also includes a rjust-ed prompt
    """
    def __init__(self):
        self.line = ''
        self.rprompt = ''

    def display(self):
        """Display this term component.

        Pre:  Cursor at the beginning of this term component.
        Post: Cursor at the beginning of this term component.
        """
        TERM_ERASE_LINE()
        # Account for the HIGHLIGHT special chars
        stdout.write(
            (TERM_BOLD(os.getcwd())
             .rjust(min(COLUMNS,100) + 8)))
        TERM_HOME()
        stdout.write(self.line)

    def clear(self):
        """Clear this term component. """
        TERM_ERASE_LINE()
        TERM_HOME()

    def __str__(self):
        return TERM_CHAR["ERASE_UP"] + self.prompt


class term_list:
    """
    Arguments:
        display_func: function applied to each line prior to display
    """
    lines = []
    selected_offset = 0

    def __init__(self, lines, display_func=None):
        self.lines = lines
        if display_func == None:
            self.__display_line = term_list.__display_line
        else:
            self.__display_line = display_func

    def display(self):
        """Display this term component.

        Pre:  Cursor at the beginning of this term component.
        Post: Cursor at the beginning of this term component.
        """
        for i, line in enumerate(self.lines):

            line = self.__display_line(line)
            # Highlighting saved here
            if i == self.selected_offset:
                line = TERM_HIGHLIGHT(line)
            print line
        for _i in range(len(self.lines)):
            TERM_CURSOR_UP()
        stdout.flush()

    def clear(self):
        """Clear this term component.

        Clear will send a number of erase signals corresponding to the number
        of lines currently in the list. Consequently, it is important to keep
        the 'displayed' list synced with the internal list.

        Pre:  Cursor at the beginning of this term component.
        Post: Cursor at the beginning of this term component.
        """
        TERM_CURSOR_DOWN(len(self.lines))  # NOTE: CURSOR DOWN DOES NOT SCROLL PAST THE WINDOW BORDER
        for _i in range(len(self.lines)):
            TERM_CURSOR_UP()
            TERM_ERASE_LINE()
        stdout.flush()

    def get_selected(self):
        return self.lines[self.selected_offset]

    @staticmethod
    def __display_line(line):
        """
        Override this method to add additional processing to a line before
        being displayed
        """
        return line


class term_fuzzy:
    def __init__(self, candidates=None, command=None, options=None,
                 length=None, path=None, output=None, isBackground=None):
        self.command = command
        self.options = options
        self.length = length
        os.chdir(path)
        self.output = output
        self.isBackground = isBackground
        self.prompt = term_prompt()
        self.candidates = \
                term_list(term_fuzzy.__get_candidates(self.prompt.line, self.length),
                          term_fuzzy.__display_path)
        self.candidates.__display_line = term_fuzzy.__display_path
        self.process_key = { 127: self.__process_backspace,         #Backspace
                              27: self.__process_escape,            #Escape
                              21: self.__process_clear_prompt,      #CTRL-u
                              20: self.__process_select_directory,  #CTRL-t
                              18: self.__process_select_item,       #CTRL-r
                              12: self.__process_cd_forward,        #CTRL-l
                              8: self.__process_cd_back,            #CTRL-h
                              11: self.__process_select_up,         #CTRL-k
                              10: self.__process_select_down        #CTRL-j
                            }

    def run(self):
        self.prompt.display()
        TERM_NEWLINE()
        self.candidates.display()
        TERM_CURSOR_UP()
        stdout.flush()
        while True:
            try:
                ord(self.__parsekey())
                TERM_NEWLINE()
                self.__refresh()
                self.__redraw()
            except Exception, ex:
                # TODO: work on this
                if ex.args[0] == 'escape':
                    print "Escaping ..."
                else:
                    pass
                break

    def __parsekey(self):
        """Parse and process key and return the ordinality of the key signal.

        Assumes that the cursor is on the prompt.
        """
        key = getch()
        # TODO: multichar input like arrows
        # if ord(key) == 27:
        #     key2 = getch()
        #     print ord(key2)

        try:
            self.process_key[ord(key)]()
            if ord(key) not in [10, 11]:
                self.candidates.selected_offset = 0
        except KeyError:
            # Normal letter key
            if str(key).isalnum() | str(key).isspace():
                self.__process_normal(key)
                self.candidates.selected_offset = 0
            else:
                pass

        return key

    # Process Key functions
    # NOTES:
    # 1.) Pre-processing: the cursor should be at the end of the prompt line.
    # 2.) Post-processing: the cursor should be at the beginning of the
    #     candidates list.
    # 3.) This is not responsible for redraw (leave that to __redraw in the
    #     run loop)

    def __process_normal(self, key):
        self.prompt.line += key

    def __process_escape(self):
        self.__clear()
        raise Exception('escape')

    def __process_backspace(self):
        self.prompt.line = self.prompt.line[:-1]

    def __process_clear_prompt(self):
        self.prompt.line = ''

    def __process_select_down(self):
        self.candidates.selected_offset = \
            (self.candidates.selected_offset + 1) % len(self.candidates.lines)

    def __process_select_up(self):
        self.candidates.selected_offset = \
            (self.candidates.selected_offset - 1) % len(self.candidates.lines)

    def __process_select_item(self):
        self.__clear()
        # Flush to immediately get clear effect or else output might get garbled
        stdout.flush()

        if self.isBackground:
            child_pid = os.fork()
            if child_pid==0:
                self.__run_command(os.getcwd() + "/" + self.candidates.get_selected())
        else:
            self.__run_command(os.getcwd() + "/" + self.candidates.get_selected())

        raise Exception('select')

    def __process_select_directory(self):
        self.__clear()
        # Flush to immediately get clear effect or else output might get garbled
        stdout.flush()

        if self.isBackground:
            child_pid = os.fork()
            if child_pid==0:
                self.__run_command(os.getcwd())
        else:
            self.__run_command(os.getcwd())

        raise Exception('select')

    def __process_cd_forward(self):
        try:
            os.chdir(self.candidates.get_selected())
            self.prompt.line = ''
        except Exception, ex:
            TERM_ERASE_LINE()
            TERM_HOME()
            print ex

    def __process_cd_back(self):
        self.prompt.line = ''
        os.chdir("..")

    ## End of Process Key functions

    def __run_command(self, item):
        command = [self.command]
        if self.options:
            command.append(self.options)
        command.append(item)
        subprocess.check_call(command, stdout=open(self.output, "w") if self.output else None)

    def __clear(self):
        """Clear self.

        Post: Cursor at prompt.
        Post:  Cursor at the beginning of candidate list.
        """
        self.prompt.clear()
        TERM_CURSOR_DOWN()
        self.candidates.clear()
        TERM_CURSOR_UP()

    def __redraw(self):
        """Redraw self.

        Pre:  Cursor at the beginning of candidate list.
        Post: Cursor at the end of prompt.
        """
        self.candidates.display()
        # Prompt should be last written to keep cursor in the proper position
        # do not use prompt.display()?
        TERM_CURSOR_UP()
        self.prompt.display()
        stdout.flush()

    def __refresh(self):
        """Refresh according to logic. """

        # Clear must be done here before candidates.lines is updated
        self.candidates.clear()
        self.candidates.lines = term_fuzzy.__get_candidates(self.prompt.line,
                                                            self.length)

    @staticmethod
    def __get_candidates(match, length):
        return fuzzy_match_in_list(match,
                                   os.listdir(os.getcwd()))[:length]

    @staticmethod
    def __display_path(line):
        if os.path.isdir(line):
            line = TERM_DISPLAY_ATTR(line, TERM_FOREGROUND_COLOR['BLUE'])
        if os.path.islink(line):
            line = TERM_DISPLAY_ATTR(line, TERM_FOREGROUND_COLOR['RED'])
        return line


def main():
    parser = argparse.ArgumentParser(
        description="Search for item fuzzily and apply COMMAND to item"
    )
    parser.add_argument("-c", "--command", default="echo", type=str,
                        help="command to run")
    parser.add_argument("-t", "--options", default=None, type=str,
                        help="options for COMMAND")
    parser.add_argument("-l", "--length", default=20, type=int,
                        help="maximum number of items displayed in list")
    parser.add_argument("-p", "--path", default=os.getcwd(), type=str,
                        help="starting path")
    parser.add_argument("-o", "--output", default=None, type=str,
                        help="stdout redirect")
    parser.add_argument("-b", "--background", action="store_true",
                        dest="isBackground", default=False,
                        help="run command in background (&)")
    args = parser.parse_args()

    comm = term_fuzzy(fuzzy_match_in_list('', os.listdir(os.getcwd()))[:args.length],
                      command=args.command,
                      options=args.options,
                      length=args.length,
                      path=args.path,
                      output=args.output,
                      isBackground=args.isBackground)
    comm.run()


if __name__ == '__main__':
   main()
