import requests
from typing import Optional, Dict, List
from ..utils.config import config


class HHAPI:
    """Class for interacting with HeadHunter API"""

    def __init__(self):
        self.base_url = config.HH_API_BASE_URL
        self.timeout = config.HH_API_TIMEOUT
        self.per_page = config.HH_API_PER_PAGE

    def get_employer_data(self, employer_id: str) -> Optional[Dict]:
        """Get employer data by ID"""
        url = f"{self.base_url}employers/{employer_id}"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting employer data {employer_id}: {e}")
            return None

    def get_vacancies_data(self, employer_id: str) -> List[Dict]:
        """Get vacancies data for employer"""
        url = f"{self.base_url}vacancies"
        params = {
            'employer_id': employer_id,
            'per_page': self.per_page,
            'page': 0
        }

        all_vacancies = []
        try:
            while True:
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                vacancies = data.get('items', [])
                all_vacancies.extend(vacancies)

                # Check if there are more pages
                if params['page'] >= data.get('pages', 1) - 1:
                    break
                params['page'] += 1

        except requests.exceptions.RequestException as e:
            print(f"Error getting vacancies for employer {employer_id}: {e}")

        return all_vacancies

    def get_employers_data(self, employer_ids: List[str]) -> List[Dict]:
        """Get data for multiple employers"""
        employers_data = []
        for employer_id in employer_ids:
            print(f"Getting data for company {employer_id}...")
            employer_data = self.get_employer_data(employer_id)
            if employer_data:
                employers_data.append(employer_data)
        return employers_data