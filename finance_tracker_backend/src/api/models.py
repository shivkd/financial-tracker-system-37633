"""
Data Models and Schemas for the Finance Tracker Backend.

Defines Pydantic models for requests and responses, and
ORM-compatible SQLAlchemy models for persistence.

PUBLIC_INTERFACE: All exported classes are documented.
"""

from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


# ---------- Enums ----------

class TransactionType(str, Enum):
    expense = "expense"
    income = "income"


# ---------- Pydantic Schemas ----------

# PUBLIC_INTERFACE
class UserCreate(BaseModel):
    """Request model for registering a new user."""
    username: str = Field(..., description="Username for new user")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password (plain text)")

# PUBLIC_INTERFACE
class UserLogin(BaseModel):
    """Request model for user login."""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password (plain text)")

# PUBLIC_INTERFACE
class UserOut(BaseModel):
    """Response model for user details."""
    id: int
    username: str
    email: EmailStr

    model_config = {
        'from_attributes': True
    }

# PUBLIC_INTERFACE
class Token(BaseModel):
    """JWT access token response."""
    access_token: str
    token_type: str

# PUBLIC_INTERFACE
class CategoryIn(BaseModel):
    """Request model for category creation or edit."""
    name: str = Field(..., description='Name of the category')
    is_income: Optional[bool] = Field(default=False, description='True if income category, else expense')

# PUBLIC_INTERFACE
class CategoryOut(BaseModel):
    """Response model for an expense/income category."""
    id: int
    name: str
    is_income: bool

    model_config = {
        'from_attributes': True
    }

# PUBLIC_INTERFACE
class TransactionIn(BaseModel):
    """Request model for creating or editing a transaction."""
    amount: float = Field(description='Amount of transaction')
    type: TransactionType = Field(description='Type of transaction (expense/income)')
    category_id: int = Field(description='Category ID')
    description: Optional[str] = None
    date: Optional[date] = None

# PUBLIC_INTERFACE
class TransactionOut(BaseModel):
    """Response model for a transaction."""
    id: int
    user_id: int
    amount: float
    type: TransactionType
    category: CategoryOut
    description: Optional[str]
    date: date

    class Config:
        orm_mode = True

# PUBLIC_INTERFACE
class BudgetIn(BaseModel):
    """Request model for setting or updating a budget."""
    category_id: int = Field(..., description="Category to apply budget to")
    amount: float = Field(..., description="Budgeted amount")
    period: str = Field(..., description="Budget period, e.g., 'monthly', 'weekly', etc.")

# PUBLIC_INTERFACE
class BudgetOut(BaseModel):
    """Response model for a budget record."""
    id: int
    user_id: int
    category: CategoryOut
    amount: float
    period: str

    class Config:
        orm_mode = True

# PUBLIC_INTERFACE
class DashboardSummary(BaseModel):
    """Model for the financial overview dashboard."""
    total_income: float
    total_expense: float
    balance: float
    top_expenses: List[TransactionOut]
    top_income: List[TransactionOut]

# PUBLIC_INTERFACE
class ReportRequest(BaseModel):
    """Request model for generating reports."""
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)
    group_by: Optional[str] = Field(default="category", description="How to group: 'category', 'month', etc.")

# PUBLIC_INTERFACE
class ReportResult(BaseModel):
    """Response for reports."""
    labels: list
    values: list
    totals: dict

