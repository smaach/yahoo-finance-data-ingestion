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

## Project Structure

1) ### etl-ops.py
   
   ETL pipeline: Fetches and loads data from Yahoo Finance to PostgreSQL

    * contain 5 main classes `Stock`, `StockPrice`, `StockBalanceSheet`, `StockIncomeStatement`, `StockCashFlow` for the 5 tables present in the database.
    * contains 6 main functions that extracts the data from `yfinance` API and loads the data into `PostgreSQL` database.
      
3) ### streamlit-ops.py
   
   Streamlit app: Natural language chat with your database

    * contains the code to create a simple streamlit application
      
5) ### requirements.txt
    * contains all the python libraries used in the project

## Table Structure

Below is a simplified version of the PostgreSQL schema used in this project, considering the a very basic star schema.

```sql
-- stocks table
CREATE TABLE stocks (
    ticker_id SERIAL PRIMARY KEY,
    ticker_name TEXT NOT NULL,
    company_name TEXT,
    sector TEXT,
    industry TEXT,
    employees INTEGER
);

-- stock_prices table
CREATE TABLE stock_prices (
    id SERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES stocks(ticker_id),
    date DATE,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT,
    UNIQUE(ticker_id, date)
);

-- stock_income_statement table
CREATE TABLE stock_income_statement (
    id SERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES stocks(ticker_id),
    date DATE,
    total_revenue BIGINT,
    gross_profit BIGINT,
    net_income BIGINT,
    operating_income BIGINT,
    ebit BIGINT,
    ebitda BIGINT
);

-- stock_balance_sheet table
CREATE TABLE stock_balance_sheet (
    id SERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES stocks(ticker_id),
    date DATE,
    total_debt BIGINT,
    stockholders_equity BIGINT,
    current_assets BIGINT,
    current_liabilities BIGINT,
    common_stock_equity BIGINT,
    shares_issued BIGINT,
    invested_capital BIGINT,
    total_assets BIGINT
);

-- stock_cash_flow table
CREATE TABLE stock_cash_flow (
    id SERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES stocks(ticker_id),
    date DATE,
    operating_cashflow BIGINT,
    capital_expenditure BIGINT,
    changes_in_cash BIGINT,
    issuance_of_debt BIGINT,
    common_stock_issuance BIGINT,
    depreciation_and_amortization BIGINT
);
```


