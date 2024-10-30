from django.urls import path
from . import views
from .views import ImportAPIView,ListCustomersView,CreateAPIView,UpdateAPIView,DeleteAPIView


urlpatterns = [
    path('', views.home, name='home'),
    path('import/', ImportAPIView.as_view(), name='ImportAPIView'),
    path('customer-list/', ListCustomersView.as_view(), name='list_customers'),
    path('customer/update/<int:pk>/', UpdateAPIView.as_view(), name='update-customer'),
    path('customer/delete/<int:pk>/',DeleteAPIView.as_view(),name="delete_customer"),
    path('customer/create/',CreateAPIView.as_view(),name='CreateApi')
]