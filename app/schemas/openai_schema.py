from pydantic import BaseModel, Field


class OpenAISQLResponse(BaseModel):
    sql: str = Field(..., min_length=1)
    explanation: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0, le=1)