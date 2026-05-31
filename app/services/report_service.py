import os
import aiofiles
from datetime import datetime, timezone
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class ReportService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def generate_report(self , query: str , research_data: list[dict]) -> str:
        """Generate a research report using OpenAI based on query"""

        #Compile research data 
        context = self._compile_context(research_data)

        prompt = f"""
        "You are a professional research analyst.
        Based on the following research data, write a 
        comprehensive, well-structured market research report.

        RESEARCH QUERY: {query}
        RESEARCH DATA:{context}
        Generate a report with the following structure:
        # [Report Title]
        ## Executive Summary
        ## Key Findings
        ## Market Analysis
        # Competitive Landscape
        ## Data & Statistics
        ## Conclusions & Recommendations
        ## Sources
        Use professional language. Include specific data points where available.
        Format in clean Markdown."""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt},
            ],
            max_tokens=4000,
            temperature=0.3
        )

        return response.choices[0].message.content
    
    def _compile_context(self , results: list[dict]) -> str:
        """compile research results into a structured context for OpenAI
        """

        context_parts = []
        for i , r in enumerate(results[:8] , 1) : #Limit to top 8 results
            context_parts.append(
                f"[source {i}]{r['title']}\nURL : {r['url']}\n{r['content'][:1500]}\n"
            )
        return "\n---\n".join(context_parts)
        
    async def save_report(self , job_id: str , report_content: str) -> str:
        """Save generated report to a file and return file path"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        filename =  f"reports/report_{job_id[:8]}_{timestamp}.md"
        # Ensure reports directory exists
        os.makedirs("reports", exist_ok=True)

        async with aiofiles.open(filename, "w") as f:
            await f.write(report_content)

        return filename