# Financial Data ETL Pipeline + Streamlit Interface

This project is a **complete ETL (Extract, Transform, Load) pipeline** for downloading and storing structured financial data from Yahoo Finance into a **PostgreSQL** database — and comes with an optional **Streamlit interface** that lets users explore and query the data using natural language.

---

## ⚙️ What It Does

- 🔁 **Extracts** real-time financial data for major S&P 500 stocks via the `yfinance` API
- 🧱 **Transforms** it into structured formats (prices, balance sheets, income statements, cash flows)
- 🗄️ **Loads** the data into a normalized **PostgreSQL** schema using SQLAlchemy
- 💬 **Provides a chat-based interface** via Streamlit + LangChain to interact with your database using plain English

---

## 💡 Use Cases

- Automated financial data collection and storage
- Build your own financial database for analytics or modeling
- Natural-language interface to query stock performance
- Educational tool for learning financial statements and SQL-based data pipelines

---

## 🗂️ Project Structure

