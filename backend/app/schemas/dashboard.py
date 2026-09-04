from pydantic import BaseModel, ConfigDict


class EnrolledCourse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    course_id: int
    title: str
    instructor_name: str
    progress_percent: int
    status: str


class DashboardRead(BaseModel):
    student_id: int
    student_name: str
    enrolled: list[EnrolledCourse]
    completed: list[EnrolledCourse]
    upcoming: list[EnrolledCourse]
