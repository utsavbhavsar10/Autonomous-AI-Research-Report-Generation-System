import os
from crewai import Agent, LLM
from dotenv import load_dotenv

from app.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)


def _llm() -> LLM:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not found in environment")
        raise ValueError("OPENAI_API_KEY is required")

    return LLM(
        model="gpt-4o-mini",
        temperature=0.3,
        api_key=api_key,
    )


def researcher_agent() -> Agent:
    """Senior Research Analyst — extracts verifiable facts from web sources."""
    return Agent(
        role="Senior Research Analyst",
        goal=(
            "Surface the most relevant, verifiable facts from a list of web "
            "search results. Skip marketing fluff and opinions."
        ),
        backstory=(
            "You spent a decade at a Big Four consultancy reading 200 sources "
            "to write a single 5-page briefing. You are allergic to vague claims "
            "and never let a fact through without a [n] citation back to its source."
        ),
        llm=_llm(),
        verbose=True, #Show detailed logs of what the agents are doing while crew is running
        allow_delegation=False,
    )


def analyst_agent() -> Agent:
    """Strategy Analyst — groups raw facts into themes, patterns, and gaps."""
    return Agent(
        role="Strategy Analyst",
        goal=(
            "Group raw facts into 3-5 themes. Identify patterns, contradictions, "
            "and gaps. Output structured bullets the writer can lift directly."
        ),
        backstory=(
            "You translate raw research into executive-ready themes. "
            "You always cite the underlying facts by their [n] references "
            "and call out contradictions instead of papering over them."
        ),
        llm=_llm(),
        verbose=True,
        allow_delegation=False,
    )


def writer_agent() -> Agent:
    """Technical Writer — drafts the full markdown report from analyzed themes."""
    return Agent(
        role="Technical Writer",
        goal=(
            "Turn analyzed themes into a polished markdown research report "
            "with Executive Summary, Key Findings, Detailed Analysis, "
            "Conclusions, and Sources sections."
        ),
        backstory=(
            "You write for senior engineers and product leaders. "
            "Clear, neutral, well-cited prose. No filler, no apologies. "
            "Every claim keeps its [n] citation from the analyst's bullets."
        ),
        llm=_llm(),
        verbose=True,
        allow_delegation=False,
    )


def reviewer_agent() -> Agent:
    """Editor-in-Chief — critiques the draft and returns the final polished markdown."""
    return Agent(
        role="Editor-in-Chief",
        goal=(
            "Read the draft, flag missing citations, vague claims, or weak "
            "structure, and return a polished final version of the markdown report."
        ),
        backstory=(
            "You reject anything that wouldn't pass a McKinsey QC review. "
            "If the draft is good, you make small edits. If it's bad, you rewrite it. "
            "You always return the FINAL polished markdown, never a critique."
        ),
        llm=_llm(),
        verbose=True,
        allow_delegation=False,
    )
