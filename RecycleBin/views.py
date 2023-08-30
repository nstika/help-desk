from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from Users.views import PreviewDate, sendException, sendTrials
from django.core.paginator import Paginator
from django.db.models import Q
from . import models
from Users import models as user_models
from Tickets import models as ticket_models
from django.core.exceptions import *

# Create your views here.


@login_required(login_url='Login')
def Users(request):
    if request.user.is_superuser:
        CheckSearchQuery = 'SearchQuery' in request.GET
        CheckDataNumber = 'DataNumber' in request.GET
        DataNumber = 10
        SearchQuery = ''
        UsersList = []

        if CheckDataNumber:
            DataNumber = int(request.GET['DataNumber'])

        if CheckSearchQuery:
            SearchQuery = request.GET['SearchQuery']
            UsersList = user_models.Users.objects.filter(Q(username__icontains=SearchQuery) | Q(email__icontains=SearchQuery) | Q(
                first_name__icontains=SearchQuery) | Q(last_name__icontains=SearchQuery) | Q(phone__icontains=SearchQuery) | Q(position__position_name__icontains=SearchQuery) | Q(department__dept_name__icontains=SearchQuery), is_delete=True)
        else:
            UsersList = user_models.Users.objects.filter(
                is_delete=True)

        paginator = Paginator(UsersList, DataNumber)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        Pages = paginator.get_elided_page_range(
            page_obj.number, on_each_side=0, on_ends=1)

        context = {
            'page_obj': page_obj,
            'SearchQuery': SearchQuery,
            'DataNumber': DataNumber,
            'TotalUsers': len(UsersList),
            'Pages': Pages
        }
        return render(request, 'Layout/Admin/Recycle/users.html', context)

    else:
        return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def Department(request):
    if request.user.is_superuser:
        CheckSearchQuery = 'SearchQuery' in request.GET
        CheckDataNumber = 'DataNumber' in request.GET
        DataNumber = 10
        SearchQuery = ''
        DepartmentList = []

        if CheckDataNumber:
            DataNumber = int(request.GET['DataNumber'])

        if CheckSearchQuery:
            SearchQuery = request.GET['SearchQuery']
            DepartmentList = user_models.Department.objects.filter(
                Q(dept_name__icontains=SearchQuery) | Q(created_at__icontains=SearchQuery), is_delete=True)
        else:
            DepartmentList = user_models.Department.objects.filter(
                is_delete=True)

        paginator = Paginator(DepartmentList, DataNumber)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        Pages = paginator.get_elided_page_range(
            page_obj.number, on_each_side=0, on_ends=1)

        context = {
            'page_obj': page_obj,
            'SearchQuery': SearchQuery,
            'DataNumber': DataNumber,
            'TotalDepartments': len(DepartmentList),
            'Pages': Pages
        }
        return render(request, 'Layout/Admin/Recycle/department.html', context)

    else:
        return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def Positions(request):
    if request.user.is_superuser:
        CheckSearchQuery = 'SearchQuery' in request.GET
        CheckDataNumber = 'DataNumber' in request.GET
        DataNumber = 10
        SearchQuery = ''
        PositionList = []

        if CheckDataNumber:
            DataNumber = int(request.GET['DataNumber'])

        if CheckSearchQuery:
            SearchQuery = request.GET['SearchQuery']
            PositionList = user_models.Position.objects.filter(
                Q(position_name__icontains=SearchQuery) | Q(created_at__icontains=SearchQuery), is_delete=True)
        else:
            PositionList = user_models.Position.objects.filter(is_delete=True)

        paginator = Paginator(PositionList, DataNumber)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        Pages = paginator.get_elided_page_range(
            page_obj.number, on_each_side=0, on_ends=1)

        context = {
            'page_obj': page_obj,
            'SearchQuery': SearchQuery,
            'DataNumber': DataNumber,
            'TotalPositions': len(PositionList),
            'Pages': Pages
        }
        return render(request, 'Layout/Admin/Recycle/position.html', context)

    else:
        return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def Category(request):
    if request.user.is_superuser:
        CheckSearchQuery = 'SearchQuery' in request.GET
        CheckDataNumber = 'DataNumber' in request.GET
        DataNumber = 10
        SearchQuery = ''
        CategoryList = []

        if CheckDataNumber:
            DataNumber = int(request.GET['DataNumber'])

        if CheckSearchQuery:
            SearchQuery = request.GET['SearchQuery']
            CategoryList = ticket_models.Category.objects.filter(
                Q(name__icontains=SearchQuery) | Q(created_at__icontains=SearchQuery), is_delete=True)
        else:
            CategoryList = ticket_models.Category.objects.filter(
                is_delete=True)

        paginator = Paginator(CategoryList, DataNumber)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        Pages = paginator.get_elided_page_range(
            page_obj.number, on_each_side=0, on_ends=1)

        context = {
            'page_obj': page_obj,
            'SearchQuery': SearchQuery,
            'DataNumber': DataNumber,
            'TotalCategories': len(CategoryList),
            'Pages': Pages
        }
        return render(request, 'Layout/Admin/Recycle/category.html', context)

    else:
        return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def Tickets(request):
    if request.user.is_superuser:
        CheckSearchQuery = 'SearchQuery' in request.GET
        CheckDataNumber = 'DataNumber' in request.GET
        DataNumber = 10
        SearchQuery = ''
        TicketsList = []

        if CheckDataNumber:
            DataNumber = int(request.GET['DataNumber'])

        if CheckSearchQuery:
            SearchQuery = request.GET['SearchQuery']
            TicketsList = ticket_models.Tickets.objects.filter(Q(ticket_number__icontains=SearchQuery)
                                                               | Q(title__icontains=SearchQuery) | Q(
                description__icontains=SearchQuery) | Q(status__icontains=SearchQuery)
                | Q(priority__icontains=SearchQuery) | Q(category__name__icontains=SearchQuery)
                | Q(userID__first_name__icontains=SearchQuery) | Q(userID__last_name__icontains=SearchQuery), is_delete=True)
        else:
            TicketsList = ticket_models.Tickets.objects.filter(is_delete=True)

        paginator = Paginator(TicketsList, DataNumber)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        Pages = paginator.get_elided_page_range(
            page_obj.number, on_each_side=0, on_ends=1)

        context = {
            'page_obj': page_obj,
            'SearchQuery': SearchQuery,
            'DataNumber': DataNumber,
            'TotalTickets': len(TicketsList),
            'Pages': Pages
        }
        return render(request, 'Layout/Admin/Recycle/tickets.html', context)

    else:
        return render(request, 'Auth/404.html')


