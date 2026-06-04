import asyncio

from crewai import Crew, Process

from app.crew.agents import (
    analyst_agent,
    researcher_agent,
    reviewer_agent,
    writer_agent,
)
from app.crew.tasks import (
    analysis_task,
    research_task,
    review_task,
    writing_task,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


def build_research_crew() -> Crew:
    """Wire the 4 agents and 4 tasks into a sequential crew."""
    researcher = researcher_agent()
    analyst = analyst_agent()
    writer = writer_agent()
    reviewer = reviewer_agent()

    return Crew(
        agents=[researcher, analyst, writer, reviewer],
        tasks=[
            research_task(researcher),
            analysis_task(analyst),
            writing_task(writer),
            review_task(reviewer),
        ],
        process=Process.sequential,
        verbose=True,
    )


def _format_sources(sources: list[dict]) -> str:
    """Render the source list as a single string for prompt injection."""
    lines: list[str] = []
    for i, s in enumerate(sources[:25]):
        title = s.get("title", "?")
        url = s.get("url", "?")
        snippet = s.get("content", s.get("snippet", "")) or ""
        snippet = snippet[:400].replace("\n", " ")
        lines.append(f"[{i + 1}] {title} - {url}\n    {snippet}")
    return "\n".join(lines)


async def run_crew(query: str, sources: list[dict]) -> str:
    """Run the research crew and return the final markdown report."""
    crew = build_research_crew()
    formatted_sources = _format_sources(sources)

    logger.info(
        f"Kicking off crew | query={query[:80]!r} | sources={len(sources)}"
    )

    # crew.kickoff is synchronous — run it off the event loop so FastAPI
    # request handlers don't block.
    result = await asyncio.to_thread(
        crew.kickoff,
        inputs={"query": query, "sources": formatted_sources},
    )

    markdown = getattr(result, "raw", None) or str(result)
    logger.info(f"Crew finished | output_chars={len(markdown)}")
    return markdown

