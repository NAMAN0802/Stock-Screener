from sqlalchemy import Column, Integer, String, ForeignKey, Index, create_engine
from sqlalchemy.orm import declarative_base, relationship, backref
from base import Base
from models import Stocks, Ratios, ProfitLoss, Shareholding, CashFlow, BalanceSheet
import os
from dotenv import load_dotenv
load_dotenv()

class Database:
    def __init__(self):
        self.engine = create_engine("postgresql://naman:password@localhost:5432/stock_screener")
        # DB_HOST = os.getenv("DB_HOST", "")
        # DB_NAME = os.getenv("DB_NAME", "")
        # DB_USER = os.getenv("DB_USER", "")
        # DB_PASSWORD = os.getenv("DB_PASSWORD", "") # Aapko isko securely manage karna chahiye
        # DB_PORT = os.getenv("DB_PORT", "")

        # self.engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        with self.engine.connect() as conn:
            print("Connected to database")

    def create_tables(self):
        Base.metadata.create_all(self.engine)


if __name__ == "__main__":
    db = Database()
    
