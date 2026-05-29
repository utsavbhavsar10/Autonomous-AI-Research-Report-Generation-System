""""
HTTPX is a next-generation, fully featured HTTP 
client for Python 3. It serves as a modern, upgraded 
alternative to the traditional requests library, 
featuring built-in support for both synchronous 
and asynchronous APIs, HTTP/2, and type hints.
"""
import httpx
import os 
from datetime import datetime, timezone

async def trigger_n8n_workflow(payload: dict) -> dict:
    """Send data to n8n webhook and return response through payload"""
    webhook_url = os.getenv("N8N_WEBHOOK_URL")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                webhook_url,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()  # Raise an error for bad responses
            return {"success": True, "status_code": response.status_code}
        except httpx.RequestError as e:
            return {"success": False, "error": str(e)}
        
def build_research_payload(job_id : str , query: str , depth: str) -> dict:
    """Build payload to send n8n """
    return {
        "job_id": job_id,
        "query": query,
        "depth": depth,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "ai-research-system"

    }
