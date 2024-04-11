from typing import Any

import psycopg2
import requests


def get_vac_data(url, companies, new_list_com, new_list_vac):
    """Получение данных о компаниях-работодателях и вакансиях с помощью API hh.ru"""

    for company in companies:

        params = {'per_page': 100, 'employer_id': company}
        headers = {'User-Agent': 'HH-User-Agent'}
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            clear_data = data['items']
            new_list_com.append(clear_data[0]['employer'])
            new_list_vac.extend(clear_data)


def create_database(database_name: str, params: dict):
    """Создание базы данных и таблиц для сохранения данных о вакансиях и компаниях."""

    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"DROP DATABASE {database_name}")
    cur.execute(f"CREATE DATABASE {database_name}")

    conn.close()

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE companies (
                company_id INTEGER PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                url VARCHAR(100) NOT NULL
            )
        """)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE vacancies (
                vacancy_id INTEGER PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                company_id INTEGER REFERENCES companies(company_id),
                salary_from INT,
                salary_to INT,
                url VARCHAR(100)
            )
        """)

    conn.commit()
    conn.close()


def save_data_to_database(vacancies: list[dict[str, Any]], companies: list[dict[str, Any]], database_name: str,
                          params: dict):
    """Сохранение данных о вакансиях и компаниях в базу данных."""

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        for company in companies:
            cur.execute(
                """
                INSERT INTO companies (company_id, title, url)
                VALUES (%s, %s, %s)
                """,
                (company['id'], company['name'],
                 company['alternate_url'])
            )
        for vacancy in vacancies:
            if vacancy['salary']:
                if vacancy['salary']['from']:
                    salary_from = vacancy['salary']['from']
                else:
                    salary_from = 0
                if vacancy['salary']['to']:
                    salary_to = vacancy['salary']['to']
                else:
                    salary_to = 0
            else:
                salary_from = 0
                salary_to = 0
            cur.execute(
                """
                INSERT INTO vacancies (vacancy_id, title, company_id, salary_from, salary_to, url)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (vacancy['id'], vacancy['name'], vacancy['employer']['id'], salary_from,
                 salary_to, vacancy['alternate_url'])
            )

    conn.commit()
    conn.close()