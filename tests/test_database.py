import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.database import DatabaseManager
from src.db_manager import DBManager


class TestDatabaseManager:
    """Test database management functionality"""

    def test_database_manager_initialization(self):
        """Test database manager initialization"""
        db_manager = DatabaseManager()
        assert db_manager.database_name == "hh_vacancies.db"

    def test_create_tables(self):
        """Test table creation method exists"""
        db_manager = DatabaseManager()
        assert hasattr(db_manager, 'create_tables')


class TestDBManager:
    """Test DB manager functionality"""

    def test_db_manager_initialization(self):
        """Test DB manager initialization"""
        db_manager = DBManager()
        assert db_manager.database_name == "hh_vacancies.db"

    def test_execute_query_method_exists(self):
        """Test execute query method exists"""
        db_manager = DBManager()
        assert hasattr(db_manager, '_execute_query')