from app.schemas.course import CourseRead, CourseDetailRead
from app.schemas.instructor import InstructorRead
from app.schemas.student import StudentRead
from app.schemas.dashboard import DashboardRead, EnrolledCourse
from app.schemas.statistics import StatisticsRead
from app.schemas.health import HealthRead, ReadyRead

__all__ = [
    "CourseRead",
    "CourseDetailRead",
    "InstructorRead",
    "StudentRead",
    "DashboardRead",
    "EnrolledCourse",
    "StatisticsRead",
    "HealthRead",
    "ReadyRead",
]
