import pytest

pytestmark = pytest.mark.asyncio

async def test_create_category(test_client, test_category_data, auth_headers):
    """Test category creation."""
    response = test_client.post(
        "/categories/",
        json=test_category_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_category_data["name"]
    assert data["is_income"] == test_category_data["is_income"]
    assert "id" in data

async def test_list_categories(test_client, test_category_data, auth_headers):
    """Test listing categories."""
    # Create a category first
    test_client.post("/categories/", json=test_category_data, headers=auth_headers)
    
    response = test_client.get("/categories/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == test_category_data["name"]

async def test_update_category(test_client, test_category_data, auth_headers):
    """Test category update."""
    # Create category first
    create_response = test_client.post(
        "/categories/",
        json=test_category_data,
        headers=auth_headers
    )
    category_id = create_response.json()["id"]
    
    # Update category
    updated_data = {
        "name": "Updated Category",
        "is_income": True
    }
    response = test_client.put(
        f"/categories/{category_id}",
        json=updated_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == updated_data["name"]
    assert data["is_income"] == updated_data["is_income"]

async def test_delete_category(test_client, test_category_data, auth_headers):
    """Test category deletion."""
    # Create category first
    create_response = test_client.post(
        "/categories/",
        json=test_category_data,
        headers=auth_headers
    )
    category_id = create_response.json()["id"]
    
    # Delete category
    response = test_client.delete(
        f"/categories/{category_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Category deleted"
    
    # Verify deletion
    response = test_client.get("/categories/", headers=auth_headers)
    categories = response.json()
    assert not any(cat["id"] == category_id for cat in categories)

async def test_update_nonexistent_category(test_client, test_category_data, auth_headers):
    """Test updating a non-existent category."""
    response = test_client.put(
        "/categories/999",
        json=test_category_data,
        headers=auth_headers
    )
    assert response.status_code == 404
    assert "Category not found" in response.json()["detail"]

async def test_delete_nonexistent_category(test_client, auth_headers):
    """Test deleting a non-existent category."""
    response = test_client.delete("/categories/999", headers=auth_headers)
    assert response.status_code == 404
    assert "Category not found" in response.json()["detail"]
