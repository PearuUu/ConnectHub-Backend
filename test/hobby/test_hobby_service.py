from fastapi import HTTPException
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch
from src.main import app
from src.hobby.service import HobbyService
from src.hobby.schemas.hobby import HobbySchema

client = TestClient(app)


@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def hobby_service(mock_db):
    return HobbyService(mock_db)


def test_get_hobby_success(hobby_service, mock_db):
    hobby = {"id": 1, "name": "Painting", "description": "Artistic hobby"}
    hobby_service.get_hobby = AsyncMock(return_value=hobby)

    with patch("src.hobby.router.HobbyService", return_value=hobby_service):
        response = client.get("/hobby/1")
        assert response.status_code == 200
        assert response.json() == hobby


def test_get_hobby_not_found(hobby_service, mock_db):
    hobby_service.get_hobby = AsyncMock(side_effect=HTTPException(
        status_code=404, detail="Hobby not found"))

    with patch("src.hobby.router.HobbyService", return_value=hobby_service):
        response = client.get("/hobby/999")
        assert response.status_code == 404
        assert response.json() == {"detail": "Hobby not found"}


def test_create_hobby_success(hobby_service, mock_db):
    hobby_data = {"name": "Painting", "description": "Artistic hobby"}
    created_hobby = {"id": 1, **hobby_data}
    hobby_service.create_hobby = AsyncMock(return_value=created_hobby)

    with patch("src.hobby.router.HobbyService", return_value=hobby_service):
        response = client.post("/hobby/", json=hobby_data)
        assert response.status_code == 200
        assert response.json() == created_hobby


def test_update_hobby_success(hobby_service, mock_db):
    hobby_data = {"name": "Updated Painting",
                  "description": "Updated description"}
    updated_hobby = {"id": 1, **hobby_data}
    hobby_service.update_hobby = AsyncMock(return_value=updated_hobby)

    with patch("src.hobby.router.HobbyService", return_value=hobby_service):
        response = client.put("/hobby/1", json=hobby_data)
        assert response.status_code == 200
        assert response.json() == updated_hobby


def test_delete_hobby_success(hobby_service, mock_db):
    hobby_service.delete_hobby = AsyncMock(
        return_value={"detail": "Hobby deleted successfully"})

    with patch("src.hobby.router.HobbyService", return_value=hobby_service):
        response = client.delete("/hobby/1")
        assert response.status_code == 200
        assert response.json() == {"detail": "Hobby deleted successfully"}


def test_get_user_hobbies_success(hobby_service, mock_db):
    user_hobbies = [
        {"id": 1, "name": "Painting", "description": "Artistic hobby"},
        {"id": 2, "name": "Cycling", "description": "Outdoor activity"}
    ]
    hobby_service.get_user_hobbies = AsyncMock(return_value=user_hobbies)

    with patch("src.hobby.router.HobbyService", return_value=hobby_service):
        response = client.get(
            "/hobby/user", headers={"Authorization": "Bearer mock_token"})
        assert response.status_code == 200
        assert response.json() == user_hobbies
