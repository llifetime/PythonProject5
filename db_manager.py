import psycopg2
from typing import List, Tuple, Optional
from config import config


class DBManager:
    """
    Класс для работы с данными в БД PostgreSQL

    Предоставляет методы для получения статистики по вакансиям и компаниям
    """

    def __init__(self, database_name: str):
        """
        Инициализация менеджера базы данных

        Args:
            database_name (str): Название базы данных
        """
        self.database_name = database_name
        self.params = config()

    def _execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Tuple]:
        """
        Вспомогательный метод для выполнения запросов

        Args:
            query (str): SQL-запрос
            params (Optional[Tuple]): Параметры запроса

        Returns:
            List[Tuple]: Результат запроса
        """
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        try:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                result = cur.fetchall()
            return result
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return []
        finally:
            conn.close()

    def get_companies_and_vacancies_count(self) -> List[Tuple]:
        """
        Получает список всех компаний и количество вакансий у каждой компании

        Returns:
            List[Tuple]: Список кортежей (название_компании, количество_вакансий)
        """
        query = """
            SELECT e.company_name, COUNT(v.vacancy_id) as vacancies_count
            FROM employers e
            LEFT JOIN vacancies v ON e.employer_id = v.employer_id
            GROUP BY e.company_name
            ORDER BY vacancies_count DESC
        """
        return self._execute_query(query)

    def get_all_vacancies(self) -> List[Tuple]:
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию

        Returns:
            List[Tuple]: Список кортежей (компания, вакансия, зарплата_от, зарплата_до, валюта, ссылка)
        """
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
        """
        Получает среднюю зарплату по вакансиям

        Returns:
            float: Средняя зарплата
        """
        query = """
            SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2) as avg_salary
            FROM vacancies
            WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
        """
        result = self._execute_query(query)
        return round(result[0][0], 2) if result and result[0][0] else 0.0

    def get_vacancies_with_higher_salary(self) -> List[Tuple]:
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям

        Returns:
            List[Tuple]: Список вакансий с зарплатой выше средней
        """
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
            WHERE (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 > %s
            ORDER BY (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 DESC
        """
        return self._execute_query(query, (avg_salary,))

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple]:
        """
        Получает список всех вакансий, в названии которых содержатся переданные слова

        Args:
            keyword (str): Ключевое слово для поиска

        Returns:
            List[Tuple]: Список вакансий, содержащих ключевое слово
        """
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
            WHERE LOWER(v.vacancy_name) LIKE LOWER(%s)
            ORDER BY e.company_name, v.vacancy_name
        """
        return self._execute_query(query, (f'%{keyword}%',))