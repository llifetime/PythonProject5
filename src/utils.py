import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for application settings"""

    # Database
    DB_NAME = os.getenv('DB_NAME', 'hh_vacancies.db')

    # API Settings
    HH_API_BASE_URL = os.getenv('HH_API_BASE_URL', 'https://api.hh.ru/')
    HH_API_TIMEOUT = int(os.getenv('HH_API_TIMEOUT', '10'))
    HH_API_PER_PAGE = int(os.getenv('HH_API_PER_PAGE', '100'))

    # Application
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    MAX_DESCRIPTION_LENGTH = int(os.getenv('MAX_DESCRIPTION_LENGTH', '500'))
    DEFAULT_CURRENCY = os.getenv('DEFAULT_CURRENCY', 'руб.')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    API_LANGUAGE = os.getenv('API_LANGUAGE', 'ru')

    # Data Collection
    COMPANY_IDS = os.getenv('COMPANY_IDS', '15478,3529,1740,4181,3776,39305,87021,907345,1057,1122462').split(',')
    MAX_VACANCIES_PER_COMPANY = int(os.getenv('MAX_VACANCIES_PER_COMPANY', '500'))
    API_REQUEST_DELAY = float(os.getenv('API_REQUEST_DELAY', '0.1'))

    # Search and Filter
    DEFAULT_SEARCH_KEYWORD = os.getenv('DEFAULT_SEARCH_KEYWORD', 'python')
    MIN_SALARY_THRESHOLD = int(os.getenv('MIN_SALARY_THRESHOLD', '0'))
    RESULTS_LIMIT = int(os.getenv('RESULTS_LIMIT', '10'))

    # Export
    EXPORT_FORMAT = os.getenv('EXPORT_FORMAT', 'json')
    EXPORT_DIR = os.getenv('EXPORT_DIR', 'exports')
    ENABLE_BACKUPS = os.getenv('ENABLE_BACKUPS', 'True').lower() == 'true'


def format_salary(salary_from, salary_to, currency):
    """Format salary information for display"""
    currency = currency or Config.DEFAULT_CURRENCY

    if salary_from and salary_to:
        return f"{salary_from:,} - {salary_to:,} {currency}"
    elif salary_from:
        return f"от {salary_from:,} {currency}"
    elif salary_to:
        return f"до {salary_to:,} {currency}"
    else:
        return "не указана"


def safe_get(data, keys, default=None):
    """Safely get nested dictionary values"""
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def get_company_ids():
    """Get list of company IDs from environment variable"""
    return [company_id.strip() for company_id in Config.COMPANY_IDS if company_id.strip()]
