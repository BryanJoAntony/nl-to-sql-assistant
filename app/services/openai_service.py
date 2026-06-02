import json
import time

from openai import OpenAI
from pydantic import ValidationError

from app.core.config import settings
from app.core.exceptions import ConfigurationException, OpenAIServiceException
from app.core.logger import error_logger, openai_logger
from app.db.schema import SCHEMA_DESCRIPTION
from app.prompts.sql_generation_prompt import (
    PROMPT_VERSION,
    build_sql_generation_messages,
)
from app.schemas.openai_schema import OpenAISQLResponse


class OpenAIService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ConfigurationException("OPENAI_API_KEY is not configured")

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def generate_sql(self, question: str) -> OpenAISQLResponse:
        start_time = time.time()

        openai_logger.info(
            "OPENAI_SQL_GENERATION_STARTED | model=%s | prompt_version=%s | question_length=%s",
            self.model,
            PROMPT_VERSION,
            len(question),
        )

        messages = build_sql_generation_messages(
            question=question,
            schema_description=SCHEMA_DESCRIPTION,
            max_rows=settings.MAX_QUERY_ROWS,
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content

            if not content:
                raise OpenAIServiceException("OpenAI returned an empty response")

            parsed_content = json.loads(content)
            sql_response = OpenAISQLResponse(**parsed_content)

            duration_ms = round((time.time() - start_time) * 1000, 2)
            usage = getattr(response, "usage", None)

            openai_logger.info(
                "OPENAI_SQL_GENERATION_COMPLETED | model=%s | prompt_version=%s | duration_ms=%s | input_tokens=%s | output_tokens=%s",
                self.model,
                PROMPT_VERSION,
                duration_ms,
                getattr(usage, "prompt_tokens", None) if usage else None,
                getattr(usage, "completion_tokens", None) if usage else None,
            )

            return sql_response

        except json.JSONDecodeError as exc:
            error_logger.exception("OPENAI_RESPONSE_JSON_PARSE_FAILED")

            raise OpenAIServiceException(
                message="OpenAI response was not valid JSON",
                details={"raw_response": content if "content" in locals() else None},
            ) from exc

        except ValidationError as exc:
            error_logger.exception("OPENAI_RESPONSE_SCHEMA_VALIDATION_FAILED")

            raise OpenAIServiceException(
                message="OpenAI response did not match the expected schema",
                details={"errors": exc.errors()},
            ) from exc

        except OpenAIServiceException:
            raise

        except Exception as exc:
            error_logger.exception("OPENAI_SQL_GENERATION_FAILED")

            raise OpenAIServiceException(
                message="Failed to generate SQL using OpenAI",
                details={"error": str(exc)},
            ) from exc