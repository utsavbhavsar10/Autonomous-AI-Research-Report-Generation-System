"""LangSmith tracing setup for LangGraph and CrewAI.

LangGraph and LangChain pick up tracing automatically when the LANGSMITH_*
env vars are set, so this module mostly normalizes those vars and then
opportunistically wires CrewAI spans into the same LangSmith project via
OpenInference + OTLP.
"""

import os

from dotenv import load_dotenv

from app.utils.logger import get_logger

logger = get_logger(__name__)

_initialized = False

load_dotenv()  # Ensure env vars are loaded before we check them

def _ensure_langsmith_env() -> bool:
    """Mirror LANGSMITH_* into the LANGCHAIN_* vars older callers still read."""
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        logger.info("LANGSMITH_API_KEY not set — tracing disabled.")
        return False

    tracing = os.getenv("LANGSMITH_TRACING")
    project = os.getenv("LANGSMITH_PROJECT")
    endpoint = os.getenv("LANGSMITH_ENDPOINT")

    os.environ["LANGSMITH_TRACING"] = "true" if tracing else "false"
    os.environ["LANGSMITH_PROJECT"] = project
    os.environ["LANGSMITH_ENDPOINT"] = endpoint

    # Back-compat aliases — some LangChain versions still read these.
    os.environ["LANGCHAIN_TRACING_V2"] = "true" if tracing else "false"
    os.environ["LANGCHAIN_API_KEY"] = api_key
    os.environ["LANGCHAIN_PROJECT"] = project
    os.environ["LANGCHAIN_ENDPOINT"] = endpoint

    return tracing


def _instrument_crewai(project: str, api_key: str, endpoint: str) -> None:
    """Send CrewAI/OpenAI spans to LangSmith via OTLP, if the exporter is available."""
    try:
        from openinference.instrumentation.crewai import CrewAIInstrumentor
        from openinference.instrumentation.openai import OpenAIInstrumentor
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError as e:
        logger.info(
            f"CrewAI tracing skipped — install opentelemetry-exporter-otlp to enable ({e})."
        )
        return

    otlp_endpoint = endpoint.rstrip("/") + "/otel/v1/traces"
    resource = Resource.create({"service.name": project, "langsmith.project": project})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(
        endpoint=otlp_endpoint,
        headers={"x-api-key": api_key, "Langsmith-Project": project},
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    CrewAIInstrumentor().instrument(tracer_provider=provider)
    OpenAIInstrumentor().instrument(tracer_provider=provider)
    logger.info(f"CrewAI + OpenAI spans → LangSmith project '{project}'.")


def init_langsmith() -> None:
    """Idempotent setup; safe to call from FastAPI lifespan startup."""
    global _initialized
    if _initialized:
        return
    _initialized = True

    if not _ensure_langsmith_env():
        return

    project = os.environ["LANGSMITH_PROJECT"]
    endpoint = os.environ["LANGSMITH_ENDPOINT"]
    api_key = os.environ["LANGSMITH_API_KEY"]

    logger.info(f"LangSmith tracing enabled → project='{project}'.")
    _instrument_crewai(project, api_key, endpoint)
