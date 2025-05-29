
from sqlalchemy import create_engine, Column, Date, Float, BigInteger, String, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import yfinance as yf
import pandas as pd
from scipy.stats import skew, kurtosis
import numpy as np


TICKERS = ["AAPL", "MSFT", "NVDA", "GOOGL", "META", "AMZN", "TSLA", "HD", 
           "BRK.A", "MA", "V", "UNH", "JNJ", "PG", "KO", "PEP", "COST", 
           "CVX", "XOM", "AVGO"]


START_DATE = "2000-01-01"           
END_DATE = "2025-05-28"             
INTERVAL = "1d"                     




# SQLAlchemy setup
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/yahoo-finance"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

#stocks table
class Stock(Base):
    __tablename__ = 'stocks'
    ticker_id = Column(Integer, autoincrement=True, primary_key=True)  
    ticker_name = Column(String, nullable=False)
    company_name = Column(String, nullable=True)
    sector = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    employees = Column(Integer, nullable=True)

    prices = relationship("StockPrice", back_populates="stock")
    balance_sheet = relationship('StockBalanceSheet', back_populates="stock")
    income_statement = relationship('StockIncomeStatement', back_populates="stock")
    cash_flow = relationship('StockCashFlow', back_populates="stock")


#stock_prices table
class StockPrice(Base):
    __tablename__ = 'stock_prices'
    id = Column(Integer, autoincrement=True, primary_key=True)
    ticker_id = Column(Integer, ForeignKey('stocks.ticker_id'))
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)

    stock = relationship("Stock", back_populates="prices")

    __table_args__ = (UniqueConstraint('ticker_id', 'date', name='_ticker_date_uc'),)



#stock_balance_sheet Table
class StockBalanceSheet(Base):
    __tablename__= 'stock_balance_sheet'
    id = Column(Integer, autoincrement = True, primary_key=True)
    ticker_id = Column(Integer, ForeignKey('stocks.ticker_id'))
    date = Column(Date)
    total_debt = Column(BigInteger)
    stockholders_equity = Column(BigInteger)
    current_assets = Column(BigInteger)
    current_liabilities = Column(BigInteger)
    common_stock_equity = Column(BigInteger)
    shares_issued = Column(BigInteger)
    invested_capital = Column(BigInteger)
    total_assets = Column(BigInteger)

    stock = relationship("Stock", back_populates="balance_sheet")


#stock_income_statement Table
class StockIncomeStatement(Base):
    __tablename__ = 'stock_income_statement'
    id = Column(Integer, autoincrement=True, primary_key=True)
    ticker_id = Column(Integer, ForeignKey('stocks.ticker_id'))
    date = Column(Date)
    net_income = Column(BigInteger)
    total_revenue = Column(BigInteger)
    ebit = Column(BigInteger)
    ebitda = Column(BigInteger)
    operating_income = Column(BigInteger)
    gross_profit = Column(BigInteger)

    stock = relationship("Stock", back_populates="income_statement")


#stock_cash_flow Table
class StockCashFlow(Base):
    __tablename__ = 'stock_cash_flow'
    id = Column(Integer, autoincrement=True, primary_key=True)
    ticker_id = Column(Integer, ForeignKey('stocks.ticker_id'))
    date = Column(Date)
    operating_cashflow = Column(BigInteger)
    capital_expenditure = Column(BigInteger)
    changes_in_cash = Column(BigInteger)
    issuance_of_debt = Column(BigInteger)
    common_stock_issuance = Column(BigInteger)
    depreciation_and_amortization = Column(BigInteger)

    stock = relationship("Stock", back_populates="cash_flow")

    
# Create tables
Base.metadata.drop_all(engine)         #resets the database and drops all the tables
Base.metadata.create_all(engine)


def get_ticker_id(symbol):
    stock = session.query(Stock).filter_by(ticker_name=symbol).first()
    if not stock:
        raise ValueError(f"Stock with ticker '{symbol}' not found.")
    return stock.ticker_id

def safe_int(value):
    try:
        return int(value) if pd.notna(value) else None
    except Exception:
        return None


def fetch_stock_metadata(symbol):
    """
        Fetch stock data from the yahoo finance API.

        TABLE NAME: stocks
    """

    ticker_obj = yf.Ticker(symbol)
    info = ticker_obj.info

    ticker_name = info.get("symbol")
    company_name = info.get("longName") or info.get("shortName")
    sector = info.get("sector")
    industry = info.get("industry")
    employees = info.get("fullTimeEmployees")

    # Ensure stock exists in `stocks` table with metadata
    existing = session.query(Stock).filter_by(ticker_name=symbol).first()
    
    if not existing:
        new_stock = Stock(
            ticker_name=symbol,
            company_name=company_name,
            sector=sector,
            industry=industry,
            employees = employees
        )
        session.add(new_stock)
        session.commit()

    return ticker_obj


