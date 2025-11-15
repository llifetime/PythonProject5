from db_manager import DBManager
from typing import NoReturn


class UserInterface:
    """Класс для взаимодействия с пользователем"""

    def __init__(self, db_manager: DBManager):
        """
        Инициализация пользовательского интерфейса

        Args:
            db_manager (DBManager): Экземпляр менеджера базы данных
        """
        self.db_manager = db_manager

    def display_companies_and_vacancies_count(self) -> None:
        """Отображает список компаний и количество вакансий"""
        print("\n=== КОМПАНИИ И КОЛИЧЕСТВО ВАКАНСИЙ ===")
        companies = self.db_manager.get_companies_and_vacancies_count()
        for company, count in companies:
            print(f"• {company}: {count} вакансий")

    def display_all_vacancies(self) -> None:
        """Отображает все вакансии"""
        print("\n=== ВСЕ ВАКАНСИИ ===")
        vacancies = self.db_manager.get_all_vacancies()
        for company, vacancy, salary_from, salary_to, currency, url in vacancies:
            salary_info = self._format_salary(salary_from, salary_to, currency)
            print(f"• {company} - {vacancy}")
            print(f"  Зарплата: {salary_info}")
            print(f"  Ссылка: {url}\n")

    def display_avg_salary(self) -> None:
        """Отображает среднюю зарплату"""
        print("\n=== СРЕДНЯЯ ЗАРПЛАТА ===")
        avg_salary = self.db_manager.get_avg_salary()
        print(f"Средняя зарплата по всем вакансиям: {avg_salary:,.2f} руб.")

    def display_vacancies_with_higher_salary(self) -> None:
        """Отображает вакансии с зарплатой выше средней"""
        print("\n=== ВАКАНСИИ С ЗАРПЛАТОЙ ВЫШЕ СРЕДНЕЙ ===")
        vacancies = self.db_manager.get_vacancies_with_higher_salary()
        for company, vacancy, salary_from, salary_to, currency, url in vacancies:
            salary_info = self._format_salary(salary_from, salary_to, currency)
            print(f"• {company} - {vacancy}")
            print(f"  Зарплата: {salary_info}")
            print(f"  Ссылка: {url}\n")

    def search_vacancies_with_keyword(self) -> None:
        """Поиск вакансий по ключевому слову"""
        keyword = input("\nВведите ключевое слово для поиска: ").strip()
        if not keyword:
            print("Ключевое слово не может быть пустым!")
            return

        print(f"\n=== РЕЗУЛЬТАТЫ ПОИСКА ПО СЛОВУ '{keyword.upper()}' ===")
        vacancies = self.db_manager.get_vacancies_with_keyword(keyword)

        if vacancies:
            for company, vacancy, salary_from, salary_to, currency, url in vacancies:
                salary_info = self._format_salary(salary_from, salary_to, currency)
                print(f"• {company} - {vacancy}")
                print(f"  Зарплата: {salary_info}")
                print(f"  Ссылка: {url}\n")
        else:
            print("Вакансий по вашему запросу не найдено.")

    def _format_salary(self, salary_from: int, salary_to: int, currency: str) -> str:
        """
        Форматирует информацию о зарплате

        Args:
            salary_from (int): Зарплата от
            salary_to (int): Зарплата до
            currency (str): Валюта

        Returns:
            str: Отформатированная строка с зарплатой
        """
        if salary_from and salary_to:
            return f"{salary_from:,} - {salary_to:,} {currency}"
        elif salary_from:
            return f"от {salary_from:,} {currency}"
        elif salary_to:
            return f"до {salary_to:,} {currency}"
        else:
            return "не указана"

    def run(self) -> NoReturn:
        """Запускает основной цикл взаимодействия с пользователем"""
        while True:
            print("\n" + "=" * 50)
            print("ПЛАТФОРМА АНАЛИЗА ВАКАНСИЙ HH.RU")
            print("=" * 50)
            print("1. Показать компании и количество вакансий")
            print("2. Показать все вакансии")
            print("3. Показать среднюю зарплату")
            print("4. Показать вакансии с зарплатой выше средней")
            print("5. Поиск вакансий по ключевому слову")
            print("0. Выход")

            choice = input("\nВыберите опцию (0-5): ").strip()

            if choice == "1":
                self.display_companies_and_vacancies_count()
            elif choice == "2":
                self.display_all_vacancies()
            elif choice == "3":
                self.display_avg_salary()
            elif choice == "4":
                self.display_vacancies_with_higher_salary()
            elif choice == "5":
                self.search_vacancies_with_keyword()
            elif choice == "0":
                print("До свидания!")
                break
            else:
                print("Неверный выбор. Пожалуйста, выберите опцию от 0 до 5.")

            input("\nНажмите Enter для продолжения...")