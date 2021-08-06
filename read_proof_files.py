import subprocess
import os
import signal
import logging
import threading

import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Engine:
    def __init__(self, executable="PARSE_WIN.exe", file="e3wins.rev4", ENGINE=5):
        self.ENGINE = ENGINE
        command = subprocess.list2cmdline([executable, file])
        self.p = self.open_process(command)
        self.init()
        self.info = []
        self.best_move = None
        self.ponder_move = None

    def open_process(self, command, cwd=None, shell=True, _popen_lock=threading.Lock()):
        kwargs = {
            "shell": shell,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.STDOUT,
            "stdin": subprocess.PIPE,
            "bufsize": 1,  # Line buffered
            "universal_newlines": True,
        }

        if cwd is not None:
            kwargs["cwd"] = cwd

        # Prevent signal propagation from parent process
        try:
            # Windows
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        except AttributeError:
            # Unix
            kwargs["preexec_fn"] = os.setpgrp

        with _popen_lock:  # Work around Python 2 Popen race condition
            return subprocess.Popen(command, **kwargs)

    def kill_process(self):
        try:
            # Windows
            self.p.send_signal(signal.CTRL_BREAK_EVENT)
        except AttributeError:
            # Unix
            os.killpg(self.p.pid, signal.SIGKILL)

        self.p.communicate()

    def send(self, line):
        logging.debug(f"{self.ENGINE} %s << %s {self.p.pid} {line}")
        self.p.stdin.write(line + "\n")
        self.p.stdin.flush()

    def recv(self):
        while True:
            line = self.p.stdout.readline()
            print(line)
            if line == "":
                raise EOFError()

            line = line.rstrip()

            logging.debug(f"{self.ENGINE} %s >> %s {self.p.pid} {line}")

            if line:
                return line

    def init(self):
        while True:
            command = self.recv()
            if command == "Ready for input":
                break

    def go(self, moves):
        # time.sleep(10)

        self.send(f"query {' '.join(moves)}")

        received_val = False
        best_move, ponder_move = None, None
        self.info = []

        while True:
            command = self.recv()
            if command == "QUERY COMPLETE":
                self.best_move = best_move
                self.ponder_move = ponder_move
                return best_move, ponder_move
            elif command == "No children":
                best_move, ponder_move = None, None
            elif command.startswith("Val: "):
                received_val = True
            else:
                command = command.split()
                move = command[0]
                size = command[1]
                percentage = command[2]
                refutation = command[3]
                if refutation == "---":
                    refutation = None
                self.info.append({"move": move, "size": size, "percentage": percentage, "refutation": refutation})
                if received_val:
                    best_move = move
                    ponder_move = refutation
                    received_val = False

    def quit(self):
        self.send("quit")
