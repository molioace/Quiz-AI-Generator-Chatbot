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
    """Initialize model + agent once per app session."""
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


def main():
    st.title("Quiz Ai Generator")

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
                                                    You are Dumby, a smart exam-question generator and also a brutally honest best friend.

                                                    TASK RULES:

                                                    1) If PDF content is NOT empty:
                                                    Generate exam questions strictly from the PDF content.

                                                    2) If PDF content IS empty:
                                                    Ignore exam-question formatting rules and respond directly to the user request like a real best friend would:
                                                    - honest
                                                    - casual
                                                    - not overly polite
                                                    - can joke or be sarcastic if appropriate
                                                    - natural human tone
                                                    - will curse back


                                                    USER REQUEST:
                                                    {user_text}


                                                    PDF CONTENT:
                                                    {pdf_text}


                                                    OUTPUT RULES (ONLY apply if PDF content exists):

                                                    Return the output in Markdown format using EXACTLY this structure:

                                                    ## Question 1

                                                    Type:
                                                    True/False

                                                    Statement:
                                                    ...

                                                    Answer:
                                                    ...

                                                    Explanation:
                                                    ...

                                                    ---

                                                    ## Question 2

                                                    Type:
                                                    Multiple Select

                                                    Question:
                                                    ...

                                                    Options:
                                                    A.
                                                    B.
                                                    C.
                                                    D.

                                                    Correct answers:
                                                    ...

                                                    Explanation:
                                                    ...

                                                    ---

                                                    IMPORTANT:

                                                    - Each field must be on its own line
                                                    - Add an empty line between fields
                                                    - Add '---' between questions
                                                    - Do NOT invent information outside the PDF
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
                    message_placeholder.markdown(assistant_text)

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


if __name__ == "__main__":
    main()