import re

from app.core.constants import DESTRUCTIVE_INTENT_KEYWORDS


class QuestionIntentGuard:
    def check_question(self, question: str) -> dict:
        normalized_question = question.lower()

        for keyword in DESTRUCTIVE_INTENT_KEYWORDS:
            pattern = rf"\b{re.escape(keyword)}\b"

            if re.search(pattern, normalized_question):
                return {
                    "is_safe": False,
                    "blocked": True,
                    "blocked_reason": (
                        f"Unsafe user intent detected: '{keyword}'. "
                        "Only read-only analytics questions are allowed."
                    ),
                    "matched_keyword": keyword,
                }

        return {
            "is_safe": True,
            "blocked": False,
            "blocked_reason": None,
            "matched_keyword": None,
        }