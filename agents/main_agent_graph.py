import json
import time
from typing import TypedDict, List, Dict

from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .lesson_designer_agent import get_lesson_designer_llm
from .quiz_generator_agent import get_quiz_generator_llm

# --- 1. AgentState Definition for THIS graph ---
# It only needs to know about the content being generated.
class ContentGenerationState(TypedDict):
    topic: str
    grade_level: str
    lesson_plan: str
    quiz: List[Dict] # Expecting the structured JSON quiz

# --- 2. Node Functions for THIS graph ---

def generate_lesson_plan_node(state: ContentGenerationState):
    """Node that invokes the Lesson Designer Agent."""
    print("---NODE: GENERATING LESSON PLAN---")
    llm = get_lesson_designer_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert educational assistant. Your task is to design a clear, concise, and engaging lesson plan, including title, objective, materials, and activities."),
        ("user", "Please create a lesson plan for a {grade_level} class on the topic of: '{topic}'.")
    ])
    chain = prompt | llm | StrOutputParser()
    lesson_plan = chain.invoke({"grade_level": state["grade_level"], "topic": state["topic"]})
    
    print("---Pausing for 5 seconds to respect API rate limits...")
    time.sleep(5)
    
    return {"lesson_plan": lesson_plan}


def generate_quiz_node(state: ContentGenerationState):
    """This node forces the LLM to generate a JSON string and parses it."""
    print("---NODE: GENERATING QUIZ (JSON)---")
    llm = get_quiz_generator_llm()
    json_prompt_template = """
You are a machine that STRICTLY outputs quiz data in JSON format.
Based on the provided lesson plan, generate a JSON array of 5 multiple-choice questions.

**RULES:**
1. The output MUST be a valid JSON array `[]`.
2. Each element MUST be a JSON object `{{}}`.
3. Each object MUST have three keys: "question", "options" (array of 4 strings), and "correct_answer_index" (integer from 0 to 3).
4. DO NOT output anything before or after the JSON array. Do not use markdown `json` tags.

**EXAMPLE OUTPUT FORMAT:**
[
  {{
    "question": "What is the capital of France?",
    "options": ["London", "Berlin", "Paris", "Madrid"],
    "correct_answer_index": 2
  }}
]

---
Here is the lesson plan to base the quiz on:
{lesson_plan}
"""
    prompt = ChatPromptTemplate.from_template(json_prompt_template)
    chain = prompt | llm | StrOutputParser()
    llm_output_str = chain.invoke({"lesson_plan": state["lesson_plan"]})
    print(f"---RAW JSON OUTPUT FROM LLM---\n{llm_output_str}\n------------------------------")
    
    quiz_data = []
    try:
        json_start = llm_output_str.find('[')
        json_end = llm_output_str.rfind(']') + 1
        if json_start != -1 and json_end != 0:
            clean_json_str = llm_output_str[json_start:json_end]
            quiz_data = json.loads(clean_json_str)
    except (json.JSONDecodeError, IndexError):
        print("---ERROR: FAILED TO PARSE JSON FROM LLM. Returning empty quiz.---")
        quiz_data = []
    
    # No pause needed here as it's the last step
    return {"quiz": quiz_data}


# --- 3. The Graph Builder ---
def build_content_generation_graph():
    """Builds the simple 2-step graph for creating a lesson and quiz."""
    workflow = StateGraph(ContentGenerationState)

    # Add the two nodes for this workflow
    workflow.add_node("lesson_planner", generate_lesson_plan_node)
    workflow.add_node("quiz_generator", generate_quiz_node)

    # Define the simple, linear flow
    workflow.set_entry_point("lesson_planner")
    workflow.add_edge("lesson_planner", "quiz_generator")
    workflow.add_edge("quiz_generator", END)
    
    app = workflow.compile()
    print("---CONTENT GENERATION GRAPH COMPILED---")
    return app