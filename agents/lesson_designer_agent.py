from langchain_google_genai import ChatGoogleGenerativeAI
from backend.app.core.config import settings

def get_lesson_designer_llm():
    """
    Initializes and returns the LLM for the Lesson Designer Agent.
    
    This function configures the connection to the Google Gemini API using
    the specified model and API key from the application settings.
    
    Returns:
        An instance of ChatGoogleGenerativeAI configured for lesson planning.
    """
    llm = ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL_NAME,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.7,
        convert_system_message_to_human=True 
    )
    return llm