def fetch_stock_price(symbol, ticker_obj):
    """
        Inserting stock price data into the database
    """
    ticker_id = get_ticker_id(symbol)
    df = ticker_obj.history(start=START_DATE, end=END_DATE, interval=INTERVAL)

    for date, row in df.iterrows():
        price = StockPrice(
            ticker_id=ticker_id,
            date=date.date(),
            open=float(row['Open']) if pd.notna(row['Open']) else None,
            high=float(row['High']) if pd.notna(row['High']) else None,
            low=float(row['Low']) if pd.notna(row['Low']) else None,
            close=float(row['Close']) if pd.notna(row['Close']) else None,
            volume=int(row['Volume']) if pd.notna(row['Volume']) else None
        )
        session.merge(price)
    session.commit()
    print(f"Inserted {len(df)} price records for {symbol}")

    return df


def fetch_balance_sheet_table(symbol, ticker_obj):
    '''
        Inserting the balance sheet data into the database
    '''
    ticker_id = get_ticker_id(symbol)
    try:
        df = ticker_obj.balance_sheet.T 

        for date, row in df.iterrows():
            record = StockBalanceSheet(
                ticker_id=ticker_id,
                date=pd.to_datetime(date).date(),
                total_debt=safe_int(row.get("Total Debt", 0)),
                stockholders_equity=safe_int(row.get("Total Stockholder Equity", 0)),
                current_assets=safe_int(row.get("Total Current Assets", 0)),
                current_liabilities=safe_int(row.get("Total Current Liabilities", 0)),
                common_stock_equity=safe_int(row.get("Common Stock Equity", 0)),
                shares_issued=safe_int(row.get("Ordinary Shares Number", 0)),
                invested_capital=safe_int(row.get("Invested Capital", 0)),
                total_assets=safe_int(row.get("Total Assets", 0))
            )
            session.merge(record)
        session.commit()

    except Exception as e:
        print(f"Error in balance sheet for {symbol}: {e}")
        session.rollback()
    
def fetch_income_statement_data(symbol, ticker_obj):
    '''
        Inserting the income statement data into the database
    '''
    ticker_id = get_ticker_id(symbol)

    try:
        df = ticker_obj.financials.T
        for date, row in df.iterrows():
            record = StockIncomeStatement(
                ticker_id=ticker_id,
                date=pd.to_datetime(date).date(),
                total_revenue=safe_int(row.get("Total Revenue", 0)),
                gross_profit=safe_int(row.get("Gross Profit", 0)),
                net_income=safe_int(row.get("Net Income", 0)),
                operating_income=safe_int(row.get("Operating Income", 0))
            )
            session.merge(record)
        session.commit()

    except Exception as e:
        print(f"Error in income statement for {symbol}: {e}")
        session.rollback()

def fetch_cashflow_data(symbol, ticker_obj):
    '''
        Inserting the cashflow data into the database.
    '''
    ticker_id = get_ticker_id(symbol)
    
    try:
        df = ticker_obj.cashflow.T
        for date, row in df.iterrows():
            record = StockCashFlow(
                ticker_id=ticker_id,
                date=pd.to_datetime(date).date(),
                operating_cashflow = safe_int(row.get('Operating Cash Flow')),
                capital_expenditure = safe_int(row.get('Capital Expenditure')),
                changes_in_cash = safe_int(row.get('Changes In Cash')),
                issuance_of_debt = safe_int(row.get('Issuance Of Debt')),
                common_stock_issuance = safe_int(row.get('Common Stock Issuance')),
                depreciation_and_amortization = safe_int(row.get('Depreciation And Amortization'))

            )
            session.merge(record)
        session.commit()

    except Exception as e:
        print(f"Error in cash flow for {symbol}: {e}")
        session.rollback()

def process_symbol(symbol):
    try:  
        ticker_obj = fetch_stock_metadata(symbol)
        fetch_stock_price(symbol, ticker_obj)
        fetch_balance_sheet_table(symbol, ticker_obj)
        fetch_income_statement_data(symbol, ticker_obj)
        fetch_cashflow_data(symbol, ticker_obj)

    except Exception as e:
        print(f"Error processing {symbol}: {e}")
        session.rollback()

for symbol in TICKERS:
    process_symbol(symbol)


session.close()