def ManageRecycle(request, id):

    if request.method == 'POST':
        type = request.POST.get('Type')
        action = ''
        message = ''
        row = None
        if request.user.is_superuser:
            if type == 'Department':
                row = user_models.Department.objects.get(id=int(id))
                message = "Department Has been Restored Successfully"
                action = f"Department with the name of {row.dept_name} has been Restored Successfully"

            if type == 'Position':
                row = user_models.Position.objects.get(id=int(id))
                message = "Position Has been Restored Successfully"
                action = f"Position with the name of {row.position_name} has been Restored Successfully"

            if type == 'Category':
                row = ticket_models.Category.objects.get(id=int(id))
                message = "Category Has been Restored Successfully"
                action = f"Category with the name of {row.name} has been Restored Successfully"

            if type == 'Tickets':
                row = ticket_models.Tickets.objects.get(id=id)
                message = f"Ticket with the ticket number of {row.ticket_number}  Has been Restored Successfully"
                action = f"Ticket with the ticket number of {row.ticket_number} has been Restored Successfully"
                
            if type == 'Users':
                row = user_models.Users.objects.get(id=id)
                message = f"User with the Username of {row.username}  Has been Restored Successfully"
                action = f"User with the Username of {row.username}  Has been Restored Successfully"

            if row is not None:
                row.is_delete = False
                row.save()
                username = request.user.username
                names = request.user.first_name + ' ' + request.user.last_name
                avatar = str(request.user.avatar)
                module = "Recycle Module"
                action = action
                sendTrials(request, username, names,
                           avatar, action, module)

                return JsonResponse({'isError': False,  'Message': message}, status=200)

            return JsonResponse({'isError': True,  'Message': "Unkown Operation"}, status=200)

        else:
            return render(request, 'Auth/404.html')
