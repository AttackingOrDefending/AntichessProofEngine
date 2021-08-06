import logging
import read_proof_files
import threading

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class UCIEngine:
    def __init__(self, ENGINE=5):
        self.ENGINE = ENGINE
        self.isready = False
        self.executable = "PARSE_WIN.exe"
        self.file = "easy12.done"  # "e3wins.rev4"
        self.show_refutations = False
        self.engine = None
        self.moves = ""
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
                info = self.engine.info
                multipv = 1
                for line in info:
                    refutation = line["refutation"]
                    if refutation:
                        if self.show_refutations:
                            print("info multipv {} pv {} {} refutation {}".format(multipv, line["move"], refutation,
                                                                                  refutation), flush=True)
                        else:
                            print("info multipv {} pv {} {}".format(multipv, line["move"], refutation), flush=True)
                    else:
                        print("info multipv {} pv {}".format(multipv, line["move"]), flush=True)
                    multipv += 1

                if output[1] is not None:
                    print("bestmove {} ponder {}".format(output[0], output[1]), flush=True)
                else:
                    print("bestmove {}".format(output[0]), flush=True)

            if command == "quit":
                if self.search_thread and self.search_thread.is_alive():
                    self.search_thread.join()
                self.engine.quit()
                self.engine.kill_process()
                break

            elif command == "stop":
                pass

            elif command.startswith("setoption"):
                if self.isready:
                    continue
                args = command.split()
                name = args[2]
                try:
                    value = args[4]
                except IndexError:
                    value = None
                if name == "executable":
                    self.executable = value
                elif name == "file":
                    self.file = value
                elif name == "UCI_ShowRefutations":
                    self.show_refutations = True

            elif command.startswith("isready"):
                if not self.isready:
                    self.engine = read_proof_files.Engine(executable=self.executable, file=self.file, ENGINE=self.ENGINE)
                    self.isready = True
                print("readyok", flush=True)

            elif command == "uci":
                print('id name AntichessProofEngine', flush=True)
                print('id author AttackingOrDefending', flush=True)

                print("option name executable type string default PARSE_WIN.exe", flush=True)
                print("option name file type string default e3wins.rev4", flush=True)
                print("option name UCI_ShowRefutations type check default false", flush=True)

                print("uciok", flush=True)

            elif command == "ucinewgame":
                self.stack.append("position startpos")

            elif command.startswith("position"):
                args = command.split()
                if args[1] == "startpos" or len(args) >= 3 and args[2] == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1":
                    if "moves" in args:
                        self.moves = args[args.index("moves") + 1:]
                    else:
                        self.moves = ""

            elif command.startswith("go"):
                if command.split()[1] == "ponder":
                    continue
                self.search_thread = threading.Thread(target=self.engine.go, args=(self.moves,))
                self.search_thread.start()


UCIEngine()
