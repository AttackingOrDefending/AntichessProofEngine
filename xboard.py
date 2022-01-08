import logging
import signal
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
        self.start()

    def start(self):
        show_thinking = False
        forced = False
        stack = []
        while True:
            if stack:
                command = stack.pop()
            else:
                command = input()
                print('>>>', command, flush=True)

            if command == 'quit':
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
                stack.append('setboard ' + "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

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
                output = self.engine.go(self.moves)
                move = output[0]
                self.ponder_move = output[1]

                if show_thinking:
                    info = self.engine.info
                    line = info[0]
                    print("0 {} 0 0 {} {}".format(line["cp"], line["move"], line["refutation"]), flush=True)

                print('move {}'.format(move))
                self.moves.append(move)

            elif command.startswith('ping'):
                _, N = command.split()
                print('pong', N)

            elif command.startswith('usermove'):
                _, move = command.split()
                self.moves.append(move)
                if not forced:
                    stack.append('go')

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
                stack.append('usermove {}'.format(command))
