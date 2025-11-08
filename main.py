import requests
import sqlite3
import os
from typing import List, Dict, Optional, Tuple


class HHAPI:
    """Класс для работы с API HeadHunter"""

    def get_employer_data(self, employer_id: str) -> Optional[Dict]:
        """Получает данные о работодателе"""
        url = f"https://api.hh.ru/employers/{employer_id}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ошибка при получении данных работодателя {employer_id}: {e}")
            return None

    def get_vacancies_data(self, employer_id: str) -> List[Dict]:
        """Получает данные о вакансиях работодателя"""
        url = "https://api.hh.ru/vacancies"
        params = {'employer_id': employer_id, 'per_page': 100, 'page': 0}

        all_vacancies = []
        try:
            while True:
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                vacancies = data.get('items', [])
                all_vacancies.extend(vacancies)

                if params['page'] >= data.get('pages', 1) - 1:
                    break
                params['page'] += 1
        except Exception as e:
            print(f"Ошибка при получении вакансий: {e}")

        return all_vacancies


class DatabaseManager:
    """Класс для работы с базой данных SQLite"""

    def __init__(self, db_name: str = 'hh_vacancies.db'):
        self.db_name = db_name

    def create_tables(self) -> None:
        """Создает таблицы в базе данных"""
        conn = sqlite3.connect(self.db_name)

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
        print("✅ Таблицы созданы успешно!")

    def save_data(self, employers_data: List[Dict], vacancies_data: List[Dict]) -> None:
        """Сохраняет данные в базу данных"""
        conn = sqlite3.connect(self.db_name)

        # Сохраняем работодателей
        employer_mapping = {}
        for employer in employers_data:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO employers 
                (company_id, company_name, description, website, vacancies_url)
                VALUES (?, ?, ?, ?, ?)
            """, (
                employer['id'],
                employer['name'],
                employer.get('description', '')[:500],
                employer.get('site_url', ''),
                employer.get('vacancies_url', '')
            ))
            employer_mapping[employer['id']] = cursor.lastrowid

        # Сохраняем вакансии
        vacancies_count = 0
        for vacancy in vacancies_data:
            employer_id = employer_mapping.get(vacancy['employer']['id'])
            if employer_id:
                # Безопасное получение данных о зарплате
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
                        (employer_id, vacancy_name, salary_from, salary_to, currency, url, requirement, responsibility)
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
                    print(f"Ошибка при сохранении вакансии {vacancy['name']}: {e}")

        conn.commit()
        conn.close()
        print(f"✅ Данные сохранены: {len(employers_data)} компаний, {vacancies_count} вакансий!")


class DBManager:
    """Класс для управления данными в БД"""

    def __init__(self, db_name: str = 'hh_vacancies.db'):
        self.db_name = db_name

    def _execute_query(self, query: str, params: tuple = ()) -> List[Tuple]:
        """Выполняет SQL-запрос"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        conn.close()
        return result

    def get_companies_and_vacancies_count(self) -> List[Tuple]:
        """Получает список компаний и количество вакансий"""
        query = """
            SELECT e.company_name, COUNT(v.vacancy_id) 
            FROM employers e 
            LEFT JOIN vacancies v ON e.employer_id = v.employer_id 
            GROUP BY e.company_name 
            ORDER BY COUNT(v.vacancy_id) DESC
        """
        return self._execute_query(query)

    def get_all_vacancies(self) -> List[Tuple]:
        """Получает все вакансии"""
        query = """
            SELECT e.company_name, v.vacancy_name, v.salary_from, v.salary_to, v.currency, v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            ORDER BY e.company_name
        """
        return self._execute_query(query)

    def get_avg_salary(self) -> float:
        """Получает среднюю зарплату"""
        query = """
            SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2.0)
            FROM vacancies
            WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
        """
        result = self._execute_query(query)
        return round(result[0][0], 2) if result and result[0][0] else 0.0

    def get_vacancies_with_higher_salary(self) -> List[Tuple]:
        """Получает вакансии с зарплатой выше средней"""
        avg_salary = self.get_avg_salary()
        query = """
            SELECT e.company_name, v.vacancy_name, v.salary_from, v.salary_to, v.currency, v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE (COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2.0 > ?
            ORDER BY (COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2.0 DESC
        """
        return self._execute_query(query, (avg_salary,))

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple]:
        """Ищет вакансии по ключевому слову"""
        query = """
            SELECT e.company_name, v.vacancy_name, v.salary_from, v.salary_to, v.currency, v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE LOWER(v.vacancy_name) LIKE LOWER(?)
        """
        return self._execute_query(query, (f'%{keyword}%',))

    def get_vacancies_count(self) -> int:
        """Получает общее количество вакансий"""
        query = "SELECT COUNT(*) FROM vacancies"
        result = self._execute_query(query)
        return result[0][0] if result else 0


