from .config import config


def format_salary(salary_from, salary_to, currency):
    """Format salary information for display"""
    currency = currency or config.DEFAULT_CURRENCY

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
    return [company_id.strip() for company_id in config.COMPANY_IDS if company_id.strip()]