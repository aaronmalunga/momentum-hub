import datetime

import pytest

from momentum_hub.category import Category


class TestCategory:
    """Tests for Category model behavior."""

    def test_category_creation(self):
        """Test creating a new Category instance."""
        category = Category(name="Health", description="Health-related habits")
        assert category.name == "Health"
        assert category.description == "Health-related habits"
        assert category.is_active is True
        assert category.created_at is not None

    def test_category_creation_minimal(self):
        """Test creating a Category with minimal parameters."""
        category = Category(name="Fitness")
        assert category.name == "Fitness"
        assert category.description is None
        assert category.color is None
        assert category.is_active is True

    def test_category_from_dict(self):
        """Test creating Category from dictionary."""
        data = {
            "id": 1,
            "name": "Productivity",
            "description": "Work and study habits",
            "color": "#FF5733",
            "is_active": True,
            "created_at": "2023-01-01T00:00:00",
        }
        category = Category.from_dict(data)
        assert category.id == 1
        assert category.name == "Productivity"
        assert category.description == "Work and study habits"
        assert category.color == "#FF5733"
        assert category.is_active is True

    def test_category_to_dict(self):
        """Test converting Category to dictionary."""
        category = Category(
            name="Learning", description="Learning habits", color="#3498DB"
        )
        data = category.to_dict()
        assert data["name"] == "Learning"
        assert data["description"] == "Learning habits"
        assert data["color"] == "#3498DB"
        assert data["is_active"] is True
        assert "created_at" in data

    def test_category_repr(self):
        """Test string representation of Category."""
        category = Category(name="Test Category")
        repr_str = repr(category)
        assert "name='Test Category'" in repr_str

    def test_get_habits_placeholder(self):
        """Test that get_habits returns empty list (placeholder implementation)."""
        category = Category(name="Test")
        habits = category.get_habits("test.db")
        assert habits == []
