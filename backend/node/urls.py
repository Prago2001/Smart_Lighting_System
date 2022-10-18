from django.urls import path
from . import views


urlpatterns = [
    path('getNodes/', views.get_nodes),
    path('discover/',views.discover_remote_nodes),
    path('toggle/', views.toggle_mains),
    path('dimming/', views.dim_to),
]