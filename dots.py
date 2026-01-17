"""Simple utility for printing progress dots."""
import time


class Dots:
    """Utility for printing progress dots."""

    def __init__(self, total=None, width=80, msg=None):
        self.total = total
        self.width = width
        self.column = 0
        self.timestamps = []
        if msg:
            print(msg, end='', flush=True)
            self.column = len(msg)

    def dot(self, char='.'):
        """Print a single character without a newline."""
        self._clear_eta()
        self.timestamps.append(time.time())
        print(char, end='', flush=True)
        self.column += 1
        if self.column >= self.width:
            print()
            self.column = 0
        self._print_eta()

    def _print_eta(self):
        """Print estimated time remaining if total is known."""
        if self.total is None or len(self.timestamps) < 2:
            self.last_eta_len = 0
            return
        avg = self.average_time()
        remaining = self.total - len(self.timestamps)
        eta_seconds = avg * remaining
        eta_str = f" {avg:.2f}s/dot, {eta_seconds:.0f}s remaining"
        self.last_eta_len = len(eta_str)
        print(eta_str, end='', flush=True)

    def _clear_eta(self):
        """Clear the previously printed ETA."""
        if hasattr(self, 'last_eta_len') and self.last_eta_len > 0:
            # Use ANSI escape to clear to end of line, then backspace over the ETA
            print(f'\x1b[{self.last_eta_len}D\x1b[K', end='', flush=True)
            self.last_eta_len = 0

    def done(self, message='done'):
        """Print a completion message with a newline."""
        self._clear_eta()
        print(message)

    def average_time(self):
        """Return the average time between dots in seconds."""
        if len(self.timestamps) < 2:
            return 0
        total_time = self.timestamps[-1] - self.timestamps[0]
        return total_time / (len(self.timestamps) - 1)
