from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models import Course, Enrollment, Instructor
from app.schemas.course import CourseDetailRead, CourseRead

router = APIRouter(prefix="/courses", tags=["courses"])


def _course_row_to_read(row) -> dict:
    return {
        "id": row.id,
        "title": row.title,
        "category": row.category,
        "instructor_name": row.instructor_name,
        "description": row.description,
        "student_count": row.student_count or 0,
    }


@router.get("", response_model=list[CourseRead])
def list_courses(db: Session = Depends(get_db)) -> list[CourseRead]:
    stmt = (
        select(
            Course.id,
            Course.title,
            Course.category,
            Course.description,
            Instructor.name.label("instructor_name"),
            func.count(Enrollment.id).label("student_count"),
        )
        .join(Instructor, Instructor.id == Course.instructor_id)
        .outerjoin(Enrollment, Enrollment.course_id == Course.id)
        .group_by(Course.id, Instructor.name)
        .order_by(Course.title)
    )
    rows = db.execute(stmt).all()
    return [CourseRead(**_course_row_to_read(r)) for r in rows]


@router.get("/{course_id}", response_model=CourseDetailRead)
def get_course(course_id: int, db: Session = Depends(get_db)) -> CourseDetailRead:
    stmt = (
        select(
            Course.id,
            Course.title,
            Course.category,
            Course.description,
            Course.duration_hours,
            Course.status,
            Instructor.name.label("instructor_name"),
            func.count(Enrollment.id).label("student_count"),
        )
        .join(Instructor, Instructor.id == Course.instructor_id)
        .outerjoin(Enrollment, Enrollment.course_id == Course.id)
        .where(Course.id == course_id)
        .group_by(Course.id, Instructor.name)
    )
    row = db.execute(stmt).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return CourseDetailRead(
        id=row.id,
        title=row.title,
        category=row.category,
        description=row.description,
        instructor_name=row.instructor_name,
        student_count=row.student_count or 0,
        duration_hours=row.duration_hours,
        status=row.status.value if hasattr(row.status, "value") else str(row.status),
    )
