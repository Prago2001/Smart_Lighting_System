from django.urls import path
from . import views


urlpatterns = [
    path('getNodes/', views.get_nodes),
    path('discover/',views.discover_remote_nodes),
    path('toggle/', views.toggle_mains),
    path('dimming/', views.dim_to),
    path('getSchedule/',views.getSchedule),
    path('setSchedule/', views.changeSchedule),
    path('sync/',views.syncToSchedule),
    path('instValues/',views.getInstValues),
    path('graphValues/',views.getGraphValues),
    path('setTelemetry/',views.enable_disable_telemetry),
    path('activateSchedule/',views.enable_disable_schedule),
    path('deleteNode/',views.delete_node),
    path('getRetryJobStatus/',views.getRetryJobStatus),
    path('createOrEditSchedule/',views.createOrEditSchedule),
    path('getAllSchedules/',views.getAllSchedules),
    path('getScheduleByName/<str:schedule_name>/',views.getScheduleByName),
    path('getActiveSchedule/',views.getActiveSchedule),
    path('activateSchedule/',views.activateSchedule),
    path('deleteSchedule/<str:schedule_name>/',views.deleteSchedule),
    path('getSlotsBySchedule/<str:schedule_name>/',views.getSlotsByScheduleName),
    path('changeSlot/',views.changeASlotFromSchedule)

]