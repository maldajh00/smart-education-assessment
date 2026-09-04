from pydantic import BaseModel, ConfigDict


class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    category: str
    instructor_name: str
    description: str
    student_count: int = 0


class CourseDetailRead(CourseRead):
    duration_hours: int
    status: str
