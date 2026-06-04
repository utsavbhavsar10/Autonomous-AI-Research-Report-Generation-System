import asyncio
import os
from datetime import datetime, timezone

import aiofiles
import markdown as md_lib
from playwright.async_api import async_playwright
from app.utils.logger import get_logger

logger = get_logger(__name__)


# Print stylesheet: cover-style title page, page numbers, citation-friendly typography.
_PRINT_CSS = """
body {
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: 11pt;
    line-height: 1.55;
    color: #1f2328;
}

h1 {
    font-family: 'Helvetica', 'Arial', sans-serif;
    font-size: 26pt;
    color: #0d1117;
    border-bottom: 2px solid #0969da;
    padding-bottom: 8px;
    margin-top: 0;
    page-break-after: avoid;
}

h2 {
    font-family: 'Helvetica', 'Arial', sans-serif;
    font-size: 17pt;
    color: #0d1117;
    margin-top: 22px;
    border-bottom: 1px solid #d0d7de;
    padding-bottom: 4px;
    page-break-after: avoid;
}

h3 {
    font-family: 'Helvetica', 'Arial', sans-serif;
    font-size: 13pt;
    color: #24292f;
    margin-top: 16px;
    page-break-after: avoid;
}

p, li {
    text-align: justify;
    orphans: 3;
    widows: 3;
}

ul, ol { padding-left: 22px; }

code {
    font-family: 'Consolas', 'Courier New', monospace;
    background: #f6f8fa;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 9.5pt;
}

pre {
    background: #f6f8fa;
    padding: 10px 12px;
    border-radius: 4px;
    font-size: 9.5pt;
    overflow-x: auto;
    page-break-inside: avoid;
}

blockquote {
    border-left: 3px solid #0969da;
    padding-left: 12px;
    color: #57606a;
    margin: 12px 0;
}

a { color: #0969da; text-decoration: none; word-wrap: break-word; }

table {
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    font-size: 10pt;
    page-break-inside: avoid;
}
th, td {
    border: 1px solid #d0d7de;
    padding: 6px 10px;
    text-align: left;
}
th { background: #f6f8fa; }

.report-meta {
    color: #57606a;
    font-size: 9pt;
    margin: 4px 0 24px 0;
    font-family: 'Helvetica', 'Arial', sans-serif;
}
"""


def _md_to_html(markdown_text: str, title: str = "Research Report") -> str:
    """Render markdown to a full HTML document ready for Playwright."""
    body_html = md_lib.markdown(
        markdown_text,
        extensions=["extra", "tables", "fenced_code", "toc", "sane_lists"],
    )
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return (
        f"<!DOCTYPE html>"
        f"<html lang='en'><head><meta charset='utf-8'>"
        f"<title>{title}</title>"
        f"<style>{_PRINT_CSS}</style>"
        f"</head><body>"
        f"<div class='report-meta'>Generated {generated_at}</div>"
        f"{body_html}"
        f"</body></html>"
    )


async def generate_pdf(markdown_text: str, output_path: str, title: str = "Research Report") -> str:
    """Async wrapper: render markdown to a PDF file using Playwright."""
    logger.info(f"Generating PDF -> {output_path}")
    html_doc = _md_to_html(markdown_text, title=title)
    
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_doc)
        await page.pdf(
            path=output_path,
            format="A4",
            margin={"top": "22mm", "right": "18mm", "bottom": "24mm", "left": "18mm"},
            display_header_footer=True,
            header_template="<span></span>",
            footer_template="""
            <div style="font-size: 9pt; font-family: Helvetica, Arial, sans-serif; color: #888; width: 100%; display: flex; justify-content: space-between; padding: 0 18mm;">
                <span>Autonomous AI Research Report</span>
                <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
            </div>
            """
        )
        await browser.close()
        
    size = os.path.getsize(output_path)
    logger.info(f"PDF saved: {output_path} ({size} bytes)")
    return output_path


def _sync_generate_pdf(markdown_text: str, output_path: str, title: str):
    """Run generate_pdf in a separate thread-bound ProactorEventLoop on Windows."""
    import sys
    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(generate_pdf(markdown_text, output_path, title=title))
    finally:
        loop.close()


async def md_path_to_pdf_path(md_path: str, title: str = "Research Report") -> str:
    """Read an existing .md file, write a sibling .pdf, return its path."""
    async with aiofiles.open(md_path, "r", encoding="utf-8") as f:
        markdown_text = await f.read()
    pdf_path = os.path.splitext(md_path)[0] + ".pdf"
    
    # Run in a thread-isolated ProactorEventLoop to avoid Uvicorn's SelectorEventLoop override
    return await asyncio.to_thread(
        _sync_generate_pdf,
        markdown_text,
        pdf_path,
        title
    )
