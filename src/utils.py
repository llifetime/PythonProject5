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


def format_salary(salary_from, salary_to, currency):
    """Format salary information for display"""
    if salary_from and salary_to:
        return f"{salary_from:,} - {salary_to:,} {currency or 'руб.'}"
    elif salary_from:
        return f"от {salary_from:,} {currency or 'руб.'}"
    elif salary_to:
        return f"до {salary_to:,} {currency or 'руб.'}"
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