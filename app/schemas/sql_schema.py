from pydantic import BaseModel, Field


class SQLValidationResult(BaseModel):
    is_safe: bool
    blocked: bool
    original_sql: str
    final_sql: str | None = None
    blocked_reason: str | None = None
    checks_passed: list[str] = Field(default_factory=list)
    detected_tables: list[str] = Field(default_factory=list)
    detected_columns: list[str] = Field(default_factory=list)