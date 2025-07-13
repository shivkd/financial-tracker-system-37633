from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import (
    auth_router, transaction_router, category_router, budget_router, dashboard_router, report_router
)
from src.api.db import create_database_and_tables

openapi_tags = [
    {'name': 'Authentication', 'description': 'User authentication endpoints.'},
    {'name': 'Transactions', 'description': 'Transaction CRUD and listing for user.'},
    {'name': 'Categories', 'description': 'Expense/income category management.'},
    {'name': 'Budgets', 'description': 'Budget setting and management.'},
    {'name': 'Dashboard', 'description': 'Financial overview information.'},
    {'name': 'Reports', 'description': 'Financial reports and analytics.'}
]

app = FastAPI(
    title="Finance Tracker Backend API",
    description="Backend RESTful API for the Finance Tracker App (FastAPI).",
    version="1.0.0",
    openapi_tags=openapi_tags
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    # Create tables if not existing
    await create_database_and_tables()

@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}

# Mount routers
app.include_router(auth_router)
app.include_router(transaction_router)
app.include_router(category_router)
app.include_router(budget_router)
app.include_router(dashboard_router)
app.include_router(report_router)
