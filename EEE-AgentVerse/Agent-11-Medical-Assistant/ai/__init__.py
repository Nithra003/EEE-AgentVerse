# ai/__init__.py
from ai.llm_router import get_router, LLMRouter
from ai.base_llm import BaseLLM, LLMMessage, LLMResponse
from ai.prompt_templates import (
    PRESCRIPTION_EXTRACT, MEDICINE_EXPLAIN,
    SYMPTOM_ANALYSE, MEDICAL_QA, MISSED_DOSE, TRANSLATE_TEXT,
)

__all__ = [
    "get_router", "LLMRouter",
    "BaseLLM", "LLMMessage", "LLMResponse",
    "PRESCRIPTION_EXTRACT", "MEDICINE_EXPLAIN",
    "SYMPTOM_ANALYSE", "MEDICAL_QA", "MISSED_DOSE", "TRANSLATE_TEXT",
]
