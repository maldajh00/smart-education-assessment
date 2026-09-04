from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    enrolled_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="student")  # noqa: F821
    enrollments: Mapped[list["Enrollment"]] = relationship(  # noqa: F821
        back_populates="student", cascade="all, delete-orphan"
    )
    progress: Mapped[list["CourseProgress"]] = relationship(  # noqa: F821
        back_populates="student", cascade="all, delete-orphan"
    )
