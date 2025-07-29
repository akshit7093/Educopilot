from langchain_google_genai import ChatGoogleGenerativeAI
from backend.app.core.config import settings

def get_quiz_generator_llm():
    """
    Initializes and returns the LLM for the Quiz Generator Agent.
    
    This function configures a separate LLM instance, potentially with
    different settings if needed, for generating quizzes.
    
    Returns:
        An instance of ChatGoogleGenerativeAI configured for quiz generation.
    """
    llm = ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL_NAME,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.5, # Slightly lower temperature for more predictable quiz questions
        convert_system_message_to_human=True
    )
    return llm