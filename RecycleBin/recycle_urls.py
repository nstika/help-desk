from django.urls import path
from . import views

urlpatterns = [

    path('recycle_department', views.Department, name='RecycleDepartment'),
    path('recycle_position', views.Positions, name='RecyclePosition'),
    path('recycle_category', views.Category, name='RecycleCategory'),
    path('recycle_ticket', views.Tickets, name='RecycleTickets'),
    path('recycle_users', views.Users, name='RecycleUsers'),
    path('manage_recycle/<str:id>', views.ManageRecycle, name='ManageRecycle'),
]
