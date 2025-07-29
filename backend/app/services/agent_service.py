import logging
from typing import Optional, List, Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Import our specific graph builder and the necessary agent LLM getters
from agents.main_agent_graph import build_content_generation_graph
from agents.differentiated_support_agent import get_differentiated_support_llm
from agents.parent_communicator_agent import get_parent_communicator_llm

# --- Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Build the content generation graph once when the module is loaded
content_graph_app = build_content_generation_graph()


# --- Workflow 1: Content Generation (using the graph) ---
def run_content_generation(topic: str, grade_level: str) -> dict:
    """
    Runs the simple 2-step graph to generate a new lesson plan and quiz.
    """
    try:
        logger.info(f"Running content generation workflow for topic: '{topic}'")
        inputs = {"topic": topic, "grade_level": grade_level}
        
        final_state = content_graph_app.invoke(inputs)
        
        logger.info("Content generation workflow completed successfully.")
        
        # This function correctly nests the output in a 'data' key.
        return {
            "status": "success", 
            "data": {
                "lesson_plan": final_state.get("lesson_plan"),
                "quiz": final_state.get("quiz"),
            }
        }

    except Exception as e:
        logger.error(f"Error in content generation: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


# --- Workflow 2: Differentiated Support (single agent call) ---
def run_support_generation(
    topic: str,
    quiz_score: int,
    student_name: str,
    student_performance_summary: str,
    wrong_answers: List[Dict]
) -> dict:
    """
    Invokes only the Differentiated Support Agent to generate hyper-personalized materials.
    """
    try:
        logger.info(f"Running support generation for {student_name}, score: {quiz_score}")
        llm = get_differentiated_support_llm()

        # Helper to format the wrong answers for the prompt
        wrong_answers_text = "\n".join([
            f"- Question: {wa['question']}\n  - Their Answer: {wa['their_answer']}\n  - Correct Answer: {wa['correct_answer']}" 
            for wa in wrong_answers
        ]) if wrong_answers else "None"
        
        # Determine which detailed prompt to use based on the score
        if quiz_score < 70:
            system_prompt = f"""
You are an expert, empathetic tutor creating a personalized remedial worksheet for **{student_name}**.

**Student Context:**
- **General Performance:** {student_performance_summary}
- **Recent Quiz Score:** {quiz_score}%
- **Specific Mistakes on the Quiz:**
{wrong_answers_text}

**Your Task:**
Create a helpful, one-page worksheet titled "{topic}: Let's Review!". It must have these markdown sections:
1.  **A Quick Note for {student_name}:** Write a short, encouraging paragraph. Acknowledge their effort and frame this as a helpful review.
2.  **Let's Revisit the Tricky Parts:** Based *specifically* on their wrong answers, provide a simple, targeted re-explanation of the core concepts they misunderstood.
3.  **Practice Questions:** Write 2-3 new practice questions similar to the ones they got wrong.
4.  **Answer Key:** Provide a clear answer key at the bottom.
Generate only the structured worksheet content.
"""
        elif quiz_score > 90:
            system_prompt = f"""
You are an expert curriculum designer for advanced students, creating an enrichment project for **{student_name}**.

**Student Context:**
- **General Performance:** {student_performance_summary}
- **Recent Quiz Score:** {quiz_score}%

**Your Task:**
Create an exciting "Enrichment Project Brief" titled "{topic}: Expert Challenge!". It must have these markdown sections:
1.  **Congratulations, {student_name}!:** Write a single sentence congratulating them on mastering the material.
2.  **Your Mission:** Based on their profile (e.g., "seeks new challenges"), write a creative, one-sentence project goal.
3.  **Project Outline:** List 3-4 bullet points outlining the project steps.
4.  **Submission Format:** Suggest a creative presentation format (e.g., a short video, a slide deck).
"""
        else: # Reinforcement for scores 70-90
            system_prompt = f"""
You are a motivating teacher creating a "Next Steps" activity for **{student_name}**.

**Student Context:**
- **General Performance:** {student_performance_summary}
- **Recent Quiz Score:** {quiz_score}%

**Your Task:**
Create a short, engaging activity sheet titled "{topic}: Great Job!". It must have these markdown sections:
1.  **Excellent Work, {student_name}!:** Write a single, personalized sentence of praise.
2.  **Challenge Question:** Write one thought-provoking, open-ended question related to the topic.
3.  **Explore Further:** Provide one high-quality link (full URL) to an online resource.
"""

        prompt = ChatPromptTemplate.from_template(system_prompt)
        chain = prompt | llm | StrOutputParser()
        
        differentiated_output = chain.invoke({}) # All context is in the prompt template
        
        logger.info("Support generation successful.")

        # --- THIS IS THE FIX ---
        # Wrap the successful response in a 'data' key to match the API's expectation.
        return {
            "status": "success",
            "data": {
                "differentiated_output": differentiated_output
            }
        }

    except Exception as e:
        logger.error(f"An error occurred in support generation: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


# --- Workflow 3: Parent Communication (single agent call) ---
def run_parent_communication_generation(student_name: str, quiz_topic: str, score: int, support_material: str) -> dict:
    """
    Invokes the Parent Communicator Agent to draft a note for parents.
    """
    try:
        logger.info(f"Generating parent communication for {student_name} on topic '{quiz_topic}'.")
        llm = get_parent_communicator_llm()
        system_prompt = """
You are an empathetic and professional school communicator. Your task is to draft a brief, positive, and clear note to a student's parent about their recent quiz performance...
"""
        user_prompt = f"""
Please draft the parent note based on this information:
- Student's Name: {student_name}
- Quiz Topic: {quiz_topic}
- Their Score: {score}%
- Support Material Provided:
---
{support_material}
---
"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt)
        ])
        chain = prompt | llm | StrOutputParser()
        parent_note = chain.invoke({})
        
        return {"status": "success", "parent_note": parent_note}

    except Exception as e:
        logger.error(f"An error occurred in parent communication generation: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}