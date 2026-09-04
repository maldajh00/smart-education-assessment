from pydantic import BaseModel, ConfigDict


class StudentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    enrolled_count: int = 0
    completed_count: int = 0
