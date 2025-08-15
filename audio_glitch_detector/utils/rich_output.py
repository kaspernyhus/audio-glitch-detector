import time
from collections.abc import Callable
from threading import Event, Lock, Thread

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class RichOutput:
    def __init__(self):
        self.console = Console()
        self.start_time = time.time()
        self.lock = Lock()
        self.running = True
        self.elapsed_time = "00:00:00"
        self.get_meter_data = None
        self.vol = [0, 0]

    def _format_time(self, seconds) -> str:
        """Format elapsed time into HH:MM:SS."""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def calc_elapsed_time(self) -> str:
        """Get the elapsed time in HH:MM:SS format."""
        elapsed = time.time() - self.start_time
        self.elapsed_time = self._format_time(elapsed)
        return self.elapsed_time

    def get_elapsed_time(self) -> str:
        """Get the elapsed time in HH:MM:SS format."""
        return self.elapsed_time

    def header(self, header_str: str) -> None:
        """Print the program header."""
        header = Panel(Text(header_str, justify="center"), style="bold white")
        self.console.print(header)

    def log(self, log_str: str, style: str = "") -> None:
        """Print a log message."""
        with self.lock:
            self.console.log(log_str, style=style)

    def reset(self) -> None:
        with self.lock:
            self.count = 0
        self.start_time = time.time()

    def start_timer(self) -> None:
        self.start_time = time.time()
        self.running = True

    def stop_timer(self) -> None:
        self.running = False

    def reset_timer(self) -> None:
        self.start_time = time.time()

    def update_volume_info(self, vol: list[int, int]) -> None:
        self.vol = vol

    def is_running(self) -> bool:
        return self.running

    def _update_output(self):
        table = Table.grid(expand=True)
        table.add_column(justify="left", ratio=1)
        table.add_column(justify="right", ratio=1)
        table.add_row(
            f"{self.vol[0]:.2f}dB\n{self.vol[1]:.2f}dB", f"{self.get_elapsed_time()}"
        )
        return Panel(table, title="Volume", style="bold white")

    def _run_live_output(self, exit_event: Event) -> None:
        with Live(
            self._update_output(), console=self.console, auto_refresh=False
        ) as live:
            while True:
                self.calc_elapsed_time()
                if self.get_meter_data:
                    self.update_volume_info(self.get_meter_data())
                live.update(self._update_output())
                live.refresh()
                if exit_event.is_set():
                    self.stop_timer()
                    break
                time.sleep(0.1)

    def live_output_start(
        self, exit_event: Event, get_meter_data: Callable = None
    ) -> None:
        self.get_meter_data = get_meter_data
        thread = Thread(target=self._run_live_output, args=(exit_event,))
        thread.start()
