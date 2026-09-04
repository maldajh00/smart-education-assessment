from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models import Course, Instructor
from app.schemas.instructor import InstructorRead

router = APIRouter(prefix="/instructors", tags=["instructors"])


def _stmt():
    return (
        select(
            Instructor.id,
            Instructor.name,
            Instructor.specialization,
            Instructor.bio,
            func.count(Course.id).label("course_count"),
        )
        .outerjoin(Course, Course.instructor_id == Instructor.id)
        .group_by(Instructor.id)
    )


@router.get("", response_model=list[InstructorRead])
def list_instructors(db: Session = Depends(get_db)) -> list[InstructorRead]:
    rows = db.execute(_stmt().order_by(Instructor.name)).all()
    return [
        InstructorRead(
            id=r.id,
            name=r.name,
            specialization=r.specialization,
            bio=r.bio,
            course_count=r.course_count or 0,
        )
        for r in rows
    ]


@router.get("/{instructor_id}", response_model=InstructorRead)
def get_instructor(instructor_id: int, db: Session = Depends(get_db)) -> InstructorRead:
    row = db.execute(_stmt().where(Instructor.id == instructor_id)).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instructor not found")
    return InstructorRead(
        id=row.id,
        name=row.name,
        specialization=row.specialization,
        bio=row.bio,
        course_count=row.course_count or 0,
    )
