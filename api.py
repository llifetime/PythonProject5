import requests
from typing import Optional, Dict, List


class HHAPI:
    """Класс для взаимодействия с API HeadHunter"""

    def __init__(self):
        self.base_url = "https://api.hh.ru/"

    def get_employer_data(self, employer_id: str) -> Optional[Dict]:
        """Получает данные о работодателе по API hh.ru"""
        url = f"{self.base_url}employers/{employer_id}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении данных работодателя {employer_id}: {e}")
            return None

    def get_vacancies_data(self, employer_id: str) -> List[Dict]:
        """Получает данные о вакансиях работодателя"""
        url = f"{self.base_url}vacancies"
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