import json
import aiofiles
from datetime import datetime, timezone
from rich.console import Console
from rich.panel import Panel

from app.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()
LOG_FILE = "jobs_log.json"


class NotificationService:
    """
    Handles all event notifications without n8n.
    Logs to file + Rich terminal output.
    """

    async def job_started(self, job_id: str, query: str, depth: str):
        console.print(
            Panel(
                f"[bold cyan]Research Job Started[/bold cyan]\n"
                f"[white]Job ID:[/white] {job_id}\n"
                f"[white]Query:[/white] {query[:80]}\n"
                f"[white]Depth:[/white] {depth}",
                title="[bold]AI Research System[/bold]",
                border_style="cyan",
            )
        )
        await self._log_event("job_started", job_id, query=query, depth=depth)

    async def job_complete(
        self,
        job_id: str,
        query: str,
        report_path: str,
        sources_count: int,
        duration: float,
    ):
        console.print(
            Panel(
                f"[bold green]Report Generated Successfully[/bold green]\n"
                f"[white]Job ID:[/white] {job_id}\n"
                f"[white]Query:[/white] {query[:80]}\n"
                f"[white]Report:[/white] {report_path}\n"
                f"[white]Sources:[/white] {sources_count}\n"
                f"[white]Duration:[/white] {duration:.1f}s",
                title="[bold]Research Complete[/bold]",
                border_style="green",
            )
        )
        await self._log_event(
            "job_complete",
            job_id,
            query=query,
            report_path=report_path,
            sources_count=sources_count,
            duration=duration,
        )

    async def job_failed(self, job_id: str, query: str, error: str):
        console.print(
            Panel(
                f"[bold red]Research Job Failed[/bold red]\n"
                f"[white]Job ID:[/white] {job_id}\n"
                f"[white]Query:[/white] {query[:80]}\n"
                f"[white]Error:[/white] {error}",
                title="[bold]Job Failed[/bold]",
                border_style="red",
            )
        )
        await self._log_event("job_failed", job_id, query=query, error=error)

    async def step_update(self, job_id: str, step: str, message: str):
        console.print(f"  [dim]→[/dim] [yellow]{step}[/yellow]: {message}")
        await self._log_event("step_update", job_id, step=step, message=message)

    async def _log_event(self, event: str, job_id: str, **kwargs):
        entry = {
            "event": event,
            "job_id": job_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **kwargs,
        }
        async with aiofiles.open(LOG_FILE, "a", encoding="utf-8") as f:
            await f.write(json.dumps(entry) + "\n")
