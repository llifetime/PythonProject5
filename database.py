import psycopg2
from typing import List, Dict, Any, Tuple
from config import config


class DatabaseManager:
    """Класс для управления базой данных PostgreSQL"""

    def __init__(self, database_name: str):
        """
        Инициализация менеджера базы данных

        Args:
            database_name (str): Название базы данных
        """
        self.database_name = database_name
        self.params = config()

    def create_database(self) -> None:
        """Создает базу данных и таблицы"""
        # Подключаемся к базе postgres для создания новой БД
        conn = psycopg2.connect(dbname='postgres', **self.params)
        conn.autocommit = True
        cur = conn.cursor()

        # Удаляем базу данных если она существует
        cur.execute(f"DROP DATABASE IF EXISTS {self.database_name}")
        # Создаем базу данных
        cur.execute(f"CREATE DATABASE {self.database_name}")

        cur.close()
        conn.close()

        # Создаем таблицы в новой базе данных
        self._create_tables()

    def _create_tables(self) -> None:
        """Создает таблицы в базе данных"""
        commands = (
            """
            CREATE TABLE employers (
                employer_id SERIAL PRIMARY KEY,
                company_id INTEGER UNIQUE NOT NULL,
                company_name VARCHAR(255) NOT NULL,
                description TEXT,
                website VARCHAR(255),
                vacancies_url VARCHAR(255)
            )
            """,
            """
            CREATE TABLE vacancies (
                vacancy_id SERIAL PRIMARY KEY,
                employer_id INTEGER REFERENCES employers(employer_id) ON DELETE CASCADE,
                vacancy_name VARCHAR(255) NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                currency VARCHAR(10),
                url VARCHAR(255) NOT NULL,
                requirement TEXT,
                responsibility TEXT
            )
            """
        )

        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        try:
            with conn.cursor() as cur:
                for command in commands:
                    cur.execute(command)
            conn.commit()
        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")
        finally:
            conn.close()

    def save_data_to_database(self, employers_data: List[Dict], vacancies_data: List[Dict]) -> None:
        """
        Сохраняет данные о компаниях и вакансиях в базу данных

        Args:
            employers_data (List[Dict]): Данные о работодателях
            vacancies_data (List[Dict]): Данные о вакансиях
        """
        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        try:
            with conn.cursor() as cur:
                # Сохраняем работодателей
                employer_mapping = {}
                for employer in employers_data:
                    cur.execute("""
                        INSERT INTO employers (company_id, company_name, description, website, vacancies_url)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (company_id) DO UPDATE SET
                        company_name = EXCLUDED.company_name,
                        description = EXCLUDED.description,
                        website = EXCLUDED.website,
                        vacancies_url = EXCLUDED.vacancies_url
                        RETURNING employer_id, company_id
                    """, (
                        employer['id'],
                        employer['name'],
                        employer.get('description', '')[:500],
                        employer.get('site_url', ''),
                        employer.get('vacancies_url', '')
                    ))
                    result = cur.fetchone()
                    employer_mapping[employer['id']] = result[0]

                # Сохраняем вакансии
                for vacancy in vacancies_data:
                    employer_id = employer_mapping.get(vacancy['employer']['id'])
                    if employer_id:
                        salary = vacancy.get('salary')
                        salary_from = salary.get('from') if salary else None
                        salary_to = salary.get('to') if salary else None
                        currency = salary.get('currency') if salary else None

                        cur.execute("""
                            INSERT INTO vacancies (employer_id, vacancy_name, salary_from, salary_to, currency, url, requirement, responsibility)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (url) DO NOTHING
                        """, (
                            employer_id,
                            vacancy['name'],
                            salary_from,
                            salary_to,
                            currency,
                            vacancy['alternate_url'],
                            vacancy['snippet'].get('requirement', ''),
                            vacancy['snippet'].get('responsibility', '')
                        ))

            conn.commit()
            print(f"Данные успешно сохранены: {len(employers_data)} компаний, {len(vacancies_data)} вакансий")

        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
            conn.rollback()
        finally:
            conn.close()