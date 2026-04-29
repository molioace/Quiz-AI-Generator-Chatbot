from pypdf import PdfReader
import streamlit as st
import os
import uuid
from streamlit_cookies_manager import EncryptedCookieManager
import re
import json


def setup_cookies() -> str:
    """
    Creates or retrieves a persistent user_id stored in encrypted cookies.

    Purpose:
    - Identify returning users across sessions.
    - Allow the chatbot to associate conversation history
      or memory with the same user.
    - Store the ID securely using encrypted cookies.

    Returns:
        str: A unique user_id for the current user session.
    """
    user_id = ""

    cookies = EncryptedCookieManager(
        prefix="myapp_",
        password=os.getenv("COOKIES_PASSWORD")
    )

    if not cookies.ready():
        st.error("Failed to create cookies")
        st.stop()

    if "user_id" not in cookies:
        user_id = str(uuid.uuid4())
        cookies["user_id"] = user_id
        cookies.save()

    else:
        user_id = cookies["user_id"]
    return user_id



def setup_api_keys():
    api_key = st.secrets.get("MISTRAL_API_KEY", os.getenv("MISTRAL_API_KEY"))
    if api_key:
        os.environ["MISTRAL_API_KEY"] = api_key
    else:
        st.error("MISTRAL_API_KEY is missing.")
        st.stop()


def secret_mode():
    """
    Retrieves passwords to enter secret mode with different prompt and session id only I can enter.

    Returns:
        list: list contains a password to enter the secret mode and a password to get out of it
    """
    secret_mood_in = st.secrets.get("secret_mood_in", os.getenv("secret_mood_in"))
    secret_mood_out = st.secrets.get("secret_mood_out", os.getenv("secret_mood_out"))

    return secret_mood_in, secret_mood_out


def extract_pdf_text(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    pages_text = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            pages_text.append(page_text)

    return "\n".join(pages_text)


def clean_json_response(text: str):
    """
    Cleans the json string response returned by the model and returns a json data.

    Args:
        text (str): The json text returned by the model
    Returns:
        json: json cleaned data
    """
    text = text.strip()

    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    return json.loads(text)


def create_quiz(quiz_data, quiz_index):
    st.subheader("Quiz")

    submitted_key = f"quiz_submitted_{quiz_index}"

    if submitted_key not in st.session_state:
        st.session_state[submitted_key] = False

    for i, q in enumerate(quiz_data):
        st.write(f"### Question {i + 1}")
        st.write(q["question"])

        st.radio(
            "Choose your answer:",
            q["choices"],
            key=f"quiz_{quiz_index}_question_{i}"
        )

    if st.button("Submit Quiz", key=f"submit_quiz_{quiz_index}"):
        st.session_state[submitted_key] = True

    if st.session_state[submitted_key]:
        score = 0
        st.write("## Answers Review")

        for i, q in enumerate(quiz_data):
            user_answer = st.session_state.get(f"quiz_{quiz_index}_question_{i}")
            correct_answer = q["answer"]

            st.write(f"### Question {i + 1}")
            st.write(q["question"])

            if user_answer == correct_answer:
                score += 1
                st.success(f"Correct: {user_answer}")
            else:
                st.error(f"Your answer: {user_answer}")
                st.info(f"Correct answer: {correct_answer}")

            st.write(f"Explanation: {q['explanation']}")

        st.success(f"Your score: {score}/{len(quiz_data)}")


def render_messages():
    """
    Render chat timeline in correct chronological order.
    Supports: user messages, assistant messages, quizzes.
    """

    for index, message in enumerate(st.session_state.messages):

        if message["role"] == "quiz":
            with st.chat_message("assistant"):
                create_quiz(message["content"], index)

        else:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
