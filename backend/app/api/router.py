from fastapi import APIRouter
from app.api.endpoints import auth, students, exams, questions, registrations, attempts, results

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(exams.router, prefix="/exams", tags=["exams"])
api_router.include_router(questions.router, tags=["questions"])
api_router.include_router(registrations.router, tags=["registrations"])
api_router.include_router(attempts.router, tags=["attempts"])
api_router.include_router(results.router, tags=["results"])
