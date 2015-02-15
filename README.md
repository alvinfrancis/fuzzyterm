fuzzyterm.py
============

Fuzzy incremental search on the terminal.

![fuzzyterm with vim](img/fuzzy-vim.gif)

Basic Usage
-----------

* Search for an item fuzzily and use item as an argument for COMMAND

        fuzzyterm -c COMMAND

### Keys

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
* `-l LENGTH, --length LENGTH`
    * maximum number of items displayed in list
* `-o OUTPUT, --output OUTPUT`
    * redirect COMMAND stdout to OUTPUT
* `-p PATH, --path PATH`
    * starting path
    * defaults to current directory
* `-b, --background`
    * run COMMAND in background (`&`)

Notes
-----
* Note that the command run by fuzzyterm is run as a subprocess. As such, it
  cannot directly affect the environment of the parent process.  Passing a
  command like `cd`, for example, will not change the directory. However,
  something like the following bash shell function could be used along with
  fuzzyterm as a workaround to such a limitation.
 
    ```bash
    # example function to use fuzzyterm to change directories
    function fcd {
        fcdpipe=/tmp/fcdfifo
        # create a named pipe
        if [[ ! -p $fcdpipe ]]; then
            mkfifo $fcdpipe
        fi

        # echo selection to named pipe
        # (process must be backgrounded or it will block)
        fuzzyterm.py --background --output $fcdpipe

        # check fuzzyterm exit code
        if [[ $? -ne 0 ]]; then
            rm $fcdpipe
        else
            # cd using the selection piped into the named pipe
            read directory <$fcdpipe
            cd "$directory"
        fi
    }
    ```
