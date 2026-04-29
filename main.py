from prompts import load_prompts
from utils import *
from agent_utils import init_agent
from dotenv import load_dotenv

load_dotenv()

setup_api_keys()

user_id = setup_cookies()

secret_mood_in, secret_mood_out = secret_mode()

pdf_quiz_generation_prompt, chatbot_prompt, secret_prompt = load_prompts()


def init_session_state_vars():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = user_id

    if "secret_thread_id" not in st.session_state:
        st.session_state.secret_thread_id = "secret_thread_id"

    if "secret" not in st.session_state:
        st.session_state.secret = "False"



def main():
    st.title("Quiz AI Generator")

    model_option = st.sidebar.selectbox(
        "Choose a model",
        ["mistral-small-latest", "mistral-medium-latest", "mistral-large-latest"]
    )

    init_session_state_vars()

    chat_agent = init_agent(model_option)

    if chat_agent is None:
        st.error("Model initialization failed")
        return

    render_messages()

    prompt = st.chat_input(
        "Ask for question generation, e.g. 'Generate 10 questions'",
        accept_file=True,
        file_type=["pdf"],
    )

    if prompt:

        user_text = prompt.text or ""

        # Store user message
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

                    # Secret mode activation
                    if user_text.lower() == secret_mood_in:
                        st.session_state.secret = "True"

                    # Secret mode logic
                    if st.session_state.secret == "True":

                        prompt_template = secret_prompt.format(
                            user_text=user_text
                        )

                        response = chat_agent.invoke(
                            {
                                "messages": [
                                    {"role": "user", "content": prompt_template}
                                ]
                            },
                            config={
                                "configurable": {
                                    "thread_id": st.session_state.secret_thread_id
                                }
                            }
                        )

                        if user_text.lower() == secret_mood_out:
                            st.session_state.secret = "False"

                    else:

                        # PDF quiz generation
                        if prompt.files:

                            pdf_text = extract_pdf_text(prompt.files[0])

                            prompt_template = pdf_quiz_generation_prompt.format(
                                user_text=user_text,
                                pdf_text=pdf_text
                            )

                        else:

                            prompt_template = chatbot_prompt.format(
                                user_text=user_text
                            )

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

                    # Normal chat response
                    if not prompt.files:

                        message_placeholder.markdown(assistant_text)

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": assistant_text
                        })

                    # Quiz response
                    else:

                        quiz_json = clean_json_response(assistant_text)

                        message_placeholder.success(
                            "Quiz generated successfully!"
                        )

                        st.session_state.messages.append({
                            "role": "quiz",
                            "content": quiz_json
                        })

                        st.rerun()

            except Exception as e:

                error_text = f"Sorry, I encountered an error: {str(e)}"

                st.error(error_text)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_text
                })


if __name__ == "__main__":
    main()