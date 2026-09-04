from fastapi import APIRouter

from app.api.routes import (
    courses,
    dashboard,
    instructors,
    statistics,
    students,
)

api_router = APIRouter(prefix="/api")
api_router.include_router(courses.router)
api_router.include_router(instructors.router)
api_router.include_router(students.router)
api_router.include_router(dashboard.router)
api_router.include_router(statistics.router)

__all__ = ["api_router"]
