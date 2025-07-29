import streamlit as st
import requests
import os
import pandas as pd

# --- Configuration ---
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
API_PREFIX = "/api/v1/generate"
ENDPOINTS = {
    "Generate Content": f"{BACKEND_URL}{API_PREFIX}/generate-content",
    "Generate Support": f"{BACKEND_URL}{API_PREFIX}/generate-support",
    "Save Score": f"{BACKEND_URL}{API_PREFIX}/save-score",
    "Get Results": f"{BACKEND_URL}{API_PREFIX}/quiz-results",
    "Get Students": f"{BACKEND_URL}{API_PREFIX}/students",
}

# --- Initialize Session State ---
if "view" not in st.session_state: st.session_state.view = "main"
if "content" not in st.session_state: st.session_state.content = {}
if "topic" not in st.session_state: st.session_state.topic = "The Water Cycle"
if "quiz_active" not in st.session_state: st.session_state.quiz_active = False
if "student_id" not in st.session_state: st.session_state.student_id = None
# --- ADD THIS NEW STATE VARIABLE ---
if "last_score" not in st.session_state: st.session_state.last_score = None

# --- Main App ---
st.set_page_config(page_title="EduCopilot", page_icon="📚", layout="wide")
st.title("📚 EduCopilot")
st.markdown("##### The Intelligent Multi-Agent System for the Modern Classroom")

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
if st.sidebar.button("Content Generation", use_container_width=True):
    st.session_state.view = "main"
    st.session_state.quiz_active = False
    st.session_state.last_score = None # Reset score on navigation
if st.sidebar.button("Teacher Dashboard", use_container_width=True):
    st.session_state.view = "dashboard"
    st.session_state.quiz_active = False

# --- Main Page View (Content Generation & Quiz) ---
if st.session_state.view == "main":
    st.header("📝 Step 1: Generate Content")
    with st.form("generation_form"):
        col1, col2 = st.columns(2)
        with col1:
            grade_level = st.text_input("Grade Level", value="5th Grade")
        with col2:
            topic = st.text_input("Lesson Topic", value=st.session_state.topic)
        submitted = st.form_submit_button("Generate Lesson Plan & Quiz")

    if submitted:
        st.session_state.topic = topic
        st.session_state.quiz_active = False
        st.session_state.last_score = None # Reset score on new generation
        payload = {"topic": topic, "grade_level": grade_level}
        with st.spinner("Agents are generating content..."):
            try:
                response = requests.post(ENDPOINTS["Generate Content"], json=payload, timeout=300)
                response.raise_for_status()
                st.session_state.content = response.json()
            except requests.exceptions.RequestException as e:
                st.session_state.content = {}
                st.error(f"Error connecting to backend: {e}")

    if st.session_state.content.get("lesson_plan"):
        st.write("---")
        st.success("Content generated successfully!")
        st.subheader("Generated Lesson Plan")
        st.markdown(st.session_state.content["lesson_plan"])

        quiz_questions = st.session_state.content.get("quiz", [])
        if not quiz_questions or not isinstance(quiz_questions, list):
            st.error("The AI did not generate a quiz in the expected format. Please try again.")
        else:
            st.write("---")
            st.header("✍️ Step 2: Attempt the Quiz")

            # --- NEW: Display the score if it exists ---
            if st.session_state.last_score is not None:
                st.success(f"Quiz Submitted! Final Score: {st.session_state.last_score}%")
                st.info("Score saved. Navigate to the Teacher Dashboard to view results, or start the quiz for another student.")

            if not st.session_state.quiz_active:
                try:
                    students_response = requests.get(ENDPOINTS["Get Students"])
                    students_response.raise_for_status()
                    all_students = students_response.json().get("data", [])
                    
                    if not all_students:
                        st.warning("No student data available.")
                    else:
                        student_map = {s['name']: s['id'] for s in all_students}
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            selected_student_name = st.selectbox("Select Student:", options=list(student_map.keys()))
                        with col2:
                            st.write("")
                            if st.button(f"Start Quiz for {selected_student_name}"):
                                st.session_state.student_id = student_map[selected_student_name]
                                st.session_state.quiz_active = True
                                st.session_state.last_score = None # Reset score before starting new attempt
                                st.rerun()
                except requests.exceptions.RequestException as e:
                    st.error(f"Could not load student data: {e}")

            if st.session_state.quiz_active:
                st.subheader(f"Quiz for: {st.session_state.topic}")
                with st.form("quiz_form"):
                    user_answers = {}
                    for i, q in enumerate(quiz_questions):
                        user_answers[i] = st.radio(q["question"], q["options"], key=f"q_{i}", index=None)
                    
                    quiz_submitted = st.form_submit_button("Submit Quiz")

                    if quiz_submitted:
                        if None in user_answers.values():
                            st.error("Please answer all questions.")
                        else:
                            correct_count = 0
                            wrong_answers_list = []
                            for i, q in enumerate(quiz_questions):
                                selected_option = user_answers[i]
                                correct_option = q["options"][q["correct_answer_index"]]
                                if selected_option == correct_option:
                                    correct_count += 1
                                else:
                                    wrong_answers_list.append({"question": q["question"], "their_answer": selected_option, "correct_answer": correct_option})
                            
                            score_percent = int((correct_count / len(quiz_questions)) * 100)
                            # --- SAVE SCORE TO SESSION STATE ---
                            st.session_state.last_score = score_percent
                            
                            score_payload = {"student_id": st.session_state.student_id, "quiz_topic": st.session_state.topic, "score_percent": score_percent, "total_questions": len(quiz_questions), "wrong_answers": wrong_answers_list}
                            try:
                                requests.post(ENDPOINTS["Save Score"], json=score_payload)
                            except requests.exceptions.RequestException as e:
                                st.error(f"Failed to save score: {e}")

                            st.session_state.quiz_active = False
                            st.balloons()
                            st.rerun() # This is now safe because the score is saved

