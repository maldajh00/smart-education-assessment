"""
Idempotent seed script for the Smart Education Portal.

Usage:
    python -m app.seed

Safe to run repeatedly — existing rows are matched by natural keys
(email, instructor name, course title) and updated instead of duplicated.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.logging import configure_logging
from app.models import (
    Course,
    CourseProgress,
    CourseStatus,
    Enrollment,
    Instructor,
    ProgressStatus,
    Student,
    User,
    UserRole,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CourseSpec:
    title: str
    category: str
    description: str
    duration_hours: int
    status: CourseStatus
    instructor_name: str


INSTRUCTORS: list[dict] = [
    {
        "name": "Dr. Sara Al-Farsi",
        "specialization": "Cloud Architecture",
        "bio": "Ten years designing GCP and AWS platforms for enterprise workloads.",
    },
    {
        "name": "Prof. Omar Haddad",
        "specialization": "Kubernetes & Platform Engineering",
        "bio": "CKA/CKAD; teaches production-grade Kubernetes to platform teams.",
    },
    {
        "name": "Layla Nasser",
        "specialization": "Cybersecurity",
        "bio": "Former DFIR lead. Focus on secure-by-default architecture.",
    },
    {
        "name": "Karim Youssef",
        "specialization": "Backend Engineering (Python)",
        "bio": "Builds high-throughput APIs; contributor to open-source FastAPI tooling.",
    },
    {
        "name": "Nour El-Sayed",
        "specialization": "DevOps & SRE",
        "bio": "CI/CD, observability, and progressive delivery specialist.",
    },
]


COURSES: list[CourseSpec] = [
    CourseSpec(
        title="Cloud Computing Fundamentals",
        category="Cloud",
        description=(
            "Concepts of IaaS, PaaS, and SaaS; core Google Cloud services; "
            "networking, identity, storage, and cost basics."
        ),
        duration_hours=20,
        status=CourseStatus.active,
        instructor_name="Dr. Sara Al-Farsi",
    ),
    CourseSpec(
        title="Kubernetes Administration",
        category="Kubernetes",
        description=(
            "Cluster architecture, workloads, services, ingress, RBAC, "
            "autoscaling, and troubleshooting on GKE."
        ),
        duration_hours=30,
        status=CourseStatus.active,
        instructor_name="Prof. Omar Haddad",
    ),
    CourseSpec(
        title="Cybersecurity Essentials",
        category="Security",
        description=(
            "Threat models, secure defaults, secrets management, "
            "and the OWASP top ten for cloud-native applications."
        ),
        duration_hours=18,
        status=CourseStatus.active,
        instructor_name="Layla Nasser",
    ),
    CourseSpec(
        title="Python Backend Development",
        category="Backend",
        description=(
            "Designing REST APIs with FastAPI, SQLAlchemy, "
            "Pydantic, and Alembic; testing and packaging."
        ),
        duration_hours=25,
        status=CourseStatus.active,
        instructor_name="Karim Youssef",
    ),
    CourseSpec(
        title="DevOps Engineering",
        category="DevOps",
        description=(
            "CI/CD with GitHub Actions, containerization with Docker, "
            "GitOps with Argo CD, and observability with Prometheus."
        ),
        duration_hours=28,
        status=CourseStatus.active,
        instructor_name="Nour El-Sayed",
    ),
    CourseSpec(
        title="Introduction to SRE",
        category="DevOps",
        description=(
            "SLIs, SLOs, error budgets, incident response, and the "
            "cultural practices behind reliable production systems."
        ),
        duration_hours=15,
        status=CourseStatus.draft,
        instructor_name="Nour El-Sayed",
    ),
]


STUDENTS: list[dict] = [
    {"name": "Amina Karim", "email": "amina.karim@example.com"},
    {"name": "Bilal Osman", "email": "bilal.osman@example.com"},
    {"name": "Chloe Habib", "email": "chloe.habib@example.com"},
    {"name": "Danyal Reza", "email": "danyal.reza@example.com"},
    {"name": "Eman Sabir", "email": "eman.sabir@example.com"},
    {"name": "Fahad Mansour", "email": "fahad.mansour@example.com"},
]


ENROLLMENTS: list[tuple[str, str, int, ProgressStatus]] = [
    # (student_email, course_title, progress_percent, status)
    ("amina.karim@example.com", "Cloud Computing Fundamentals", 100, ProgressStatus.completed),
    ("amina.karim@example.com", "Kubernetes Administration", 60, ProgressStatus.in_progress),
    ("amina.karim@example.com", "DevOps Engineering", 0, ProgressStatus.upcoming),
    ("bilal.osman@example.com", "Cybersecurity Essentials", 85, ProgressStatus.in_progress),
    ("bilal.osman@example.com", "Python Backend Development", 100, ProgressStatus.completed),
    ("chloe.habib@example.com", "Cloud Computing Fundamentals", 45, ProgressStatus.in_progress),
    ("chloe.habib@example.com", "Kubernetes Administration", 0, ProgressStatus.upcoming),
    ("danyal.reza@example.com", "Python Backend Development", 70, ProgressStatus.in_progress),
    ("danyal.reza@example.com", "DevOps Engineering", 30, ProgressStatus.in_progress),
    ("eman.sabir@example.com", "Cybersecurity Essentials", 100, ProgressStatus.completed),
    ("eman.sabir@example.com", "Cloud Computing Fundamentals", 20, ProgressStatus.in_progress),
    ("fahad.mansour@example.com", "Kubernetes Administration", 100, ProgressStatus.completed),
    ("fahad.mansour@example.com", "DevOps Engineering", 55, ProgressStatus.in_progress),
]


def _upsert_instructor(db: Session, spec: dict) -> Instructor:
    obj = db.execute(select(Instructor).where(Instructor.name == spec["name"])).scalar_one_or_none()
    if obj is None:
        obj = Instructor(**spec)
        db.add(obj)
        db.flush()
        logger.info("created instructor %s", spec["name"])
    else:
        obj.specialization = spec["specialization"]
        obj.bio = spec["bio"]
    return obj


def _upsert_course(db: Session, spec: CourseSpec, instructor_id: int) -> Course:
    obj = db.execute(select(Course).where(Course.title == spec.title)).scalar_one_or_none()
    if obj is None:
        obj = Course(
            title=spec.title,
            description=spec.description,
            category=spec.category,
            duration_hours=spec.duration_hours,
            status=spec.status,
            instructor_id=instructor_id,
        )
        db.add(obj)
        db.flush()
        logger.info("created course %s", spec.title)
    else:
        obj.description = spec.description
        obj.category = spec.category
        obj.duration_hours = spec.duration_hours
        obj.status = spec.status
        obj.instructor_id = instructor_id
    return obj


def _upsert_student(db: Session, spec: dict) -> Student:
    user = db.execute(select(User).where(User.email == spec["email"])).scalar_one_or_none()
    if user is None:
        user = User(email=spec["email"], name=spec["name"], role=UserRole.student)
        db.add(user)
        db.flush()
        logger.info("created user %s", spec["email"])
    else:
        user.name = spec["name"]
        user.role = UserRole.student

    student = db.execute(select(Student).where(Student.user_id == user.id)).scalar_one_or_none()
    if student is None:
        student = Student(user_id=user.id)
        db.add(student)
        db.flush()
        logger.info("created student for %s", spec["email"])
    return student


def _upsert_enrollment_and_progress(
    db: Session,
    student_id: int,
    course_id: int,
    percent: int,
    status: ProgressStatus,
) -> None:
    enrollment = db.execute(
        select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id,
        )
    ).scalar_one_or_none()
    if enrollment is None:
        db.add(Enrollment(student_id=student_id, course_id=course_id))
        db.flush()

    progress = db.execute(
        select(CourseProgress).where(
            CourseProgress.student_id == student_id,
            CourseProgress.course_id == course_id,
        )
    ).scalar_one_or_none()
    if progress is None:
        db.add(
            CourseProgress(
                student_id=student_id,
                course_id=course_id,
                progress_percent=percent,
                status=status,
            )
        )
    else:
        progress.progress_percent = percent
        progress.status = status


def seed(db: Session) -> dict[str, int]:
    instructors_by_name = {
        spec["name"]: _upsert_instructor(db, spec) for spec in INSTRUCTORS
    }

    courses_by_title: dict[str, Course] = {}
    for spec in COURSES:
        instructor = instructors_by_name[spec.instructor_name]
        courses_by_title[spec.title] = _upsert_course(db, spec, instructor.id)

    students_by_email = {
        spec["email"]: _upsert_student(db, spec) for spec in STUDENTS
    }

    for email, title, percent, status in ENROLLMENTS:
        student = students_by_email[email]
        course = courses_by_title[title]
        _upsert_enrollment_and_progress(db, student.id, course.id, percent, status)

    db.commit()
    return {
        "instructors": len(instructors_by_name),
        "courses": len(courses_by_title),
        "students": len(students_by_email),
        "enrollments": len(ENROLLMENTS),
    }


def main() -> None:
    configure_logging("smart-education-seed")
    logger.info("starting seed")
    with SessionLocal() as db:
        counts = seed(db)
    logger.info("seed complete: %s", counts)


if __name__ == "__main__":
    main()
