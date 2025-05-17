# %%
from sqlalchemy import create_engine, Column, Date, Float, BigInteger, String, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import yfinance as yf
import pandas as pd
from scipy.stats import skew, kurtosis
import numpy as np

# %%
# ------------------- USER CONFIGURATION ------------------- #
TICKERS = ["AAPL", "TSLA", "MSFT"]  # Add as many tickers as you want

# Choose either (period) or (start + end)
USE_PERIOD = False                  # Set to True to use period instead of start/end
PERIOD = "3mo"                      # Only used if USE_PERIOD = True
START_DATE = "2023-01-01"           # Only used if USE_PERIOD = False
END_DATE = "2023-12-31"             # Only used if USE_PERIOD = False

INTERVAL = "1d"                     # Examples: '1d', '1wk', '1mo'
# ---------------------------------------------------------- #

# %%
#Base.metadata.drop_all(engine)

# %%
# SQLAlchemy setup
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/yahoo-finance"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# STOCKS table
class Stock(Base):
    __tablename__ = 'stocks'
    ticker = Column(String, primary_key=True)  
    company_name = Column(String, nullable=True)
    sector = Column(String, nullable=True)
    industry = Column(String, nullable=True)

    prices = relationship("StockPrice", back_populates="stock")
    stats = relationship("StockStats", uselist=False, back_populates="stock")


# STOCK PRICES table
class StockPrice(Base):
    __tablename__ = 'stock_prices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, ForeignKey('stocks.ticker'))
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)

    stock = relationship("Stock", back_populates="prices")

    __table_args__ = (UniqueConstraint('ticker', 'date', name='_ticker_date_uc'),)

class StockStats(Base):
    __tablename__ = 'stock_statistics'
    ticker = Column(String, ForeignKey('stocks.ticker'), primary_key=True)
    start_date = Column(Date)
    end_date = Column(Date)
    mean_close = Column(Float)
    std_close = Column(Float)
    skew_close = Column(Float)
    kurt_close = Column(Float)
    min_close = Column(Float)
    max_close = Column(Float)
    daily_volatility = Column(Float)

    stock = relationship("Stock", back_populates="stats")

# Create tables
Base.metadata.create_all(engine)

# %%
for symbol in TICKERS:
    try:
        print(f"Processing {symbol}...")

        # Fetch metadata from yfinance
        ticker_obj = yf.Ticker(symbol)
        info = ticker_obj.info  # Pulls metadata

        # Extract metadata safely
        company_name = info.get("longName") or info.get("shortName")
        sector = info.get("sector")
        industry = info.get("industry")

        # Ensure stock exists in `stocks` table with metadata
        existing = session.query(Stock).filter_by(ticker=symbol).first()
        if not existing:
            new_stock = Stock(
                ticker=symbol,
                company_name=company_name,
                sector=sector,
                industry=industry
            )
            session.add(new_stock)
            session.commit()

        # Get price data
        df = ticker_obj.history(start=START_DATE, end=END_DATE, interval=INTERVAL)

        if df.empty:
            print(f"No data for {symbol}, skipping.")
            continue

        # Insert price data
        for date, row in df.iterrows():
            price = StockPrice(
                ticker=symbol,
                date=date.date(),
                open=float(row['Open']) if pd.notna(row['Open']) else None,
                high=float(row['High']) if pd.notna(row['High']) else None,
                low=float(row['Low']) if pd.notna(row['Low']) else None,
                close=float(row['Close']) if pd.notna(row['Close']) else None,
                volume=int(row['Volume']) if pd.notna(row['Volume']) else None
            )

            session.merge(price)  # Upsert

        session.commit()
        print(f"Inserted data for {symbol}")


        prices = df['Close'].dropna()

        if len(prices) > 10:  # Avoid unreliable stats
            returns = prices.pct_change().dropna()
            stats_record = StockStats(
                ticker=symbol,
                start_date=prices.index[0].date(),
                end_date=prices.index[-1].date(),
                mean_close=float(prices.mean()),
                std_close=float(prices.std()),
                skew_close=float(skew(prices, nan_policy='omit')),
                kurt_close=float(kurtosis(prices, nan_policy='omit')),
                min_close=float(prices.min()),
                max_close=float(prices.max()),
                daily_volatility=float(returns.std())
            )

            session.merge(stats_record)
            session.commit()

            print(f"Stats computed for {symbol}")
        else:
            print(f"Not enough data to compute stats for {symbol}")

    except Exception as e:
        print(f"Error for {symbol}: {e}")
        session.rollback()



session.close()


# %%
ticker = yf.Ticker('MSFT')

# %%
ticker.balance_sheet


#

# %%
ticker.info

# %%
ticker.financials

# %%
ticker.cashflow

# %%
ticker.income_stmt

# %%


# %%
ticker.shares


