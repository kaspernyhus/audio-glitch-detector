import time
import random
from threading import Event, Thread, Lock
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.panel import Panel


class RichOutput:
    def __init__(self):
        self.console = Console()
        self.start_time = time.time()
        self.count = 0
        self.lock = Lock()
        self.running = True
        self.elapsed_time = "00:00:00"
        self.vol = [0, 0]

    def _format_time(self, seconds) -> str:
        """Format elapsed time into HH:MM:SS."""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def _get_elapsed_time(self) -> str:
        """Get the elapsed time in HH:MM:SS format."""
        elapsed = time.time() - self.start_time
        elapsed_formatted = self._format_time(elapsed)
        return elapsed_formatted

    def header(self, header_str: str) -> None:
        """Print the program header."""
        header = Panel(Text(header_str, justify="center"), style="bold white")
        self.console.print(header)

    def log(self, log_str: str) -> None:
        """Print a log message."""
        with self.lock:
            self.console.log(log_str)

    def increment(self, count: int) -> None:
        self.log(f"Incrementing count by {count}")
        with self.lock:
            self.count += count

    def reset(self) -> None:
        with self.lock:
            self.count = 0
        self.start_time = time.time()

    def start(self) -> None:
        self.start_time = time.time()
        self.running = True

    def stop(self) -> None:
        self.running = False

    def is_running(self) -> bool:
        return self.running

    def _update_output(self, vol1, vol2):
        text1 = Text(f"{vol1}.0dB\n{vol2}.0dB", justify="left")
        return Panel(text1, title="Volume", style="bold white")

    def _run_live_output(self, exit_event: Event) -> None:
        with Live(self._update_output(self.vol[0], self.vol[1]), console=self.console, auto_refresh=False) as live:
            while True:
                self.vol[0] = -random.randint(0, 100)
                self.vol[1] = -random.randint(0, 100)
                live.update(self._update_output(self.vol[0], self.vol[1]))
                live.refresh()
                if exit_event.is_set():
                    break
                time.sleep(0.1)

    def live_output_start(self, exit_event: Event) -> None:
        thread = Thread(target=self._run_live_output, args=(exit_event,))
        thread.start()
