import pytest
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils import Config, format_salary, safe_get


class TestConfig:
    """Test configuration settings"""

    def test_config_defaults(self):
        """Test that config has default values"""
        config = Config()
        assert config.DB_NAME == "hh_vacancies.db"
        assert config.HH_API_BASE_URL == "https://api.hh.ru/"
        assert config.HH_API_TIMEOUT == 10
        assert config.HH_API_PER_PAGE == 100


class TestHelpers:
    """Test helper functions"""

    def test_format_salary_with_range(self):
        """Test salary formatting with both from and to"""
        result = format_salary(100000, 150000, 'RUR')
        assert result == "100,000 - 150,000 RUR"

    def test_format_salary_from_only(self):
        """Test salary formatting with only from value"""
        result = format_salary(100000, None, 'RUR')
        assert result == "от 100,000 RUR"

    def test_format_salary_to_only(self):
        """Test salary formatting with only to value"""
        result = format_salary(None, 150000, 'RUR')
        assert result == "до 150,000 RUR"

    def test_format_salary_no_salary(self):
        """Test salary formatting with no salary data"""
        result = format_salary(None, None, None)
        assert result == "не указана"

    def test_safe_get_existing_keys(self):
        """Test safe_get with existing keys"""
        data = {'a': {'b': {'c': 'value'}}}
        result = safe_get(data, ['a', 'b', 'c'])
        assert result == 'value'

    def test_safe_get_missing_keys(self):
        """Test safe_get with missing keys"""
        data = {'a': {'b': 'value'}}
        result = safe_get(data, ['a', 'b', 'c'])
        assert result is None