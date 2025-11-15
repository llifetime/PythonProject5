import sys
import os
from unittest.mock import Mock, patch
from src.database import DatabaseManager
from src.db_manager import DBManager

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


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

    @patch('src.db_manager.sqlite3.connect')
    def test_execute_query_success(self, mock_connect):
        """Test successful query execution"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [('result1',), ('result2',)]
        mock_connect.return_value = mock_conn

        db_manager = DBManager()
        result = db_manager._execute_query("SELECT * FROM test")

        assert len(result) == 2
        mock_conn.close.assert_called_once()
