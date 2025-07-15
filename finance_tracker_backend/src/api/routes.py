"""
API Endpoints for the Finance Tracker Backend.

Includes: Authentication, Transactions, Categories, Budgets, Reports, and Dashboard Summary.

Routers are mounted to the main FastAPI app in main.py.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date

from src.api.models import (
    UserCreate, UserLogin, UserOut, Token,
    TransactionIn, TransactionOut, CategoryIn, CategoryOut,
    BudgetIn, BudgetOut, DashboardSummary, ReportRequest, ReportResult
)
from src.api.db import SessionLocal, get_password_hash, User, \
    Category, Transaction, Budget, get_user_by_email, get_db
from src.api.auth import create_access_token, authenticate_user, get_current_user

from sqlalchemy.future import select

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
transaction_router = APIRouter(prefix="/transactions", tags=["Transactions"])
category_router = APIRouter(prefix="/categories", tags=["Categories"])
budget_router = APIRouter(prefix="/budgets", tags=["Budgets"])
dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
report_router = APIRouter(prefix="/reports", tags=["Reports"])

# ----- Auth Endpoints -----

# PUBLIC_INTERFACE
@auth_router.post('/register', response_model=UserOut, summary="User Registration", description="Register a new user.")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user/email exists
    lookup = await get_user_by_email(db, user.email)
    if lookup:
        raise HTTPException(status_code=400, detail="Email already registered")
    existing = await db.execute(select(User).where(User.username == user.username))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# PUBLIC_INTERFACE
@auth_router.post('/login', response_model=Token, summary="User Login & JWT Issue")
async def login(form_data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# PUBLIC_INTERFACE
@auth_router.get('/me', response_model=UserOut, summary="Get current user")
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

# ----- Category Endpoints -----

# PUBLIC_INTERFACE
@category_router.get('/', response_model=List[CategoryOut], summary="List all categories")
async def list_categories(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Category))
    cats = res.scalars().all()
    return cats

# PUBLIC_INTERFACE
@category_router.post('/', response_model=CategoryOut, summary="Create category")
async def create_category(cat: CategoryIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_cat = Category(name=cat.name, is_income=cat.is_income)
    db.add(db_cat)
    await db.commit()
    await db.refresh(db_cat)
    return db_cat

# PUBLIC_INTERFACE
@category_router.put('/{category_id}', response_model=CategoryOut, summary="Update category")
async def update_category(category_id: int, cat: CategoryIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    cat_q = await db.execute(select(Category).where(Category.id == category_id))
    db_cat = cat_q.scalar()
    if not db_cat:
        raise HTTPException(404, "Category not found")
    db_cat.name = cat.name
    db_cat.is_income = cat.is_income
    await db.commit()
    await db.refresh(db_cat)
    return db_cat

# PUBLIC_INTERFACE
@category_router.delete('/{category_id}', summary="Delete category")
async def delete_category(category_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    cat_q = await db.execute(select(Category).where(Category.id == category_id))
    db_cat = cat_q.scalar()
    if not db_cat:
        raise HTTPException(404, "Category not found")
    await db.delete(db_cat)
    await db.commit()
    return {"detail": "Category deleted"}

# ----- Transaction Endpoints -----

# PUBLIC_INTERFACE
@transaction_router.get('/', response_model=List[TransactionOut], summary="Get transactions for user")
async def list_transactions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(Transaction).where(Transaction.user_id == current_user.id)
    if start_date:
        query = query.where(Transaction.date >= start_date)
    if end_date:
        query = query.where(Transaction.date <= end_date)
    if category_id:
        query = query.where(Transaction.category_id == category_id)
    query = query.order_by(Transaction.date.desc()).offset(skip).limit(limit)
    res = await db.execute(query)
    txs = res.scalars().all()
    return txs

# PUBLIC_INTERFACE
@transaction_router.post('/', response_model=TransactionOut, summary="Create transaction entry")
async def create_transaction(tx: TransactionIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_tx = Transaction(
        user_id=current_user.id,
        amount=tx.amount,
        type=tx.type.value,
        category_id=tx.category_id,
        description=tx.description,
        date=tx.date or date.today()
    )
    db.add(db_tx)
    await db.commit()
    await db.refresh(db_tx)
    return db_tx

# PUBLIC_INTERFACE
@transaction_router.put('/{transaction_id}', response_model=TransactionOut, summary="Update a transaction")
async def update_transaction(transaction_id: int, tx: TransactionIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tx_q = await db.execute(select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == current_user.id))
    db_tx = tx_q.scalar()
    if not db_tx:
        raise HTTPException(404, "Transaction not found")
    db_tx.amount = tx.amount
    db_tx.type = tx.type.value
    db_tx.category_id = tx.category_id
    db_tx.description = tx.description
    db_tx.date = tx.date or db_tx.date
    await db.commit()
    await db.refresh(db_tx)
    return db_tx

# PUBLIC_INTERFACE
@transaction_router.delete('/{transaction_id}', summary="Delete transaction")
async def delete_transaction(transaction_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tx_q = await db.execute(select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == current_user.id))
    db_tx = tx_q.scalar()
    if not db_tx:
        raise HTTPException(404, "Transaction not found")
    await db.delete(db_tx)
    await db.commit()
    return {"detail": "Transaction deleted"}

# ----- Budget Endpoints -----

# PUBLIC_INTERFACE
@budget_router.post('/', response_model=BudgetOut, summary="Set or update budget for a category")
async def set_budget(budget: BudgetIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Budget).where(
            Budget.user_id == current_user.id,
            Budget.category_id == budget.category_id,
            Budget.period == budget.period
        )
    )
    db_bud = result.scalar()
    if db_bud:
        db_bud.amount = budget.amount
        await db.commit()
        await db.refresh(db_bud)
        return db_bud
    new_budget = Budget(
        user_id=current_user.id,
        category_id=budget.category_id,
        amount=budget.amount,
        period=budget.period
    )
    db.add(new_budget)
    await db.commit()
    await db.refresh(new_budget)
    return new_budget

# PUBLIC_INTERFACE
@budget_router.get('/', response_model=List[BudgetOut], summary="Get user budgets")
async def get_budgets(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Budget).where(Budget.user_id == current_user.id))
    return result.scalars().all()

# ----- Dashboard Endpoint -----

# PUBLIC_INTERFACE
@dashboard_router.get('/', response_model=DashboardSummary, summary="Financial overview dashboard logic")
async def get_dashboard(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tx_query = select(Transaction).where(Transaction.user_id == current_user.id)
    tx_res = await db.execute(tx_query)
    txs = tx_res.scalars().all()
    total_income = sum(t.amount for t in txs if t.type == "income")
    total_expense = sum(t.amount for t in txs if t.type == "expense")
    sorted_exp = sorted([t for t in txs if t.type == "expense"], key=lambda x: -x.amount)[:5]
    sorted_inc = sorted([t for t in txs if t.type == "income"], key=lambda x: -x.amount)[:5]
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
        "top_expenses": sorted_exp,
        "top_income": sorted_inc,
    }

# ----- Reports Endpoint -----

# PUBLIC_INTERFACE
@report_router.post('/', response_model=ReportResult, summary="Generate financial reports for user")
async def generate_report(request: ReportRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = select(Transaction).where(Transaction.user_id == current_user.id)
    if request.start_date:
        query = query.where(Transaction.date >= request.start_date)
    if request.end_date:
        query = query.where(Transaction.date <= request.end_date)
    tx_res = await db.execute(query)
    txs = tx_res.scalars().all()
    # Simple grouping: by category name
    groups = {}
    for t in txs:
        key = None
        if request.group_by == "category":
            key = t.category.name if t.category else "Unknown"
        elif request.group_by == "month":
            key = t.date.strftime("%Y-%m")
        else:
            key = "all"
        if key not in groups:
            groups[key] = 0.0
        groups[key] += t.amount
    total = {"income": sum(t.amount for t in txs if t.type == "income"),
                "expense": sum(t.amount for t in txs if t.type == "expense")}
    labels = list(groups.keys())
    values = [groups[k] for k in labels]
    return {"labels": labels, "values": values, "totals": total}
