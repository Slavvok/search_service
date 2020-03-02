import datetime
from dateutil.relativedelta import relativedelta
from zeep import Client
from zeep.transports import Transport
from zeep.helpers import serialize_object
from requests import Session
from requests.auth import HTTPDigestAuth
import json
import re

from django.core.serializers.json import DjangoJSONEncoder

import pandas as pd

url = 'http://test.fedresurs.ru/MessageService/WebService.svc?singleWsdl'
u = 'demowebuser'
p = 'Ax!761BN'

session = Session()
session.auth = HTTPDigestAuth(u, p)
client = Client(url, transport=Transport(session=session))


def data_write():
    """Загрузка данных по всем должникам"""
    start = datetime.date(2019, 10, 1)
    end = datetime.date(2019, 10, 30)
    delta = relativedelta(months=1)
    debtors = []
    while start < datetime.date.today():
        print(start.strftime('%Y-%m-%d'))
        try:
            month_data = client.service.GetDebtorsByLastPublicationPeriod(start, end)
            if month_data:
                # Фильтр долгов частных лиц
                month_debtors = [i['DebtorPerson'] for i in month_data['_value_1'] if 'DebtorPerson' in i]
                debtors.extend(month_debtors)
            else:
                start += delta
                end += delta
                continue
        except Exception as e:
            print(e)
        else:
            start += delta
            end += delta
    with open('data.json', 'w') as f:
        f.write(json.dumps(serialize_object(debtors), cls=DjangoJSONEncoder))


def load():
    """Загрузка данных из json файла"""
    with open('data.json', 'r') as f:
        dd = json.load(f)
        df = pd.DataFrame(dd, columns=['FirstName', 'LastName', 'MiddleName', 'Birthdate', 'BankruptId'])
        return df


def search_person_by_fio(fio, birthday):
    """Функция для поиска совпадений по имени и дате рождения"""
    #TODO: Полноценный поиск
    last_name = fio.split()[0]
    df = load()
    df = df[df['LastName'].str.match(last_name, flags=re.IGNORECASE) &
            df['Birthdate'].str.match(birthday)]
    if not df.empty:
        df.columns = ['Имя', 'Фамилия', 'Отчество', 'Дата рождения', 'ID']
        return df.to_html()
    else:
        return 'Не найдено совпадений. Проверьте входные данные.'
