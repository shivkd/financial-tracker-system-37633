import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.db import Base
from src.api.auth import create_access_token

# Use SQLite in-memory database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def test_db(test_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)

@pytest.fixture
def test_user_data():
    """Test user data fixture."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }

@pytest.fixture
def test_category_data():
    """Test category data fixture."""
    return {
        "name": "Test Category",
        "is_income": False
    }

@pytest.fixture
def test_transaction_data():
    """Test transaction data fixture."""
    return {
        "amount": 100.0,
        "type": "expense",
        "description": "Test transaction",
        "category_id": 1
    }

@pytest.fixture
def test_budget_data():
    """Test budget data fixture."""
    return {
        "category_id": 1,
        "amount": 1000.0,
        "period": "monthly"
    }

@pytest.fixture
def auth_headers(test_user_data):
    """Generate authentication headers with JWT token."""
    token = create_access_token({"sub": test_user_data["username"]})
    return {"Authorization": f"Bearer {token}"}
