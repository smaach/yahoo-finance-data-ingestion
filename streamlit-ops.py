import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from langchain.agents import create_sql_agent, AgentType
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI

# ---------- Streamlit Page Config ----------
st.set_page_config(
    page_title="PostgreSQL Chat",
    layout="centered"
)

# ---------- Sidebar for Config ----------
with st.sidebar:
    st.title("Settings")
    openai_api_key = st.text_input("OpenAI API Key", type="password", help="Paste your OpenAI key here.")
    st.markdown("---")
    st.markdown("Built with using LangChain + Streamlit")

if not openai_api_key:
    st.warning("Enter your OpenAI API key in the sidebar to get started.")
    st.stop()

# ---------- Title & Instructions ----------
st.markdown("<h1 style='text-align: center;'> Chat with Your Finance Database</h1>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
Ask natural language questions like:
<ul style="list-style-position: inside; text-align: left; display: inline-block;">
    <li>What is the average closing price of AAPL?</li>
    <li>Show TSLA's income statements for 2023.</li>
</ul>
</div>
""", unsafe_allow_html=True)

# ---------- Session State ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- Database Setup ----------
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/yahoo-finance"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()
db = SQLDatabase(engine)

# ---------- LangChain Setup ----------
llm = ChatOpenAI(api_key=openai_api_key, model="gpt-3.5-turbo", temperature=0)
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    return_intermediate_steps=True,
    handle_parsing_errors=True
)

# ---------- Display Chat History ----------
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(chat["question"])
    with st.chat_message("assistant"):
        st.markdown(chat["answer"])

# ---------- Chat Input ----------
user_question = st.chat_input("Ask something...")

# ---------- Process New Input ----------
if user_question:
    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = agent.invoke({"input": user_question})
                answer = result["output"]

                st.markdown(answer)

                # Save chat
                st.session_state.chat_history.append({
                    "question": user_question,
                    "answer": answer
                })

            except Exception as e:
                st.error(f"Error: {e}")
