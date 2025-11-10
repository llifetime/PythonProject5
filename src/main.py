from src.api import HHAPI
from src.database import DatabaseManager
from src.db_manager import DBManager
from src.utils import format_salary


def main():
    """Main application function"""
    # List of company IDs for data collection
    COMPANY_IDS = [
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

    print("=== HH.RU VACANCIES DATABASE PROJECT ===\n")

    # Initialize components
    api = HHAPI()
    db_manager = DatabaseManager()
    analysis_db = DBManager()

    # Collect data
    print("1. Collecting company data...")
    employers_data = api.get_employers_data(COMPANY_IDS)
    print(f"   Obtained data for {len(employers_data)} companies")

    print("\n2. Collecting vacancies data...")
    all_vacancies = []
    for employer in employers_data:
        vacancies = api.get_vacancies_data(employer['id'])
        all_vacancies.extend(vacancies)
        print(f"   {employer['name']}: {len(vacancies)} vacancies")

    print(f"\n   Total vacancies collected: {len(all_vacancies)}")

    # Create database
    print("\n3. Creating database...")
    db_manager.create_tables()

    # Save data
    print("\n4. Saving data to database...")
    db_manager.save_data_to_database(employers_data, all_vacancies)

    # Display analysis
    print("\n5. Data analysis...")

    # Companies statistics
    companies = analysis_db.get_companies_and_vacancies_count()
    print("\nCompanies and vacancies count:")
    for company, count in companies:
        print(f"   {company}: {count} vacancies")

    # Average salary
    avg_salary = analysis_db.get_avg_salary()
    print(f"\nAverage salary: {avg_salary:,.2f} руб.")

    # Search example
    print("\nSearch results for 'python':")
    python_vacancies = analysis_db.get_vacancies_with_keyword('python')
    if python_vacancies:
        for company, vacancy, salary_from, salary_to, currency, url in python_vacancies[:3]:
            salary_info = format_salary(salary_from, salary_to, currency)
            print(f"   {company} - {vacancy}")
            print(f"   Salary: {salary_info}")
            print(f"   URL: {url}\n")
    else:
        print("   No vacancies found with 'python'")

    print("\n✅ Project completed successfully!")
    print("📁 Database: 'hh_vacancies.db'")


if __name__ == "__main__":
    main()