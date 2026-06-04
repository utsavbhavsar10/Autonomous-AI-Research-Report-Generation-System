from crewai import Task
from crewai.agent import Agent


##Placeholder replaces by crew.kickoff(inputs = {"query": query, "sources": sources})
def research_task(agent: Agent) -> Task:
    """Researcher pulls 15-25 verifiable facts from the raw sources, each cited [n]."""
    return Task(
        description=(
            "Topic: {query}\n\n"
            "Sources (each with index, title, url, snippet):\n{sources}\n\n"
            "Produce a markdown bullet list of the 15-25 most relevant facts about the topic. "
            "Rules:\n"
            "  - Skip marketing fluff, opinions, and vague claims.\n"
            "  - Prefer specific numbers, dates, names, and verifiable statements.\n"
            "  - Every bullet MUST end with a [n] citation referencing the source index "
            "    (e.g. [1], [2][4] for multi-source claims).\n"
            "  - Do NOT invent facts that are not supported by the sources."
        ),
        expected_output=(
            "A markdown bullet list of 15-25 cited facts. Example:\n"
            "- FastAPI is built on Starlette and Pydantic [1][3]\n"
            "- Average request latency is sub-10ms in benchmarks [2]"
        ),
        agent=agent,
    )


def analysis_task(agent: Agent) -> Task:
    """Analyst groups the researcher's bullets into 3-5 themes with citations + gaps."""
    return Task(
        description=(
            "Take the cited research bullets from the previous task and group them "
            "into 3-5 coherent themes about '{query}'.\n\n"
            "For each theme provide:\n"
            "  - A one-line summary as an H3 heading (### Theme name)\n"
            "  - 3-6 supporting bullets, each preserving its original [n] citations\n"
            "  - A short note on any contradictions between sources, if present\n\n"
            "At the end, add a section '### Gaps & Contradictions' listing:\n"
            "  - Questions the sources do NOT answer\n"
            "  - Any direct conflicts between sources (cite both [n] references)\n\n"
            "Do NOT drop or rewrite the [n] citations from the research bullets."
        ),
        expected_output=(
            "Markdown with an H3 heading per theme, cited bullets underneath, "
            "and a final '### Gaps & Contradictions' section."
        ),
        agent=agent,
    )


def writing_task(agent: Agent) -> Task:
    """Writer drafts the full markdown report from the analyst's themed output."""
    return Task(
        description=(
            "Using the themed analysis from the previous task, write the full "
            "research report on '{query}'.\n\n"
            "Required sections, in this exact order:\n"
            "  # [Title]\n"
            "  ## Executive Summary    (2-3 paragraphs, neutral tone, cited)\n"
            "  ## Key Findings         (5-7 bullets, each ending with a [n] citation)\n"
            "  ## Detailed Analysis    (one H3 per theme from the analyst's output)\n"
            "  ## Conclusions & Recommendations\n"
            "  ## Sources              (numbered list, format: [n] title - url)\n\n"
            "Rules:\n"
            "  - Preserve every [n] citation from the analyst's bullets.\n"
            "  - Do NOT invent facts; only use what was researched and analyzed.\n"
            "  - No filler phrases ('In conclusion, it is important to note...').\n"
            "  - The Sources section MUST list every [n] used in the body.\n\n"
            "Sources list to use for the Sources section:\n{sources}"
        ),
        expected_output=(
            "A complete markdown report with Title, Executive Summary, "
            "Key Findings, Detailed Analysis, Conclusions & Recommendations, "
            "and Sources sections — all citations preserved."
        ),
        agent=agent,
    )


def review_task(agent: Agent) -> Task:
    """Reviewer critiques the writer's draft and returns the final polished markdown."""
    return Task(
        description=(
            "Review the draft markdown report from the previous task. Check:\n"
            "  1. Every factual claim ends with a [n] citation\n"
            "  2. All required sections are present and non-empty "
            "(Title, Executive Summary, Key Findings, Detailed Analysis, "
            "Conclusions & Recommendations, Sources)\n"
            "  3. No filler phrases or vague hedging\n"
            "  4. The Sources section matches every [n] used in the body\n"
            "  5. Themes from the analyst survived into Detailed Analysis\n\n"
            "Apply your edits directly. Return the FINAL polished markdown "
            "report only — do NOT return a critique, a changelog, or commentary "
            "above or below the report."
        ),
        expected_output=(
            "The final, ready-to-publish markdown report. Starts with the "
            "'# [Title]' line and ends with the last source in the Sources list. "
            "No surrounding commentary."
        ),
        agent=agent,
    )
