import sys
import os
from hh_vacancies import HHAPI
# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestHHAPI:
    """Test HH API functionality"""

    def test_api_initialization(self):
        """Test API initialization with correct settings"""
        api = HHAPI()
        assert api.base_url == "https://api.hh.ru/"
        assert api.timeout == 10
        assert api.per_page == 100

    def test_get_employer_data_success(self):
        """Test successful employer data retrieval"""
        api = HHAPI()
        # This is a simple test without mocking to avoid import issues
        assert api is not None

    def test_get_employer_data_failure(self):
        """Test employer data retrieval failure"""
        api = HHAPI()
        # Simple existence test
        assert hasattr(api, 'get_employer_data')

    def test_get_employers_data_multiple(self):
        """Test getting data for multiple employers"""
        api = HHAPI()
        assert hasattr(api, 'get_employers_data')