# --- Teacher Dashboard View ---
elif st.session_state.view == "dashboard":
    st.header("📊 Teacher Dashboard")
    st.write("View the most recent student quiz results and generate targeted support.")
    
    try:
        results_response = requests.get(ENDPOINTS["Get Results"])
        results_response.raise_for_status()
        all_results_data = results_response.json().get("data", [])

        if not all_results_data:
            st.info("No quiz results found yet.")
        else:
            df = pd.DataFrame(all_results_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            latest_results_df = df.sort_values('timestamp', ascending=False).drop_duplicates(subset=['student_id', 'quiz_topic'], keep='first')

            st.dataframe(latest_results_df[['student_name', 'quiz_topic', 'score_percent', 'timestamp']])

            st.write("---")
            st.subheader("Generate Differentiated Support")
            
            latest_results_list = latest_results_df.to_dict('records')
            result_options = {
                f"{res['student_name']} - {res['quiz_topic']} ({res['score_percent']}%)": res
                for res in latest_results_list
            }
            
            if not result_options:
                st.warning("No results available to generate support for.")
            else:
                selected_result_key = st.selectbox("Select a student result:", options=result_options.keys())
                
                if st.button("Generate Support Materials for Selected Result"):
                    selected_result = result_options[selected_result_key]
                    
                    students_response = requests.get(ENDPOINTS["Get Students"])
                    all_students = students_response.json().get("data", [])
                    student_profile = next((s for s in all_students if s['id'] == selected_result['student_id']), None)

                    payload = {
                        "topic": selected_result['quiz_topic'],
                        "quiz_score": selected_result['score_percent'],
                        "student_name": selected_result['student_name'],
                        "student_performance_summary": student_profile['performance_summary'] if student_profile else "N/A",
                        "wrong_answers": selected_result.get('wrong_answers', [])
                    }
                    with st.spinner("Differentiated Support Agent is at work..."):
                        try:
                            response = requests.post(ENDPOINTS["Generate Support"], json=payload, timeout=300)
                            response.raise_for_status()
                            result = response.json()
                            
                            st.subheader("Targeted Support Material Generated")
                            st.markdown(result["differentiated_output"])

                        except requests.exceptions.RequestException as e:
                            st.error(f"Backend Error: {e}")

    except requests.exceptions.RequestException as e:
        st.error(f"Could not load dashboard data: {e}")