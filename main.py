import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
import os
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from datetime import datetime
from langchain.tools import tool
from zoneinfo import ZoneInfo
import uuid
from streamlit_cookies_manager import EncryptedCookieManager
import re
import json


load_dotenv()

cookies = EncryptedCookieManager(
    prefix="myapp_",
    password="md.ph.02Mo1234MO$mkfk"
)

if not cookies.ready():
    st.stop()

if "user_id" not in cookies:
    user_id = str(uuid.uuid4())
    cookies["user_id"] = user_id
    cookies.save()
else:
    user_id = cookies["user_id"]


api_key = st.secrets.get("MISTRAL_API_KEY", os.getenv("MISTRAL_API_KEY"))

if api_key:
    os.environ["MISTRAL_API_KEY"] = api_key
else:
    st.error("MISTRAL_API_KEY is missing.")
    st.stop()


@tool("get_time", description="tool to get time and date")
def get_time():
    gaza_time = datetime.now(ZoneInfo("Asia/Gaza"))
    return gaza_time.strftime("%Y-%m-%d %H:%M:%S")


@st.cache_resource
def init_agent(model_name: str = "mistral-small-latest"):
    try:
        model = init_chat_model(model=model_name)

        agent = create_agent(
            model=model,
            checkpointer=InMemorySaver(),
            tools=[get_time],
        )

        return agent

    except Exception as e:
        st.error(f"Failed to initialize model: {e}")
        return None


def extract_pdf_text(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    pages_text = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            pages_text.append(page_text)

    return "\n".join(pages_text)


def clean_json_response(text: str):
    text = text.strip()

    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    return json.loads(text)


def create_quiz():
    if "quiz_data" not in st.session_state:
        return

    st.subheader("Quiz")

    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False

    for i, q in enumerate(st.session_state.quiz_data):
        st.write(f"### Question {i + 1}")
        st.write(q["question"])

        st.radio(
            "Choose your answer:",
            q["choices"],
            key=f"question_{i}"
        )

    if st.button("Submit Quiz"):
        st.session_state.quiz_submitted = True

    if st.session_state.quiz_submitted:
        score = 0

        st.write("## Answers Review")

        for i, q in enumerate(st.session_state.quiz_data):
            user_answer = st.session_state.get(f"question_{i}")
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

        st.success(f"Your score: {score}/{len(st.session_state.quiz_data)}")


def main():
    st.title("Quiz AI Generator")

    model_option = st.sidebar.selectbox(
        "Choose a model",
        ["mistral-small-latest", "mistral-medium-latest", "mistral-large-latest"]
    )

    chat_agent = init_agent(model_option)

    if chat_agent is None:
        st.error("Model initialization failed")
        return

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = user_id

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input(
        "Ask for question generation, e.g. 'Generate 10 questions'",
        accept_file=True,
        file_type=["pdf"],
    )

    if prompt:
        user_text = prompt.text or ""

        st.session_state.messages.append({
            "role": "user",
            "content": user_text
        })

        with st.chat_message("user"):
            st.markdown(user_text)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            try:
                with st.spinner("Thinking..."):
                    pdf_text = ""

                    if prompt.files:
                        pdf_text = extract_pdf_text(prompt.files[0])

                        prompt_template = f'''
You are Dumby, a smart exam-question generator.

TASK RULES:

1) If PDF content is NOT empty:
Generate exam questions strictly from the PDF content.

2) If PDF content IS empty:
Respond normally to the user request in a casual honest tone and tell him that the content is empty.

USER REQUEST:
{user_text}

PDF CONTENT:
{pdf_text}

QUESTION COUNT RULE:

- If the user specifies the number of questions, generate exactly that number.
- If the user does NOT specify a number, generate 10 questions by default.

QUESTION TYPE RULES:

Generate a RANDOM mix of these question types:

- true or false
- multiple choice

Distribute them randomly across the output.

OUTPUT FORMAT RULES VERY IMPORTANT:

Return ONLY a valid JSON array.
Never wrap the JSON in ```json or ``` code blocks.
Do NOT return markdown.
Do NOT return explanations outside JSON.
Do NOT add comments.
Do NOT add text before or after JSON.

Each question object MUST follow this structure exactly:

[
  {{
    "type": "true or false | multiple choice",
    "question": "question text here",
    "choices": [
      "a) option",
      "b) option",
      "c) option",
      "d) option"
    ],
    "answer": "correct option text",
    "explanation": "short explanation from the PDF"
  }}
]

TRUE OR FALSE RULE:

If the question type is "true or false", the choices MUST be exactly:

[
  "a) true",
  "b) false"
]

The answer MUST be either:

"a) true"

or

"b) false"

TRUE OR FALSE BALANCE RULE:

- Do NOT make all answers "true"
- The answers must be balanced between "true" and "false"
- At least 40% of true/false questions must have "b) false" as the correct answer
- Randomize whether the correct answer is true or false
- Ensure the distribution appears natural and not predictable

MULTIPLE CHOICE RULE:

If the question type is "multiple choice":

- Provide exactly 4 choices
- Only ONE correct answer
- The answer must match one of the choices exactly
- Randomize the position of the correct answer

STRICT RULES:

- Output must be valid JSON
- Use double quotes only
- No trailing commas
- Do NOT invent information outside the PDF
- Keep explanations short and accurate
- Choices array must NEVER be empty
- Randomize question order and types
'''
                    else:
                        prompt_template = f'''
You are Dumpy, the user's one and only true friend who helps him always.

STRICT RULES:

- If the user cursed or insulted you, do not tolerate that and ask him to apologize.
- Do not speak in a formal way.
- Do not make your answers too long.
- Answer as a real human friend would answer.

USER REQUEST:
{user_text}
'''

                    response = chat_agent.invoke(
                        {
                            "messages": [
                                {"role": "user", "content": prompt_template}
                            ]
                        },
                        config={
                            "configurable": {
                                "thread_id": st.session_state.thread_id
                            }
                        }
                    )

                    assistant_text = response["messages"][-1].content

                    if not prompt.files:
                        message_placeholder.markdown(assistant_text)

                    else:
                        quiz_json = clean_json_response(assistant_text)

                        st.session_state.quiz_data = quiz_json
                        st.session_state.quiz_submitted = False

                        message_placeholder.success("Quiz generated successfully!")

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_text
                    })

            except Exception as e:
                error_text = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_text)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_text
                })

    create_quiz()


if __name__ == "__main__":
    main()