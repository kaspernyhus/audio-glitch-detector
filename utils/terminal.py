import sys, tty, termios, time, os
from threading import Thread, Event


class Terminal:
    def __init__(self):
        self.fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(self.fd)
        self.thread = None

    def __enter__(self):
        tty.setraw(sys.stdin.fileno())
        return self

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

    def getch(self):
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
        return ch

    def puts(self, string):
        tty.setraw(sys.stdout.fileno())
        sys.stdout.write(string)
        sys.stdout.write("\r\n")
        sys.stdout.flush()


def listen_for_keys(on_key, on_exit, exit_event):
    with terminal as term:
        while True:
            ch = term.getch()
            if ch == "q":
                on_exit()
                exit_event.set()
                break
            on_key(ch)


if __name__ == "__main__":

    exit_event = Event()

    def on_key(key):
        print(f"Key: {key}")

    def on_exit():
        print("Exiting")
        exit_event.set()

    terminal = Terminal()

    thread = Thread(target=listen_for_keys, args=(on_key, on_exit, exit_event))
    thread.start()

    while True:
        time.sleep(1)
        if exit_event.is_set():
            break
        terminal.puts("Hello")
        terminal.puts("worldddsdsadsads")
