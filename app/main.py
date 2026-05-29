from fastapi import FastAPI
from dotenv import load_dotenv
from app.routers import research_route
load_dotenv()

app = FastAPI(
    title="Autonomous AI Research System",
    description="AI-powered research and report generation API",
    version="0.1.0"
)
app.include_router(research_route.router)


@app.get("/")
async def root():
  return {"message": "Autonomous AI Research System is running."}