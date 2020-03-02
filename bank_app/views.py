from zeep import Client
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPDigestAuth

from django.views import View
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from django.http import HttpResponse
from .utils import search_person_by_fio


url = 'http://test.fedresurs.ru/MessageService/WebService.svc?singleWsdl'
u = 'demowebuser'
p = 'Ax!761BN'

session = Session()
session.auth = HTTPDigestAuth(u, p)
client = Client(url, transport=Transport(session=session))


class LastPeriodFormView(TemplateView):
    template_name = 'last_period_form.html'


class FioFormView(TemplateView):
    template_name = 'fio_form.html'


@method_decorator(csrf_exempt, name='dispatch')
class GetIdsView(View):
    def post(self, request):
        start = request.POST.get('start')
        end = request.POST.get('end')
        # start = datetime.datetime(2020, 1, 30)
        # end = datetime.datetime(2020, 3, 1)
        try:
            ids = client.service.GetDebtorsByLastPublicationPeriod(start, end)
            if ids:
                ids = [i['DebtorPerson']['BankruptId'] for i in ids['_value_1'] if 'DebtorPerson' in i]
                return render(request, 'response.html', {'ids': ids})
            else:
                return HttpResponse('Нет данных')
        except Exception as e:
            return HttpResponse(e)


@method_decorator(csrf_exempt, name='dispatch')
class GetIdInfoView(View):
    def post(self, request):
        id = request.POST.get('id')
        info = client.service.GetDebtorByIdBankrupt(id)
        if info:
            return render(request, 'info.html', {'info': info})
        else:
            return 'None'


@method_decorator(csrf_exempt, name='dispatch')
class GetInfoByFioView(View):
    def post(self, request):
        fio = request.POST.get('fio')
        birthday = request.POST.get('birthday')
        info = search_person_by_fio(fio, birthday)
        return HttpResponse(info)
