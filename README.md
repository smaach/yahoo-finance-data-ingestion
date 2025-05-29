# Financial Data ETL Pipeline + Streamlit Interface

This project is a **complete ETL (Extract, Transform, Load) project** for downloading and storing structured financial data from Yahoo Finance into a **PostgreSQL** database — and provides a **Streamlit interface** that lets users explore and query the data using natural language processing utilizing the capability of Langchain, and Open AI API.

---

##  What It Does?

-  **Extracts** real-time financial data for major S&P 500 stocks via the `yfinance` API
-  **Transforms** it into structured formats of 5 main tables which includes information of stocks, stock prices, balance sheets, income statement, and cash flows
-  **Loads** the data into a normalized **PostgreSQL** schema using [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
-  **Provides a chat-based interface** via Streamlit + LangChain to interact with your database using natural english language.

---

##  Use Cases

- Build your own financial database for analytics purposes, and analysing questions like Return-on-Equity (ROE), Gross Profit Margin, Net Income etc.
- Streamlit provides a natural-language interface to query stock related data
- Educational tool for learning financial statements, ETL operations and SQL-based query operation.

---

## 🗂️ Project Structure

├── etl-ops.py # ETL pipeline: Fetches and loads data from Yahoo Finance to PostgreSQL
├── streamlit-ops.py # Streamlit app: Natural language chat with your database
├── requirements.txt # Python dependencies
└── README.md # Project documentation
