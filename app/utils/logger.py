import logging
from rich.logging import RichHandler
from rich.console import Console

console = Console()

_configured = False


def get_logger(name: str) -> logging.Logger:
    """Return a Rich-formatted logger. Configures the root handler once."""
    global _configured
    if not _configured:
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)],
        )
        _configured = True
    return logging.getLogger(name)
