from django.urls import path
from .views import *

urlpatterns = [
    path('last_period/', LastPeriodFormView.as_view()),
    path('fio/', FioFormView.as_view()),
    path('get_ids/', GetIdsView.as_view()),
    path('get_id_info/', GetIdInfoView.as_view()),
    path('get_fio_info/', GetInfoByFioView.as_view())
]
