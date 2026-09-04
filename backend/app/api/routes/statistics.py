from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.config import get_settings
from app.models import Course, Enrollment, Instructor, Student
from app.schemas.statistics import StatisticsRead

router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.get("", response_model=StatisticsRead)
def get_statistics(db: Session = Depends(get_db)) -> StatisticsRead:
    settings = get_settings()
    total_courses = db.execute(select(func.count(Course.id))).scalar_one()
    total_instructors = db.execute(select(func.count(Instructor.id))).scalar_one()
    total_students = db.execute(select(func.count(Student.id))).scalar_one()
    total_enrollments = db.execute(select(func.count(Enrollment.id))).scalar_one()
    return StatisticsRead(
        version=settings.app_version,
        total_courses=total_courses,
        total_instructors=total_instructors,
        total_students=total_students,
        total_enrollments=total_enrollments,
    )
