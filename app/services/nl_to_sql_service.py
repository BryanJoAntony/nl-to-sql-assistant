from typing import Any

from app.core.logger import error_logger, output_logger, sql_logger
from app.schemas.openai_schema import OpenAISQLResponse
from app.schemas.sql_schema import SQLValidationResult
from app.services.openai_service import OpenAIService
from app.services.query_history_service import QueryHistoryService
from app.services.sql_executor import SQLExecutor
from app.services.sql_validator import SQLValidator
from app.services.question_intent_guard import QuestionIntentGuard


class NLToSQLService:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.sql_validator = SQLValidator()
        self.sql_executor = SQLExecutor()
        self.query_history_service = QueryHistoryService()
        self.question_intent_guard = QuestionIntentGuard()

    def process_question(self, question: str, dry_run: bool = False) -> dict[str, Any]:
        try:
            output_logger.info(
                "NL_TO_SQL_PIPELINE_STARTED | question_length=%s | dry_run=%s",
                len(question),
                dry_run,
            )

            intent_result = self.question_intent_guard.check_question(question)

            if intent_result["blocked"]:
                result = {
                    "question": question,
                    "generated_sql": None,
                    "final_sql": None,
                    "explanation": "The request was blocked before SQL generation because it appears to ask for a destructive database operation.",
                    "confidence": None,
                    "dry_run": dry_run,
                    "safety": {
                        "is_safe": False,
                        "blocked": True,
                        "blocked_reason": intent_result["blocked_reason"],
                        "checks_passed": [],
                        "detected_tables": [],
                        "detected_columns": [],
                        "intent_guard": intent_result,
                    },
                    "execution": None,
                }

                self.query_history_service.save_query_history(result)

                output_logger.info(
                    "NL_TO_SQL_PIPELINE_BLOCKED_BY_INTENT | reason=%s",
                    intent_result["blocked_reason"],
                )

                return result
                
            generated_response: OpenAISQLResponse = self.openai_service.generate_sql(
                question=question
            )

            sql_logger.info(
                "SQL_GENERATED | confidence=%s | sql=%s",
                generated_response.confidence,
                generated_response.sql,
            )

            validation_result: SQLValidationResult = self.sql_validator.validate(
                generated_response.sql
            )

            if validation_result.blocked:
                result = {
                    "question": question,
                    "generated_sql": generated_response.sql,
                    "final_sql": None,
                    "explanation": generated_response.explanation,
                    "confidence": generated_response.confidence,
                    "dry_run": dry_run,
                    "safety": validation_result.model_dump(),
                    "execution": None,
                }

                self.query_history_service.save_query_history(result)

                output_logger.info(
                    "NL_TO_SQL_PIPELINE_BLOCKED | reason=%s",
                    validation_result.blocked_reason,
                )

                return result

            if dry_run:
                result = {
                    "question": question,
                    "generated_sql": generated_response.sql,
                    "final_sql": validation_result.final_sql,
                    "explanation": generated_response.explanation,
                    "confidence": generated_response.confidence,
                    "dry_run": dry_run,
                    "safety": validation_result.model_dump(),
                    "execution": None,
                }

                self.query_history_service.save_query_history(result)

                output_logger.info(
                    "NL_TO_SQL_PIPELINE_DRY_RUN_COMPLETED | final_sql=%s",
                    validation_result.final_sql,
                )

                return result

            execution_result = self.sql_executor.execute(validation_result.final_sql)

            result = {
                "question": question,
                "generated_sql": generated_response.sql,
                "final_sql": validation_result.final_sql,
                "explanation": generated_response.explanation,
                "confidence": generated_response.confidence,
                "dry_run": dry_run,
                "safety": validation_result.model_dump(),
                "execution": execution_result,
            }

            self.query_history_service.save_query_history(result)

            output_logger.info(
                "NL_TO_SQL_PIPELINE_COMPLETED | row_count=%s",
                execution_result["row_count"],
            )

            return result

        except Exception:
            error_logger.exception("NL_TO_SQL_PIPELINE_FAILED")
            raise