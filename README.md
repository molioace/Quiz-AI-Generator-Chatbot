🧠 Quiz AI Generator Chatbot

An intelligent Streamlit chatbot that generates quizzes from PDFs or user prompts using LangChain agents, Mistral models, and LangGraph memory, with interactive quiz rendering inside the chat timeline.

🚀 Features
Generate quizzes from uploaded PDFs
Ask the chatbot for custom question sets
Interactive quiz interface inside chat
Persistent user sessions using encrypted cookies
LangGraph thread-based memory support
Secret mode conversation channel
Dynamic tool loading system
Time-by-city tool integration
Clean chat timeline rendering (messages + quizzes inline)
🧩 Tech Stack

Frontend

Streamlit

LLM & Agents

LangChain
LangGraph
Mistral API

Memory

Thread-based conversational memory

Utilities

Encrypted cookie session tracking
PDF parsing with pypdf
Dynamic tool discovery
📂 Project Structure
chatbot/
│
├── main.py
├── agent_utils.py
├── utils.py
├── prompts.py
├── tools.py
├── requirements.txt
└── README.md

main.py
Controls UI flow, chat logic, quiz insertion, and agent interaction

agent_utils.py
Initializes LangChain agent with tools and memory checkpointing

utils.py
Helper utilities:

cookie manager
secret mode
PDF extraction
JSON cleaning
quiz rendering

prompts.py
Stores reusable LLM prompt templates

tools.py
Dynamic LangChain tools (e.g., city time lookup)

🧪 Example Usage
