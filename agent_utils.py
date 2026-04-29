import streamlit as st

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
import inspect
import tools as tools_module
from langchain_core.tools import BaseTool
from typing import List


def load_tools() -> List[BaseTool]:
    """
    Retrieves all the tools available in tools_module dynamically.

    Returns:
        List[BaseTool]: List of tools the chatbot can use.
    """

    tools = []

    for _, obj in inspect.getmembers(tools_module):
        if isinstance(obj, BaseTool):
            tools.append(obj)

    return tools


@st.cache_resource
def init_agent(model_name: str = "mistral-small-latest"):

    tools = load_tools()

    try:
        model = init_chat_model(model=model_name)

        agent = create_agent(
            model=model,
            checkpointer=InMemorySaver(),
            tools=tools,
        )

        return agent

    except Exception as e:
        st.error(f"Failed to initialize model: {e}")
        st.stop()