from pydantic import BaseModel


class StatisticsRead(BaseModel):
    version: str
    total_courses: int
    total_instructors: int
    total_students: int
    total_enrollments: int
