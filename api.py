import requests
from typing import Optional, Dict, List


class HHAPI:
    """Класс для взаимодействия с API HeadHunter"""

    def __init__(self):
        """Инициализация класса API"""
        self.base_url = "https://api.hh.ru/"

    def get_employer_data(self, employer_id: str) -> Optional[Dict]:
        """
        Получает данные о работодателе по API hh.ru

        Args:
            employer_id (str): ID работодателя на hh.ru

        Returns:
            Optional[Dict]: Данные работодателя или None в случае ошибки
        """
        url = f"{self.base_url}employers/{employer_id}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении данных работодателя {employer_id}: {e}")
            return None

    def get_vacancies_data(self, employer_id: str) -> List[Dict]:
        """
        Получает данные о вакансиях работодателя по API hh.ru

        Args:
            employer_id (str): ID работодателя на hh.ru

        Returns:
            List[Dict]: Список вакансий работодателя
        """
        url = f"{self.base_url}vacancies"
        params = {
            'employer_id': employer_id,
            'per_page': 100,
            'page': 0
        }

        all_vacancies = []
        try:
            while True:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                vacancies = data.get('items', [])
                all_vacancies.extend(vacancies)

                # Проверяем, есть ли следующая страница
                if params['page'] >= data.get('pages', 1) - 1:
                    break
                params['page'] += 1

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении вакансий работодателя {employer_id}: {e}")

        return all_vacancies

    def get_employers_data(self, employer_ids: List[str]) -> List[Dict]:
        """
        Получает данные о нескольких работодателях

        Args:
            employer_ids (List[str]): Список ID работодателей

        Returns:
            List[Dict]: Список данных о работодателях
        """
        employers_data = []
        for employer_id in employer_ids:
            employer_data = self.get_employer_data(employer_id)
            if employer_data:
                employers_data.append(employer_data)
        return employers_data