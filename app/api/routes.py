from fastapi import APIRouter
from pydantic import BaseModel
from app.services.query_handler import handle_question

router = APIRouter()

# Define the input schema
class QuestionRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_question(payload: QuestionRequest):
    return await handle_question(payload.question)

