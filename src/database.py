import sqlite3
from typing import List, Dict
from src.utils import Config

config = Config()


class DatabaseManager:
    """Class for managing SQLite database"""

    def __init__(self):
        self.database_name = config.DB_NAME

    def create_tables(self) -> None:
        """Create database tables"""
        conn = sqlite3.connect(self.database_name)

        # Create employers table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS employers (
                employer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER UNIQUE NOT NULL,
                company_name TEXT NOT NULL,
                description TEXT,
                website TEXT,
                vacancies_url TEXT
            )
        """)

        # Create vacancies table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                vacancy_id INTEGER PRIMARY KEY AUTOINCREMENT,
                employer_id INTEGER REFERENCES employers(employer_id),
                vacancy_name TEXT NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                currency TEXT,
                url TEXT UNIQUE NOT NULL,
                requirement TEXT,
                responsibility TEXT
            )
        """)

        conn.commit()
        conn.close()
        print(f"Database {self.database_name} created successfully!")

    def save_data_to_database(self, employers_data: List[Dict], vacancies_data: List[Dict]) -> None:
        """Save companies and vacancies data to database"""
        conn = sqlite3.connect(self.database_name)

        try:
            # Save employers
            employer_mapping = {}
            for employer in employers_data:
                cursor = conn.execute("""
                    INSERT OR REPLACE INTO employers 
                    (company_id, company_name, description, website, vacancies_url)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    employer['id'],
                    employer['name'],
                    employer.get('description', '')[:config.MAX_DESCRIPTION_LENGTH],
                    employer.get('site_url', ''),
                    employer.get('vacancies_url', '')
                ))
                employer_mapping[employer['id']] = cursor.lastrowid

            # Save vacancies
            vacancies_count = 0
            for vacancy in vacancies_data:
                employer_id = employer_mapping.get(vacancy['employer']['id'])
                if employer_id:
                    # Safe salary data extraction
                    salary_data = vacancy.get('salary')
                    if salary_data:
                        salary_from = salary_data.get('from')
                        salary_to = salary_data.get('to')
                        currency = salary_data.get('currency')
                    else:
                        salary_from = None
                        salary_to = None
                        currency = None

                    try:
                        conn.execute("""
                            INSERT OR IGNORE INTO vacancies 
                            (employer_id, vacancy_name, salary_from, salary_to, 
                             currency, url, requirement, responsibility)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
                        vacancies_count += 1
                    except Exception as e:
                        print(f"Error saving vacancy {vacancy['name']}: {e}")

            conn.commit()
            message = f"Data saved successfully: {len(employers_data)} companies, "
            message += f"{vacancies_count} vacancies"
            print(message)

        except Exception as e:
            print(f"Error saving data: {e}")
            conn.rollback()
        finally:
            conn.close()