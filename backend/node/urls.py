from django.urls import path
from . import views


urlpatterns = [
    path('getNodes/', views.get_nodes),
]