import os
import aiofiles
from datetime import datetime, timezone
from openai import AsyncOpenAI
from dotenv import load_dotenv
from app.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)


class ReportService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment")
            raise ValueError("OPENAI_API_KEY is required")

        self.client = AsyncOpenAI(api_key=api_key)
        logger.info("ReportService initialized with OpenAI API")

    async def generate_report(self, query: str, research_data: list[dict]) -> str:
        """Generate a professional research report.

        When USE_CREW=true (default) the CrewAI multi-agent pipeline drafts the
        report. Set USE_CREW=false to fall back to the Day 3 single OpenAI call.
        """

        if not research_data:
            logger.warning("No research data provided for report generation")
            return self._generate_empty_report(query)

        if os.getenv("USE_CREW", "true").lower() == "true":
            from app.crew.crew import run_crew
            logger.info(
                f"Delegating report generation to CrewAI | query={query!r} | "
                f"sources={len(research_data)}"
            )
            return await run_crew(query, research_data)

        context = self._compile_context(research_data)
        logger.info(f"Generating report for query: '{query}' with {len(research_data)} sources")

        prompt = f"""You are a professional research analyst. Based on the following search results, generate a comprehensive, well-structured research report.

RESEARCH QUERY: {query}

SEARCH RESULTS:
{context}

Generate a professional markdown report with the following structure:

# [Descriptive Report Title]

## Executive Summary
Provide a 2-3 paragraph overview of the key findings and insights.

## Key Findings
- List 5-7 bullet points highlighting the most important discoveries
- Each finding should be specific and actionable

## Detailed Analysis
Organize findings into logical sections with subheadings. Provide in-depth analysis with:
- Specific data points and statistics
- Trends and patterns
- Comparisons and contrasts
- Expert insights from the sources

## Conclusions & Recommendations
Summarize the main takeaways and provide actionable recommendations.

## Sources
List all sources as numbered references:
[1] Title - URL
[2] Title - URL
etc.

Requirements:
- Use professional, clear language
- Cite sources inline using [1], [2] notation
- Include specific data points where available
- Ensure all claims are backed by the provided sources
- Format in clean, readable Markdown"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional research analyst who writes comprehensive, well-cited reports."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.3
            )

            report_content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            logger.info(f"Report generated successfully ({tokens_used} tokens used)")

            return report_content

        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            raise

    def _compile_context(self, results: list[dict]) -> str:
        """Compile research results into structured context for LLM"""

        context_parts = []
        for i, r in enumerate(results[:10], 1):
            title = r.get('title', 'Untitled')
            url = r.get('url', 'No URL')
            content = r.get('content', '')[:2000]
            answer = r.get('answer', '')

            source_text = f"[Source {i}] {title}\nURL: {url}\n"
            if answer:
                source_text += f"Summary: {answer}\n"
            source_text += f"Content: {content}\n"

            context_parts.append(source_text)

        return "\n---\n".join(context_parts)

    def _generate_empty_report(self, query: str) -> str:
        """Generate a report when no research data is available"""
        return f"""# Research Report: {query}

## Executive Summary
No research data was available to generate this report. The search may have failed or returned no results.

## Recommendations
- Verify the search query is correctly formatted
- Check API connectivity and rate limits
- Try a different or more specific search query

## Status
Report generation incomplete due to lack of source data.
"""

    async def save_report(self, job_id: str, report_content: str) -> str:
        """Save generated report to disk and return file path"""
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            filename = f"reports/report_{job_id[:8]}_{timestamp}.md"

            os.makedirs("reports", exist_ok=True)

            async with aiofiles.open(filename, "w", encoding="utf-8") as f:
                await f.write(report_content)

            file_size = len(report_content.encode('utf-8'))
            logger.info(f"Report saved: {filename} ({file_size} bytes)")

            return filename

        except Exception as e:
            logger.error(f"Failed to save report: {str(e)}")
            raise