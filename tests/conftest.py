import pytest
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def sample_employer_data():
    """Sample employer data for testing"""
    return {
        'id': '12345',
        'name': 'Test Company',
        'description': 'Test description',
        'site_url': 'https://test.com',
        'vacancies_url': 'https://test.com/vacancies'
    }


@pytest.fixture
def sample_vacancy_data():
    """Sample vacancy data for testing"""
    return {
        'name': 'Python Developer',
        'employer': {'id': '12345'},
        'salary': {
            'from': 100000,
            'to': 150000,
            'currency': 'RUR'
        },
        'alternate_url': 'https://hh.ru/vacancy/123',
        'snippet': {
            'requirement': 'Python experience required',
            'responsibility': 'Develop backend services'
        }
    }