import os
from dotenv import load_dotenv

load_dotenv()


def config():
    """
    Возвращает параметры для подключения к базе данных

    Returns:
        dict: Словарь с параметрами подключения
    """
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
        'port': os.getenv('DB_PORT', '5432')
    }