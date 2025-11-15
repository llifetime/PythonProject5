import sqlite3
from typing import List, Tuple, Optional
from src.utils import Config


config = Config()


class DatabaseManager:
    """Class for working with database data"""

    def __init__(self):
        self.database_name = config.DB_NAME

    def _execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Tuple]:
        """Helper method for executing queries"""
        conn = sqlite3.connect(self.database_name)
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            return result
        except Exception as e:
            print(f"Error executing query: {e}")
            return []
        finally:
            conn.close()

    def get_companies_and_vacancies_count(self) -> List[Tuple]:
        """Get list of all companies and their vacancies count"""
        query = """
            SELECT e.company_name, COUNT(v.vacancy_id) as vacancies_count
            FROM employers e
            LEFT JOIN vacancies v ON e.employer_id = v.employer_id
            GROUP BY e.company_name
            ORDER BY vacancies_count DESC
        """
        return self._execute_query(query)

    def get_all_vacancies(self) -> List[Tuple]:
        """Get all vacancies with company name, vacancy name, salary and link"""
        query = """
            SELECT
                e.company_name,
                v.vacancy_name,
                v.salary_from,
                v.salary_to,
                v.currency,
                v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            ORDER BY e.company_name, v.vacancy_name
        """
        return self._execute_query(query)

    def get_avg_salary(self) -> float:
        """Get average salary for vacancies"""
        query = """
            SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2.0) as avg_salary
            FROM vacancies
            WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
        """
        result = self._execute_query(query)
        return round(result[0][0], 2) if result and result[0][0] else 0.0

    def get_vacancies_with_higher_salary(self) -> List[Tuple]:
        """Get vacancies with salary higher than average"""
        avg_salary = self.get_avg_salary()
        query = """
            SELECT
                e.company_name,
                v.vacancy_name,
                v.salary_from,
                v.salary_to,
                v.currency,
                v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2.0 > ?
            ORDER BY (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2.0 DESC
        """
        return self._execute_query(query, (avg_salary,))

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple]:
        """Get vacancies containing keyword in name"""
        query = """
            SELECT
                e.company_name,
                v.vacancy_name,
                v.salary_from,
                v.salary_to,
                v.currency,
                v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE LOWER(v.vacancy_name) LIKE LOWER(?)
            ORDER BY e.company_name, v.vacancy_name
        """
        return self._execute_query(query, (f'%{keyword}%',))
