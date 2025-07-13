import pytest

pytestmark = pytest.mark.asyncio

async def test_set_budget(test_client, test_budget_data, auth_headers, test_category_data):
    """Test setting a new budget."""
    # Create category first
    category_response = test_client.post(
        "/categories/",
        json=test_category_data,
        headers=auth_headers
    )
    assert category_response.status_code == 200
    test_budget_data["category_id"] = category_response.json()["id"]
    
    response = test_client.post(
        "/budgets/",
        json=test_budget_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == test_budget_data["amount"]
    assert data["period"] == test_budget_data["period"]
    assert "id" in data
    assert "category" in data

async def test_update_existing_budget(test_client, test_budget_data, auth_headers):
    """Test updating an existing budget."""
    # Update the existing budget with new amount
    updated_data = test_budget_data.copy()
    updated_data["amount"] = 2000.0
    
    response = test_client.post(
        "/budgets/",
        json=updated_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == updated_data["amount"]
    assert data["period"] == updated_data["period"]

async def test_get_budgets(test_client, auth_headers):
    """Test retrieving user budgets."""
    response = test_client.get("/budgets/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Verify budget structure
    budget = data[0]
    assert "id" in budget
    assert "amount" in budget
    assert "period" in budget
    assert "category" in budget

async def test_set_budget_nonexistent_category(test_client, test_budget_data, auth_headers):
    """Test setting budget for non-existent category."""
    test_budget_data["category_id"] = 999
    response = test_client.post(
        "/budgets/",
        json=test_budget_data,
        headers=auth_headers
    )
    # Should fail with foreign key constraint
    assert response.status_code in [400, 404, 422]

async def test_multiple_period_budgets(test_client, test_budget_data, auth_headers):
    """Test setting budgets with different periods."""
    # Set monthly budget
    monthly_budget = test_budget_data.copy()
    monthly_budget["period"] = "monthly"
    response = test_client.post(
        "/budgets/",
        json=monthly_budget,
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Set weekly budget
    weekly_budget = test_budget_data.copy()
    weekly_budget["period"] = "weekly"
    response = test_client.post(
        "/budgets/",
        json=weekly_budget,
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Get all budgets and verify both exist
    response = test_client.get("/budgets/", headers=auth_headers)
    data = response.json()
    periods = [budget["period"] for budget in data]
    assert "monthly" in periods
    assert "weekly" in periods
