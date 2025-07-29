from langchain_google_genai import ChatGoogleGenerativeAI
from backend.app.core.config import settings

def get_differentiated_support_llm():
    """
    Initializes and returns the LLM for the Differentiated Support Agent.
    
    This agent is tuned for creativity and generating diverse educational content.
    
    Returns:
        An instance of ChatGoogleGenerativeAI configured for this task.
    """
    llm = ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL_NAME,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.8, # Higher temperature for more creative/varied outputs
        convert_system_message_to_human=True
    )
    return llm