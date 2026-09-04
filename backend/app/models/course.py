import enum

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CourseStatus(str, enum.Enum):
    active = "active"
    draft = "draft"
    archived = "archived"


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    duration_hours: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[CourseStatus] = mapped_column(
        Enum(CourseStatus, name="course_status"), nullable=False, default=CourseStatus.active
    )
    instructor_id: Mapped[int] = mapped_column(
        ForeignKey("instructors.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    instructor: Mapped["Instructor"] = relationship(back_populates="courses")  # noqa: F821
    enrollments: Mapped[list["Enrollment"]] = relationship(  # noqa: F821
        back_populates="course", cascade="all, delete-orphan"
    )
    progress: Mapped[list["CourseProgress"]] = relationship(  # noqa: F821
        back_populates="course", cascade="all, delete-orphan"
    )
