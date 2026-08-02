from __future__ import annotations

import json
import logging
from functools import lru_cache
from typing import Any

from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError, ServerError

from app.config import BASE_DIR, get_settings
from app.utils.exceptions import AppError

logger = logging.getLogger("lmkt.backend")

# Resolved once, relative to the project's BASE_DIR (backend/), not to this
# file's own depth in the package tree — so moving gemini_service.py to a
# different sub-package can never silently break the path again.
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
KNOWLEDGE_BASE_PATH = KNOWLEDGE_DIR / "knowledge_base.json"
SYSTEM_PROMPT_PATH = KNOWLEDGE_DIR / "system_prompt.txt"

# Minimal fallback content used only if knowledge_base.json is missing on
# disk (e.g. a fresh clone that hasn't been given real content yet). This
# keeps local dev / CI from 500ing outright; it is NOT meant for production.
_PLACEHOLDER_KNOWLEDGE_BASE = {
    "company": "LMKT",
    "services": [],
    "strengths": [],
    "products": [],
    "case_studies": [],
    "_notice": (
        "This is an auto-generated placeholder knowledge base. Replace "
        "backend/knowledge/knowledge_base.json with real content."
    ),
}


class GeminiService:
    """Production-ready wrapper around the Google Gen AI SDK."""

    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = (settings.gemini_api_key or "").strip()
        self.model_name = (settings.gemini_model or "").strip()

        if not self.api_key:
            raise AppError(status_code=500, detail="GEMINI_API_KEY is not configured")

        if not self.model_name:
            raise AppError(status_code=500, detail="GEMINI_MODEL is not configured")

        try:
            self._client = genai.Client(api_key=self.api_key)
        except ValueError as exc:
            logger.exception("Invalid Gemini client configuration")
            raise AppError(status_code=500, detail="Invalid Gemini API configuration") from exc
        except Exception as exc:
            logger.exception("Failed to initialize Gemini client")
            raise AppError(status_code=503, detail="AI service unavailable") from exc

    @property
    def client(self) -> genai.Client:
        """Expose the cached SDK client instance for reuse across requests."""
        return self._client

    def generate_response(self, prompt: str) -> str:
        """Generate a grounded answer from Gemini using the supplied prompt."""
        cleaned_prompt = prompt.strip()
        if not cleaned_prompt:
            raise AppError(status_code=400, detail="Prompt cannot be empty")

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=cleaned_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    top_p=0.9,
                    max_output_tokens=500,
                    response_mime_type="text/plain",
                ),
            )
        except (APIError, ClientError, ServerError) as exc:
            logger.exception("Gemini request failed for model %s", self.model_name)
            raise self._translate_sdk_error(exc) from exc
        except Exception as exc:
            logger.exception("Unexpected Gemini request failure for model %s", self.model_name)
            raise AppError(status_code=503, detail="AI service unavailable") from exc

        reply = getattr(response, "text", "")
        if not isinstance(reply, str) or not reply.strip():
            logger.warning("Gemini returned an empty response for model %s", self.model_name)
            raise AppError(status_code=502, detail="Gemini returned an empty response")

        return reply.strip()

    def _translate_sdk_error(self, exc: Exception) -> AppError:
        """Map SDK exceptions to stable application-level errors."""
        status_code = getattr(exc, "status_code", None) or getattr(exc, "code", None)

        if status_code in {401, 403}:
            return AppError(status_code=401, detail="Gemini authentication failed. Check GEMINI_API_KEY.")

        if status_code == 404:
            return AppError(
                status_code=400,
                detail=(
                    f"Configured Gemini model '{self.model_name}' is unavailable. "
                    "Update GEMINI_MODEL to a supported Gemini 2.5 Flash-Lite model."
                ),
            )

        if status_code == 429:
            return AppError(status_code=429, detail="Gemini API quota exceeded. Please retry later.")

        if status_code in {500, 502, 503, 504}:
            return AppError(status_code=503, detail="Gemini service is temporarily unavailable")

        return AppError(status_code=503, detail="AI service unavailable")

    @staticmethod
    @lru_cache(maxsize=1)
    def load_knowledge_base() -> dict[str, Any]:
        """Return the JSON knowledge base used for grounding the chatbot.

        Cached after the first successful read (cleared automatically if the
        process restarts) so we don't re-read + re-parse the file on every
        chat request.
        """
        if not KNOWLEDGE_BASE_PATH.exists():
            logger.warning(
                "Knowledge base file missing at %s; writing a placeholder so the "
                "service can start. Replace it with real content.",
                KNOWLEDGE_BASE_PATH,
            )
            KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
            KNOWLEDGE_BASE_PATH.write_text(
                json.dumps(_PLACEHOLDER_KNOWLEDGE_BASE, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        try:
            with KNOWLEDGE_BASE_PATH.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except json.JSONDecodeError as exc:
            logger.error("Knowledge base file is not valid JSON: %s", KNOWLEDGE_BASE_PATH)
            raise ValueError(f"Knowledge base file is not valid JSON: {KNOWLEDGE_BASE_PATH}") from exc

    @staticmethod
    @lru_cache(maxsize=1)
    def load_system_prompt() -> str:
        """Read the domain-restricted system prompt from disk (cached)."""
        if not SYSTEM_PROMPT_PATH.exists():
            logger.error("System prompt file missing: %s", SYSTEM_PROMPT_PATH)
            raise FileNotFoundError(
                f"System prompt file not found at {SYSTEM_PROMPT_PATH}. "
                "Ensure 'backend/knowledge/system_prompt.txt' exists."
            )
        return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def get_gemini_service() -> GeminiService:
    """Return the singleton Gemini service instance for request reuse."""
    return GeminiService()
