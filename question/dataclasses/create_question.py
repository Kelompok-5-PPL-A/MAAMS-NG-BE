from uuid import UUID
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class CreateQuestionDataClass(BaseModel):
    username: Optional[str] = None  # untuk guest
    id: UUID
    title: str
    question: str
    created_at: datetime
    mode: str
    tags: List[str]
    
    class Config:
        arbitrary_types_allowed = True