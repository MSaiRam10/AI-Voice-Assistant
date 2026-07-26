from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import TypedDict
import os
from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import HumanMessage, SystemMessage
import psycopg

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")

class VoiceState(TypedDict):
    question: str
    messages: list
    answer: str
DB_URL = os.getenv("DATABASE_URL")
conn = psycopg.connect(DB_URL, autocommit=True)
memory = PostgresSaver(conn)
memory.setup()

def chat_node(state: VoiceState):
    question = state["question"]
    messages = state.get("messages", [])
    messages.append(HumanMessage(content=question))
    response = llm.invoke(messages)
    messages.append(response)
    return {"answer": response.content, "messages": messages}

graph = StateGraph(VoiceState)

graph.add_node("chat", chat_node)

graph.set_entry_point("chat")

graph.add_edge("chat", END)

agent = graph.compile(checkpointer=memory)