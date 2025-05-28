import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from langchain.agents import create_sql_agent, AgentType
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI

# ---------- Streamlit Config ----------
st.set_page_config(page_title="Chat with Local PostgreSQL")
st.title("💬 Talk to Your PostgreSQL Finance Database")

st.markdown("""
Ask questions like:
- "What is the average closing price of AAPL?"
- "Show TSLA's income statements for 2023."
""")

# ---------- Session State for Chat ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- OpenAI API Key Input ----------
openai_api_key = st.text_input("🔑 OpenAI API Key", type="password")

if not openai_api_key:
    st.warning("Please enter your OpenAI API key.")
    st.stop()

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
    return_intermediate_steps=True
)

# ---------- Display Chat History ----------
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(chat["question"])
    with st.chat_message("assistant"):
        st.markdown(chat["answer"])
        with st.expander("🔍 Show SQL Query"):
            if chat["sql"]:
                st.code(chat["sql"], language="sql")
            else:
                st.info("No SQL query was detected.")

# ---------- Chat Input ----------
user_question = st.chat_input("Ask your financial database something...")

# ---------- Process New Input ----------
if user_question:
    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = agent.invoke({"input": user_question})
                answer = result["output"]

                # Extract SQL query from intermediate steps
                sql_query = ""
                steps = result.get("intermediate_steps", [])
                for step in steps:
                    if isinstance(step, tuple):
                        thought = str(step[0])
                        if "SELECT" in thought.upper():
                            sql_query = thought.strip()
                            break

                st.markdown(answer)
                with st.expander("🔍 Show SQL Query"):
                    if sql_query:
                        st.code(sql_query, language="sql")
                    else:
                        st.info("No SQL query was generated.")

                # Save interaction
                st.session_state.chat_history.append({
                    "question": user_question,
                    "answer": answer,
                    "sql": sql_query
                })

            except Exception as e:
                st.error(f"❌ Error: {e}")
