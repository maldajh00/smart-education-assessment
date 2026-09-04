from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models import Course, CourseProgress, Instructor, ProgressStatus, Student, User
from app.schemas.dashboard import DashboardRead, EnrolledCourse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/{student_id}", response_model=DashboardRead)
def get_dashboard(student_id: int, db: Session = Depends(get_db)) -> DashboardRead:
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    user = db.get(User, student.user_id)

    rows = db.execute(
        select(
            Course.id.label("course_id"),
            Course.title,
            Instructor.name.label("instructor_name"),
            CourseProgress.progress_percent,
            CourseProgress.status,
        )
        .join(CourseProgress, CourseProgress.course_id == Course.id)
        .join(Instructor, Instructor.id == Course.instructor_id)
        .where(CourseProgress.student_id == student_id)
        .order_by(Course.title)
    ).all()

    enrolled: list[EnrolledCourse] = []
    completed: list[EnrolledCourse] = []
    upcoming: list[EnrolledCourse] = []

    for r in rows:
        status_value = r.status.value if hasattr(r.status, "value") else str(r.status)
        item = EnrolledCourse(
            course_id=r.course_id,
            title=r.title,
            instructor_name=r.instructor_name,
            progress_percent=r.progress_percent,
            status=status_value,
        )
        if r.status == ProgressStatus.completed:
            completed.append(item)
        elif r.status == ProgressStatus.upcoming:
            upcoming.append(item)
        else:
            enrolled.append(item)

    return DashboardRead(
        student_id=student_id,
        student_name=user.name if user else "",
        enrolled=enrolled,
        completed=completed,
        upcoming=upcoming,
    )
