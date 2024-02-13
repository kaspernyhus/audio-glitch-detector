import time
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
        self.console.log(log_str)

    def increment(self, count: int) -> None:
        self.log(f"Incrementing count by {count}")
        with self.lock:
            self.count += count

    def _update_output(self) -> None:
        elapsed = self._get_elapsed_time()
        with self.lock:
            text_obj = Text(f"Elapsed time: {elapsed} seconds\nDetected discontinuities: {self.count}", style="bold")
        return text_obj

    def _run_live_output(self, exit_event: Event) -> None:
        with Live(self._update_output(), console=self.console, refresh_per_second=10) as live:
            while True:
                live.update(self._update_output())
                if exit_event.is_set():
                    break

    def live_output_start(self, exit_event: Event) -> None:
        thread = Thread(target=self._run_live_output, args=(exit_event,))
        thread.start()
