from langchain_google_genai import ChatGoogleGenerativeAI
from backend.app.core.config import settings

def get_parent_communicator_llm():
    """
    Initializes and returns the LLM for the Parent Communicator Agent.
    
    This agent is tuned for clear, empathetic, and professional communication.
    
    Returns:
        An instance of ChatGoogleGenerativeAI configured for this task.
    """
    llm = ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL_NAME,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.7, # A balance of creative but professional language
        convert_system_message_to_human=True
    )
    return llm