fuzzyterm.py
============

Fuzzy incremental search on the terminal.

Basic Usage
-----------

* Search for an item fuzzily and use item as an argument for COMMAND

        fuzzyterm -c COMMAND

## Keys

* `CTRL-j`: move selection down
* `CTRL-k`: move selection up
* `CTRL-h`: go to previous directory
* `CTRL-l`: go to selected directory
* `CTRL-r`: select currently selected item
* `CTRL-t`: select current directory
* `CTRL-u`: clear prompt
* `<Esc>`: exit fuzzyterm

Options
-------

* `-h, --help`
    * show this help message and exit
* `-c COMMAND, --command COMMAND`
    * command to run
    * defaults to: `echo`
* `-t OPTIONS, --options OPTIONS`
    * options for COMMAND
* `-o OUTPUT, --output OUTPUT`
    * redirect COMMAND stdout to OUTPUT
* `-p PATH, --path PATH`
    * starting path
    * defaults to current directory
* `-b, --background`
    * run COMMAND in background (`&`)
