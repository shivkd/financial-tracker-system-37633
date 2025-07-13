import pytest
from datetime import date

pytestmark = pytest.mark.asyncio

async def test_create_transaction(test_client, test_transaction_data, auth_headers, test_category_data):
    """Test transaction creation."""
    # Create category first
    category_response = test_client.post(
        "/categories/",
        json=test_category_data,
        headers=auth_headers
    )
    assert category_response.status_code == 200
    test_transaction_data["category_id"] = category_response.json()["id"]
    
    response = test_client.post(
        "/transactions/",
        json=test_transaction_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == test_transaction_data["amount"]
    assert data["type"] == test_transaction_data["type"]
    assert data["description"] == test_transaction_data["description"]
    assert "id" in data
    assert "date" in data
    assert "category" in data

async def test_list_transactions(test_client, test_transaction_data, auth_headers):
    """Test listing transactions."""
    response = test_client.get("/transactions/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # Test pagination
    response = test_client.get("/transactions/?skip=0&limit=5", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5

async def test_filter_transactions(test_client, test_transaction_data, auth_headers, test_category_data):
    """Test transaction filtering."""
    # Create category and transaction first
    category_response = test_client.post(
        "/categories/",
        json=test_category_data,
        headers=auth_headers
    )
    category_id = category_response.json()["id"]
    test_transaction_data["category_id"] = category_id
    
    test_client.post(
        "/transactions/",
        json=test_transaction_data,
        headers=auth_headers
    )
    
    # Test date filtering
    today = date.today().isoformat()
    response = test_client.get(
        f"/transactions/?start_date={today}&end_date={today}",
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Test category filtering
    response = test_client.get(
        f"/transactions/?category_id={category_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(tx["category"]["id"] == category_id for tx in data)

async def test_update_transaction(test_client, test_transaction_data, auth_headers):
    """Test transaction update."""
    # Create transaction first
    create_response = test_client.post(
        "/transactions/",
        json=test_transaction_data,
        headers=auth_headers
    )
    transaction_id = create_response.json()["id"]
    
    # Update transaction
    updated_data = {
        "amount": 200.0,
        "type": "income",
        "category_id": test_transaction_data["category_id"],
        "description": "Updated transaction"
    }
    response = test_client.put(
        f"/transactions/{transaction_id}",
        json=updated_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == updated_data["amount"]
    assert data["type"] == updated_data["type"]
    assert data["description"] == updated_data["description"]

async def test_delete_transaction(test_client, test_transaction_data, auth_headers):
    """Test transaction deletion."""
    # Create transaction first
    create_response = test_client.post(
        "/transactions/",
        json=test_transaction_data,
        headers=auth_headers
    )
    transaction_id = create_response.json()["id"]
    
    # Delete transaction
    response = test_client.delete(
        f"/transactions/{transaction_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Transaction deleted"
    
    # Verify deletion
    response = test_client.get("/transactions/", headers=auth_headers)
    transactions = response.json()
    assert not any(tx["id"] == transaction_id for tx in transactions)

async def test_nonexistent_transaction_operations(test_client, test_transaction_data, auth_headers):
    """Test operations on non-existent transactions."""
    # Try to update non-existent transaction
    response = test_client.put(
        "/transactions/999",
        json=test_transaction_data,
        headers=auth_headers
    )
    assert response.status_code == 404
    assert "Transaction not found" in response.json()["detail"]
    
    # Try to delete non-existent transaction
    response = test_client.delete("/transactions/999", headers=auth_headers)
    assert response.status_code == 404
    assert "Transaction not found" in response.json()["detail"]
