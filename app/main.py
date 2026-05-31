from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from rich.panel import Panel

from app.routers import research, reports
from app.services.job_service import init_db
from app.utils.logger import console, get_logger

load_dotenv()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    console.print(
        Panel(
            "[bold green]Autonomous AI Research System[/bold green]\n"
            "[white]API Docs:[/white] http://localhost:8000/docs\n"
            "[white]Status:[/white] Running",
            border_style="green",
        )
    )
    yield
    # Shutdown
    logger.info("Shutting down.")


app = FastAPI(
    title="Autonomous AI Research System",
    description="Multi-agent AI research and report generation.",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(research.router)
app.include_router(reports.router)


@app.get("/")
async def root():
    return {
        "system": "Autonomous AI Research System",
        "version": "2.0.0",
        "docs": "/docs",
        "status": "running",
    }
