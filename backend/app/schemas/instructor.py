from pydantic import BaseModel, ConfigDict


class InstructorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    specialization: str
    bio: str | None = None
    course_count: int = 0
