from pydantic import BaseModel, Field
from typing import List


class QueryModel(BaseModel):
    service_id: str = Field(..., min_length=1)
    service_token: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1)
    session_id: str = Field(default="")
    intents: List[str] = Field(default=[])
    context_document_id: int = Field(default=0, ge=0)
    lower_bound: int = Field(default=0, ge=0)
    
class BatchQueryModel(BaseModel):
    payload: List[QueryModel] = Field(..., min_items=1, max_items=100)
