import sys, tty, termios


class KeyboardInput:
    def __init__(self):
        self.fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(self.fd)

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


if __name__ == "__main__":
    with KeyboardInput() as keys:
        print("Press any key (CTRL+C to exit)")
        while True:
            key = keys.getch()
            print(f"Key pressed: {key}")
            if key == "q":
                break