def main():
    """Основная функция"""
    print("=== ПРОЕКТ ПО БАЗЕ ДАННЫХ HH.RU ===\n")

    # ID компаний для сбора данных
    company_ids = [
        '15478',  # VK
        '3529',  # Сбер
        '1740',  # Яндекс
        '4181',  # Wildberries
        '3776',  # МТС
        '39305',  # Газпром нефть
        '87021',  # Тинькофф
        '907345',  # Ozon
        '1057',  # Касперский
        '1122462'  # Сбермаркет
    ]

    # Инициализация классов
    api = HHAPI()
    db_manager = DatabaseManager()
    analysis_db = DBManager()

    # Сбор данных
    print("1. Собираем данные о компаниях...")
    employers_data = []
    for company_id in company_ids:
        employer = api.get_employer_data(company_id)
        if employer:
            employers_data.append(employer)
            print(f"   ✅ {employer['name']}")
        else:
            print(f"   ❌ Не удалось получить данные компании {company_id}")

    if not employers_data:
        print("❌ Не удалось получить данные ни об одной компании!")
        return

    print(f"\n2. Собираем данные о вакансиях...")
    all_vacancies = []
    for employer in employers_data:
        vacancies = api.get_vacancies_data(employer['id'])
        all_vacancies.extend(vacancies)
        print(f"   ✅ {employer['name']}: {len(vacancies)} вакансий")

    if not all_vacancies:
        print("❌ Не удалось получить данные о вакансиях!")
        return

    # Создание базы данных
    print(f"\n3. Создаем базу данных...")
    db_manager.create_tables()

    # Сохранение данных
    print(f"\n4. Сохраняем данные...")
    db_manager.save_data(employers_data, all_vacancies)

    # Демонстрация работы
    print(f"\n5. Анализ данных:")

    # Компании и вакансии
    print(f"\n📊 Компании и количество вакансий:")
    companies = analysis_db.get_companies_and_vacancies_count()
    for company, count in companies:
        print(f"   {company}: {count} вакансий")

    # Средняя зарплата
    avg_salary = analysis_db.get_avg_salary()
    print(f"\n💰 Средняя зарплата: {avg_salary:,.2f} руб.")

    # Вакансии с Python
    print(f"\n🐍 Вакансии с 'python' (первые 5):")
    python_vacancies = analysis_db.get_vacancies_with_keyword('python')
    if python_vacancies:
        for company, vacancy, salary_from, salary_to, currency, url in python_vacancies[:5]:
            if salary_from or salary_to:
                salary_info = f"{salary_from or '?'} - {salary_to or '?'} {currency or 'руб.'}"
            else:
                salary_info = "не указана"
            print(f"   🏢 {company}")
            print(f"   💼 {vacancy}")
            print(f"   💰 Зарплата: {salary_info}")
            print(f"   🔗 {url}\n")
    else:
        print("   Вакансий с 'python' не найдено")

    # Общая статистика
    total_vacancies = analysis_db.get_vacancies_count()
    print(f"\n📈 Общая статистика:")
    print(f"   Всего компаний: {len(companies)}")
    print(f"   Всего вакансий: {total_vacancies}")

    print(f"\n✅ Проект успешно завершен!")
    print(f"📁 База данных: 'hh_vacancies.db'")


if __name__ == "__main__":
    main()