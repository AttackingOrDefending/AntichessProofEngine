import logging
import signal
import threading
import read_proof_files

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class XBoardEngine:
    def __init__(self, ENGINE=5):
        self.ENGINE = ENGINE
        self.isready = False
        self.executable = "PARSE_WIN.exe"
        self.file = "e3wins.rev4"
        self.show_refutations = False
        self.engine = None
        self.moves = []
        self.ponder_move = None
        self.engine = None
        self.command = ""
        self.stack = []
        self.search_thread = None
        self.receive_thread = None
        self.start()

    def recv(self):
        if self.stack:
            command = self.stack.pop()
        else:
            command = input()
        self.command = command

    def start(self):
        show_thinking = False
        forced = False
        self.stack = []
        self.receive_thread = threading.Thread(target=self.recv)
        self.receive_thread.start()
        while True:
            command = ""
            if self.receive_thread and not self.receive_thread.is_alive():
                self.receive_thread = None
                command = self.command
                self.receive_thread = threading.Thread(target=self.recv)
                self.receive_thread.start()

            if self.search_thread and not self.search_thread.is_alive():
                self.search_thread = None

                output = self.engine.best_move, self.engine.ponder_move

                move = output[0]
                self.ponder_move = output[1]

                if show_thinking:
                    info = self.engine.info
                    line = info[0]
                    print("0 {} 0 0 {} {}".format(line["cp"], line["move"], line["refutation"]), flush=True)

                print('move {}'.format(move))
                self.moves.append(move)

            if command == 'quit':
                if self.search_thread and self.search_thread.is_alive():
                    self.search_thread.join()
                break

            elif command == 'protover 2':
                print('feature done=0')
                print('feature myname="AntichessProofEngine"')
                print('feature usermove=1')
                # Note, because of a bug in Lichess, it may be necessary to
                # set setboard=0 when using Sunfish on the server.
                print('feature setboard=1')
                print('feature ping=1')
                print('feature sigint=0')
                print('feature nps=0')
                print('feature variants="normal"')
                print('feature option="executable -string PARSE_WIN.exe"')
                print('feature option="file -string e3wins.rev4"')
                print('feature done=1')

            elif command == 'new':
                if not self.engine:
                    self.engine = read_proof_files.Engine(executable=self.executable, file=self.file, ENGINE=self.ENGINE)
                self.stack.append('setboard ' + "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

            elif command.startswith('setboard'):
                self.moves = []

            elif command == 'force':
                forced = True

            elif command.startswith('option'):
                _, option = command.split(maxsplit=1)
                if '=' in option:
                    name, val = option.split('=')
                else:
                    name, val = option, True
                if name == 'executable':
                    self.executable = val
                if name == 'file':
                    self.file = val

            elif command == 'go':
                forced = False
                self.ponder_move = None
                self.search_thread = threading.Thread(target=self.engine.go, args=(self.moves,))
                self.search_thread.start()

            elif command.startswith('ping'):
                _, N = command.split()
                print('pong', N)

            elif command.startswith('usermove'):
                _, move = command.split()
                self.moves.append(move)
                if not forced:
                    self.stack.append('go')

            elif command.startswith('time'):
                pass

            elif command.startswith('otim'):
                pass

            elif command.startswith('perft'):
                pass

            elif command.startswith('post'):
                show_thinking = True

            elif command.startswith('nopost'):
                show_thinking = False

            elif any(command.startswith(x) for x in ('xboard', 'random', 'hard', 'accepted', 'level', 'easy', 'st', 'result', '?', 'name', 'rating')):
                print('# Ignoring command {}.'.format(command))

            elif command.startswith('reject'):
                _, feature = command.split()[:2]  # split(maxsplit=2) doesnt work in python2.7
                if feature == 'sigint':
                    signal.signal(signal.SIGINT, signal.SIG_IGN)
                print('# Warning ({} rejected): Might not work as expected.'.format(feature))

            else:
                print('# Warning (unkown command): {}. Treating as move.'.format(command))
                self.stack.append('usermove {}'.format(command))
