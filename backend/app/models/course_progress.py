import enum
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProgressStatus(str, enum.Enum):
    in_progress = "in_progress"
    completed = "completed"
    upcoming = "upcoming"


class CourseProgress(Base):
    __tablename__ = "course_progress"
    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_progress_student_course"),
        CheckConstraint(
            "progress_percent BETWEEN 0 AND 100", name="ck_progress_percent_range"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    progress_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[ProgressStatus] = mapped_column(
        Enum(ProgressStatus, name="progress_status"),
        nullable=False,
        default=ProgressStatus.in_progress,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    student: Mapped["Student"] = relationship(back_populates="progress")  # noqa: F821
    course: Mapped["Course"] = relationship(back_populates="progress")  # noqa: F821
