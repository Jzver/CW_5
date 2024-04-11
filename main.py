import psycopg2

from config import config
from data.classes import DBManager
from data.funcs import create_database, get_vac_data, save_data_to_database


def main():
    companies_ids = [
        '1740',  # Яндекс
        '15478',  # VK
        '64174',  # 2ГИС
        '78638',  # ТИНЬКОФФ
        '2180',  # OZON
        '84585',  # Avito
        '3776',  # MTC
        '1272486',  # СберМаркет
        '3125',  # QIWI
        '1122462'  # Skyeng
    ]
    params = config()
    new_list_com = []
    new_list_vac = []

    get_vac_data('http://api.hh.ru/vacancies', companies_ids, new_list_com, new_list_vac)
    create_database('hhru', params)
    save_data_to_database(new_list_vac, new_list_com, 'hhru', params)
    conn = psycopg2.connect(dbname='hhru', **params)
    conn.autocommit = True
    with conn.cursor() as cur:
        dbmanager = DBManager(cur)
        print('Выберите опцию:')
        print('1. Вывести список всех компаний и количество вакансий у них.')
        print('2. Вывести список всех вакансий с указанием названия компании.')
        print('3. Вывести среднюю зарплату по вакансиям.')
        print('4. Вывести список всех вакансий, у которых зарплата выше средней.')
        print('5. Вывести список всех вакансий по слову.')
        print('Введите любое число больше 5 для того, чтобы завершить')
        while True:
            user_answer = input()
            if int(user_answer) == 1:
                data = dbmanager.get_companies_and_vacancies_count()
                print(data)
            elif int(user_answer) == 2:
                data = dbmanager.get_all_vacancies()
                print(data)
            elif int(user_answer) == 3:
                data = dbmanager.get_avg_salary()
                print(data)
            elif int(user_answer) == 4:
                avg_salary = dbmanager.get_avg_salary()
                data = dbmanager.get_vacancies_with_higher_salary()
                print(data)
            elif int(user_answer) == 5:
                user_word = input('Введите слово, по которому будем искать вакансии: ')
                data = dbmanager.get_vacancies_with_keyword(user_word)
                print(data)
            else:
                break
        conn.commit()
        conn.close()


if __name__ == '__main__':
    main()