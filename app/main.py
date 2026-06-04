import sys
import asyncio
    ## Configured Asynchronous event loop policy for windows 
    ## This is to avoid the error 'RuntimeError: Event loop is closed'
    ## which occurs when using asyncio.run()
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rich.panel import Panel

from app.routers import research, reports
from app.services.job_service import init_db
from app.utils.logger import console, get_logger
from app.utils.tracing import init_langsmith

load_dotenv()
init_langsmith()
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
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
