from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models import CourseProgress, Enrollment, ProgressStatus, Student, User
from app.schemas.student import StudentRead

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/{student_id}", response_model=StudentRead)
def get_student(student_id: int, db: Session = Depends(get_db)) -> StudentRead:
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    user = db.get(User, student.user_id)

    enrolled_count = db.execute(
        select(func.count(Enrollment.id)).where(Enrollment.student_id == student_id)
    ).scalar_one()

    completed_count = db.execute(
        select(func.count(CourseProgress.id)).where(
            CourseProgress.student_id == student_id,
            CourseProgress.status == ProgressStatus.completed,
        )
    ).scalar_one()

    return StudentRead(
        id=student.id,
        name=user.name if user else "",
        email=user.email if user else "",
        enrolled_count=enrolled_count or 0,
        completed_count=completed_count or 0,
    )
