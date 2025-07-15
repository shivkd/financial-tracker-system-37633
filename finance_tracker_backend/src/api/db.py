"""
Database setup, ORM models, and utility functions for the Finance Tracker Backend.

Handles database connections, ORM mappings, and helper functions for operations.
"""

from sqlalchemy import (Column, Integer, String, Float, Boolean, ForeignKey, Date, Enum)
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.sql import func
from passlib.context import CryptContext
import enum
import os

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./finance_tracker.db")

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------- ORM Models -----------------

class TransactionTypeEnum(str, enum.Enum):
    income = "income"
    expense = "expense"

# PUBLIC_INTERFACE
class User(Base):
    """User database model."""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)

    transactions = relationship("Transaction", back_populates="user")
    budgets = relationship("Budget", back_populates="user")

# PUBLIC_INTERFACE
class Category(Base):
    """Expense/Income category model."""
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    is_income = Column(Boolean, default=False)

    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")

# PUBLIC_INTERFACE
class Transaction(Base):
    """Transaction model for financial entry."""
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    type = Column(Enum(TransactionTypeEnum), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    description = Column(String, nullable=True)
    date = Column(Date, default=func.current_date())
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

# PUBLIC_INTERFACE
class Budget(Base):
    """Budget model."""
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    amount = Column(Float, nullable=False)
    period = Column(String, nullable=False)

    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")
# ---------------- Utility Functions -----------------

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# PUBLIC_INTERFACE
async def get_db():
    """
    Dependency for retrieving a SQLAlchemy AsyncSession, to be used with FastAPI.
    Ensures session is always closed cleanly.
    """
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# PUBLIC_INTERFACE
def get_password_hash(password: str) -> str:
    """Hash a plain password."""
    return pwd_context.hash(password)

# PUBLIC_INTERFACE
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that a plain password matches hashed."""
    return pwd_context.verify(plain_password, hashed_password)

# PUBLIC_INTERFACE
async def get_user_by_username(db: AsyncSession, username: str):
    """Fetch a user by username."""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

# PUBLIC_INTERFACE
async def get_user_by_email(db: AsyncSession, email: str):
    """Fetch a user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

# PUBLIC_INTERFACE
async def create_database_and_tables():
    """Creates all tables (async)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
