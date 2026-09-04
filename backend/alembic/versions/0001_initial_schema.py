"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-04

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column(
            "role",
            sa.Enum("student", "instructor", "admin", name="user_role"),
            nullable=False,
            server_default="student",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "instructors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("specialization", sa.String(length=120), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
    )

    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "enrolled_on",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("duration_hours", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "status",
            sa.Enum("active", "draft", "archived", name="course_status"),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "instructor_id",
            sa.Integer(),
            sa.ForeignKey("instructors.id", ondelete="RESTRICT"),
            nullable=False,
        ),
    )
    op.create_index("ix_courses_title", "courses", ["title"])
    op.create_index("ix_courses_category", "courses", ["category"])
    op.create_index("ix_courses_instructor_id", "courses", ["instructor_id"])

    op.create_table(
        "enrollments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "student_id",
            sa.Integer(),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "course_id",
            sa.Integer(),
            sa.ForeignKey("courses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "enrolled_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("student_id", "course_id", name="uq_enrollments_student_course"),
    )
    op.create_index("ix_enrollments_student_id", "enrollments", ["student_id"])
    op.create_index("ix_enrollments_course_id", "enrollments", ["course_id"])

    op.create_table(
        "course_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "student_id",
            sa.Integer(),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "course_id",
            sa.Integer(),
            sa.ForeignKey("courses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("progress_percent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "status",
            sa.Enum("in_progress", "completed", "upcoming", name="progress_status"),
            nullable=False,
            server_default="in_progress",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("student_id", "course_id", name="uq_progress_student_course"),
        sa.CheckConstraint(
            "progress_percent BETWEEN 0 AND 100", name="ck_progress_percent_range"
        ),
    )
    op.create_index("ix_course_progress_student_id", "course_progress", ["student_id"])
    op.create_index("ix_course_progress_course_id", "course_progress", ["course_id"])


def downgrade() -> None:
    op.drop_table("course_progress")
    op.drop_table("enrollments")
    op.drop_table("courses")
    op.drop_table("students")
    op.drop_table("instructors")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS progress_status")
    op.execute("DROP TYPE IF EXISTS course_status")
    op.execute("DROP TYPE IF EXISTS user_role")
