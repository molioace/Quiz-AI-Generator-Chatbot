# 🧠 Quiz AI Generator Chatbot

An intelligent Streamlit chatbot that generates quizzes from PDFs or user prompts using **LangChain agents**, **Mistral models**, and **LangGraph memory**, with interactive quiz rendering directly inside the chat timeline.

🌐 **Try the live app here:**  
https://chatbot-9be8k3hrzzo7xdspk2v5y9.streamlit.app/

---

## 🚀 Features

- Generate quizzes from uploaded PDFs
- Generate custom quiz questions from user prompts
- Interactive quiz interface embedded directly inside chat
- Persistent user sessions using encrypted cookies
- Thread-based conversational memory with LangGraph
- Dynamic tool loading system
- City-based time lookup tool
- Clean chat timeline rendering (messages + quizzes inline)

---

## 🧩 Tech Stack

**Frontend**
- Streamlit

**LLM & Agents**
- LangChain
- LangGraph
- Mistral API

**Utilities**
- Encrypted cookie session tracking
- PDF parsing with `pypdf`
- Dynamic tool discovery

---

## 📂 Project Structure

```markdown
chatbot/
│
├── main.py
├── agent_utils.py
├── utils.py
├── prompts.py
├── tools.py
├── requirements.txt
└── README.md

```
### File Roles

**main.py**  
Controls UI flow, chat logic, quiz insertion, and agent interaction.

**agent_utils.py**  
Initializes the LangChain agent with tools and memory checkpointing.

**utils.py**  
Helper utilities:
- cookie manager
- PDF extraction
- JSON cleaning
- quiz rendering

**prompts.py**  
Stores reusable LLM prompt templates.

**tools.py**  
Dynamic LangChain tools (example: city time lookup).

---

## 🧪 Example Usage

Ask:


Generate 5 questions about machine learning


Or upload a PDF and ask:


Generate 10 quiz questions from this document


The chatbot returns an interactive quiz directly inside the conversation.

---

## 🛠 Installation

Clone the repository:


git clone https://github.com/molioace/chatbot.git

cd chatbot


Install dependencies:


pip install -r requirements.txt


Run the app:


streamlit run main.py


---

## 🔑 Environment Variables

Create a `.env` file in the project root:


MISTRAL_API_KEY=your_api_key_here
COOKIES_PASSWORD=your_cookie_secret


---

## 🧠 Agent Architecture

The chatbot uses:


LangChain Agent
↓
Dynamic Tool Loader
↓
LangGraph Memory Checkpointer
↓
Thread-based Session Storage


Each user session receives a unique ID via encrypted cookies.

---

## 🧩 Dynamic Tool System

Tools are automatically loaded from:


tools.py


Example:

```python
@tool("get_time")
def get_time(city: str):

New tools are registered automatically without modifying agent code.

```
## 📊 Quiz Rendering Pipeline
PDF / user request
        ↓
LLM generates JSON quiz
        ↓
clean_json_response()
        ↓
stored in session_state.messages
        ↓
rendered inline in chat timeline

Maintains correct ordering:

user message
assistant response
quiz
next user message
## 🌍 Example Tool Usage

Ask:

What time is it in Cairo?

Agent calls:

get_time("Cairo")

Returns localized time instantly.

## 🧠 Memory Handling

Uses LangGraph checkpoint system:

thread_id = user_cookie_id

Allows persistent conversation context per user session.

## 📌 Requirements

Core dependencies:

streamlit
langchain
langchain-core
langgraph
langchain-mistralai
python-dotenv
pypdf
streamlit-cookies-manager
## 🎯 Future Improvements

Planned upgrades:

vector database memory (RAG)
quiz scoring analytics dashboard
export quiz to PDF
multilingual quiz generation
adaptive difficulty quizzes
## 👤 Author

Mohammed Sabbah

AI Engineer | LLM Applications | LangChain | Agent Systems

GitHub:
https://github.com/molioace
