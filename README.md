# AntichessProofEngine

AntichessProofEngine is an antichess engine for windows that plays perfectly. It supports both UCI and XBoard.

## How it works

The engine reads proof files for Antichess and plays the best move.
There are also wrappers for UCI and XBoard.

## Prerequisites

The engine requires PARSE_WIN.exe, which can be found [here](http://magma.maths.usyd.edu.au/~watkins/LOSING_CHESS/), by downloading LOSING_CHESS64.rar.
It also requires proof files, which can be found [here](http://magma.maths.usyd.edu.au/~watkins/LOSING_CHESS/) and [here](http://magma.maths.usyd.edu.au/~watkins/LOSING_CHESS/revision.html). The default proof file is e3wins.rev4.

## Acknowledgements
Thanks to [fishnet](https://github.com/lichess-org/fishnet/tree/ebd2a5e16d37135509cbfbff9998e0b798866ef5) which was modified to be able to communicate with PARSE_WIN.exe.
