import re
from typing import List, Dict
from bs4 import BeautifulSoup
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ContentProcessor:
    """Process and clean search results for LLM consumption"""

    @staticmethod
    def process_search_results(results: List[Dict]) -> str:
        """Convert search results into structured text for LLM"""
        if not results:
            logger.warning("No search results to process")
            return ""

        processed_parts = []
        for i, result in enumerate(results, 1):
            title = ContentProcessor.clean_text(result.get('title', 'Untitled'))
            url = result.get('url', 'No URL')
            content = ContentProcessor.clean_text(result.get('content', ''))
            snippet = ContentProcessor.clean_text(result.get('snippet', ''))

            processed = f"[{i}] {title}\n"
            processed += f"URL: {url}\n"
            if snippet:
                processed += f"Snippet: {snippet}\n"
            if content:
                processed += f"Content: {content[:1500]}\n"

            processed_parts.append(processed)

        logger.info(f"Processed {len(processed_parts)} search results")
        return "\n---\n".join(processed_parts)

    @staticmethod
    def clean_text(text: str) -> str:
        """Remove HTML, normalize whitespace, and clean text"""
        if not text:
            return ""

        # Remove HTML tags
        text = BeautifulSoup(text, "html.parser").get_text()

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters that might confuse LLM
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

        # Trim
        text = text.strip()

        return text

    @staticmethod
    def extract_key_info(results: List[Dict]) -> Dict[str, any]:
        """Extract key information from search results"""
        if not results:
            return {
                "total_sources": 0,
                "unique_domains": [],
                "total_content_length": 0
            }

        unique_domains = set()
        total_length = 0

        for result in results:
            url = result.get('url', '')
            if url:
                domain = ContentProcessor._extract_domain(url)
                if domain:
                    unique_domains.add(domain)

            content = result.get('content', '')
            total_length += len(content)

        return {
            "total_sources": len(results),
            "unique_domains": list(unique_domains),
            "total_content_length": total_length,
            "avg_content_length": total_length // len(results) if results else 0
        }

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL"""
        try:
            match = re.search(r'https?://([^/]+)', url)
            return match.group(1) if match else ""
        except Exception:
            return ""

    @staticmethod
    def deduplicate_results(results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on URL"""
        seen_urls = set()
        unique_results = []

        for result in results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)

        if len(unique_results) < len(results):
            logger.info(f"Removed {len(results) - len(unique_results)} duplicate results")

        return unique_results

    @staticmethod
    def validate_result(result: Dict) -> bool:
        """Validate that a search result has required fields"""
        required_fields = ['title', 'url']
        return all(field in result and result[field] for field in required_fields)

    @staticmethod
    def filter_valid_results(results: List[Dict]) -> List[Dict]:
        """Filter out invalid or incomplete results"""
        valid_results = [r for r in results if ContentProcessor.validate_result(r)]

        if len(valid_results) < len(results):
            logger.warning(f"Filtered out {len(results) - len(valid_results)} invalid results")

        return valid_results
