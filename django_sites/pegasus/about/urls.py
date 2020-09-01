from django.urls import path
from . import views

app_name = 'about'
urlpatterns = [
    path('', views.index, name='index'),
    path('brenna/', views.brenna, name='brenna'),
    path('fatma/', views.fatma, name='fatma'),
    path('wafi/', views.wafi, name='wafi'),
    path('zachary/', views.zachary, name='zachary'),
    path('adan/', views.adan, name='adan'),
    path('quan/', views.quan, name='quan'),
    path('omar/', views.omar, name='omar'),
]