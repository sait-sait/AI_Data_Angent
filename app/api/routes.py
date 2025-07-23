import sys
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ai_logic import handle_question
from app.core.logger import logging 
from app.core.exception import CustomException 

router = APIRouter()

class QuestionModel(BaseModel):
    question: str

@router.post("/ask")
async def ask_question(question: QuestionModel):  # <-- async here
    try:
        logging.info(f"Received question: {question.question}")
        result = await handle_question(question.question)  # <-- await here
        logging.info(f"Generated result: {result}")
        return result
    except Exception as e:
        logging.error(f"Error in /ask: {e}")
        raise CustomException(e, sys)
