from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views


urlpatterns = [
    path('ticket_category', views.TicketCategory, name='TicketCategory'),
    path('task_category', views.TaskCategory, name='TaskCategory'),
    path('project_category', views.ProjectCategory, name='ProjectCategory'),
   
    path('manage_category/<int:id>',
         csrf_exempt(views.ManageCategory)),

    path('tickets', views.ViewTicketsPage, name='ViewTicketsPage'),
    path('computers', views.Computers, name='Computers'),
    path('manage_computer/<str:action>', views.ManageComputer, name='ManageComputer'),
    path('ticket_report/<int:id>', views.TicketRreport, name='TicketRreport'),
    path('add_tickets', views.AddTickets, name='AddTickets'),
    path('assign_tickets/<int:ids>', views.ManageAssignTicket,
         name='ManageAssignTicket'),

    path('view_tickets/<str:ids>', views.ViewTicketDetails,
         name='ViewTicketDetails'),

    path('manage_tickets/<str:id>', views.ManageTickets, name='ManageTicket'),
    path('manage_replies/<str:id>', views.ManageReplies, name='ManageReplies'),


    # client Ticket

    path('client_ticket', views.CreateClientTicket, name='ClientTicket'),



]
