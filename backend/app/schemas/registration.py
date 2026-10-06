from datetime import datetime
from pydantic import BaseModel, ConfigDict

class RegistrationResponse(BaseModel):
    id: int
    exam_id: int
    student_id: int
    exam_title: str
    category: str
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)
