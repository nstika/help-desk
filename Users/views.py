
import datetime
import json
import sys
import traceback

from django.http import JsonResponse
from . import models
from Tickets import models as ticket_models
from django.forms import ValidationError
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate,  logout
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
import httpagentparser
from django.db.models import Q
from django.db.models.deletion import RestrictedError
from django.core.paginator import Paginator

from django.contrib.auth.hashers import check_password
from Tickets import models as tickets_models
from Projects import models as project_models
# Create your views here.
from django.db.models import Q, Count

currentTime = datetime.datetime.today()


def Login(request):
    # Checking if the user is logged in
    if request.user.is_authenticated == False:
        # Checking if the send request
        if request.method == 'POST':
            email = request.POST.get('Email').lower()
            password = request.POST.get('Password')
            # create instance from the user
            user = authenticate(email=email, password=password)
            check = models.Users.objects.filter(
                email=email, is_delete=False)
            if len(check) > 0:
                is_active = check_password(password, check[0].password)
                username = check[0].username
                avatar = str(check[0].avatar)
                name = check[0].first_name + ' ' + check[0].last_name
            else:
                is_active = False
            # check if user created
            if user is not None:
                login(request, user)
                action = name + " logged into the System"
                module = "Users Module"
                sendTrials(request, username, name, avatar, action, module)

                return redirect('Dashboard')

            else:
                if is_active:
                    return render(request, 'Auth/login.html', {'Message': 'Your account is Inactive. Contact to the office'})
                else:
                    return render(request, 'Auth/login.html', {'Message': 'Email or Password is invalid'})

        return render(request, 'Auth/login.html')
    else:
        return redirect('Dashboard')


def Logout(request):
    username = request.user.username
    name = request.user.first_name + ' ' + request.user.last_name
    avatar = str(request.user.avatar)
    module = "Users Module"
    action = name + " Logged out the System"
    sendTrials(request, username, name, avatar, action, module)
    logout(request)
    return redirect('Login')


@login_required(login_url='Login')
def Dashboard(request):
    # for admin and superuser Dashboard
    if request.user.is_admin == True or request.user.is_superuser == True:

        # Report about users
        currentMonth = currentTime.strftime('%m')
        currentYear = currentTime.strftime('%Y')
        prevMonth = '12' if currentMonth == 1 else str(int(currentMonth) - 1)
        prevYear = str(int(currentYear) -
                       1) if currentYear == 1 else currentYear

        totalUsers = models.Users.objects.filter(
            ~Q(is_superuser=True), is_delete=False).count()
        totalAdmins = models.Users.objects.filter(
            is_admin=True, is_delete=False).count()
        lastMonthAdmins = models.Users.objects.filter(
            is_admin=True, created_at__year=prevYear, created_at__month=prevMonth, is_delete=False).count()
        currentMonthAdmins = models.Users.objects.filter(
            is_admin=True,  created_at__year=currentYear, created_at__month=currentMonth, is_delete=False).count()

        totalAgents = models.Users.objects.filter(
            is_agent=True, is_delete=False).count()
        lastMonthAgents = models.Users.objects.filter(
            is_agent=True, created_at__month=prevMonth, created_at__year=prevYear, is_delete=False).count()
        currentMonthAgents = models.Users.objects.filter(
            is_agent=True, created_at__month=currentMonth, created_at__year=currentYear, is_delete=False).count()

        totalClients = models.Users.objects.filter(
            is_client=True, is_delete=False).count()
        lastMonthClients = models.Users.objects.filter(
            is_client=True, created_at__month=prevMonth, created_at__year=prevYear, is_delete=False).count()
        currentMonthClients = models.Users.objects.filter(
            is_client=True, created_at__month=currentMonth, created_at__year=currentYear, is_delete=False).count()
        # Report about users
        # Rport about tickets
        all_tickets = tickets_models.Tickets.objects.filter(
            is_delete=False).count()
        active_tockets = tickets_models.Tickets.objects.filter(
            ~Q(status="Closed"), is_delete=False).count()
        closed_tockets = tickets_models.Tickets.objects.filter(
            Q(status="Closed"), is_delete=False).count()
        new_tickets = tickets_models.Tickets.objects.filter(
            Q(status="On-Hold"), is_delete=False).count()
        inprogress_tockets = tickets_models.Tickets.objects.filter(
            Q(status="Inprogress"), is_delete=False).count()
        last_5_tickets = tickets_models.Tickets.objects.filter(Q(status="On-Hold") | Q(status="Re-Open") | Q(status='Assigned') | Q(status='Inprogress'))[0:8] if len(tickets_models.Tickets.objects.filter(Q(status="On-Hold") | Q(
            status="Re-Open") | Q(status='Assigned') | Q(status='Inprogress'))) > 8 else tickets_models.Tickets.objects.filter(Q(status="On-Hold") | Q(status="Re-Open") | Q(status='Inprogress') | Q(status='Assigned'), is_delete=False)

        # Chart Report
        # ------------
        # Different Priorities
        # High, Critical, Low, Medium
        checkYear = 'year' in request.GET
        checkMonth = 'month' in request.GET

        year = currentTime.year
        month = currentTime.month
        dateFilter = {
            'created_at__year': year
        }

        if checkYear:
            year = int(request.GET.get('year'))

            dateFilter = {}

            dateFilter['created_at__year'] = year

        # if checkMonth:
        #     month = int(request.GET.get('month'))

        #     if month != 0:
        #         dateFilter['created_at__month'] = 11

        # Get ticket Years
        years = []
        temp = []
        ticket_years = ticket_models.Tickets.objects.all().order_by('-created_at')

        for xList in range(0, len(ticket_years)):
            check_year = str(ticket_years[xList].created_at)[0:4]
            is_exists = check_year in temp
            if is_exists == False:
                temp.append(check_year)
                years.append({
                    "value": check_year,
                    "checked": False if int(check_year) != year else True
                })

        chart_data = [
            {
                'Total': ticket_models.Tickets.objects.filter(Q(priority="Critical"), Q(**dateFilter, _connector=Q.AND)).count(),
                'Active': ticket_models.Tickets.objects.filter(Q(priority="Critical"), ~Q(status='Closed'), Q(**dateFilter, _connector=Q.AND)).count(),
                'Inactive': ticket_models.Tickets.objects.filter(Q(priority="Critical"),  Q(status='Closed'), Q(**dateFilter, _connector=Q.AND)).count(),
            },
            {
                'Total': ticket_models.Tickets.objects.filter(Q(priority="High"), Q(**dateFilter, _connector=Q.AND)).count(),
                'Active': ticket_models.Tickets.objects.filter(Q(priority="High"), ~Q(status='Closed'), Q(**dateFilter, _connector=Q.AND)).count(),
                'Inactive': ticket_models.Tickets.objects.filter(Q(priority="High"),  Q(status='Closed'), Q(**dateFilter, _connector=Q.AND)).count(),
            },
            {
                'Total': ticket_models.Tickets.objects.filter(Q(priority="Medium"), Q(**dateFilter, _connector=Q.AND)).count(),
                'Active': ticket_models.Tickets.objects.filter(Q(priority="Medium"), ~Q(status='Closed'), Q(**dateFilter, _connector=Q.AND)).count(),
                'Inactive': ticket_models.Tickets.objects.filter(Q(priority="Medium"),  Q(status='Closed'), Q(**dateFilter, _connector=Q.AND)).count(),
            },
            {
                'Total': ticket_models.Tickets.objects.filter(Q(priority="Low"), Q(**dateFilter, _connector=Q.AND)).count(),
                'Active': ticket_models.Tickets.objects.filter(Q(priority="Low"), ~Q(status='Closed'), Q(**dateFilter, _connector=Q.AND)).count(),
                'Inactive': ticket_models.Tickets.objects.filter(Q(priority="Low"),  Q(status='Closed'), Q(**dateFilter, _connector=Q.AND)).count(),
            },
        ]

        # Rport about tickets

        # Report about trials
        last_5_trials = models.AuditTrials.objects.all().order_by('-date_of_action')[:5] if len(
            models.AuditTrials.objects.all()) > 5 else models.AuditTrials.objects.all().order_by('-date_of_action')
        # Report about trials

        context = {
            'Users': {
                'Total': {
                    'Clients': {
                        'Value': totalClients,
                        'Letter': '',
                        'Percentage': totalClients/totalUsers*100 if totalClients != 0 else 0,
                        'LastMonth': lastMonthClients,
                        'CurrentMonth': currentMonthClients
                    },
                    'Admins': {
                        'Value': totalAdmins,
                        'Letter': '',
                        'Percentage': totalAdmins/totalUsers*100 if totalAdmins != 0 else 0,
                        'LastMonth': lastMonthAdmins,
                        'CurrentMonth': currentMonthAdmins
                    },
                    'Agents': {
                        'Value': totalAgents,
                        'Letter': '',
                        'Percentage': totalAgents/totalUsers*100 if totalAgents != 0 else 0,
                        'LastMonth': lastMonthAgents,
                        'CurrentMonth': currentMonthAgents
                    }
                }
            },
            'Tickets': {
                "Years": years,
                'Month': month,
                'Total': {
                    'All': {
                        'Value': all_tickets,
                        'Letter': '',
                    },
                    'Active': {
                        'Value': active_tockets,
                        'Letter': '',
                        'Percentage': active_tockets/all_tickets*100 if active_tockets != 0 else 0
                    },
                    'Closed': {
                        'Value': closed_tockets,
                        'Letter': '',
                        'Percentage': closed_tockets/all_tickets*100 if closed_tockets != 0 else 0


                    },
                    'New': {
                        'Value': new_tickets,
                        'Letter': '',
                    },
                    'Inprogress': {
                        'Value': inprogress_tockets,
                        'Letter': '',
                        'Percentage': inprogress_tockets/all_tickets*100 if inprogress_tockets != 0 else 0

                    }
                },
                'ChartData': json.dumps(chart_data),
                'Last5': last_5_tickets
            },
            "Trials": last_5_trials
        }
        return render(request, 'Layout/Admin/admin_dashboard.html', context)

    # for agent Dashboard
    if request.user.is_agent == True:
        TotalAssigned = tickets_models.AssignTicket.objects.filter(
            userID=request.user.id, is_removed=False).count()
        TotalAccept = tickets_models.AssignTicket.objects.filter(
            userID=request.user.id, is_accepted=True, is_removed=False).count()
        TotalInprogress = tickets_models.AssignTicket.objects.filter(
            userID=request.user.id, is_accepted=True, ticketID__status="Inprogress", is_removed=False).count()
        TotalIClosed = tickets_models.AssignTicket.objects.filter(
            userID=request.user.id, is_accepted=True, ticketID__status="Closed", is_removed=False).count()
        TotalIAssigned = tickets_models.AssignTicket.objects.filter(
            userID=request.user.id, ticketID__status="Assigned", is_removed=False).count()

        CheckSearchQuery = 'SearchQuery' in request.GET

        CheckDataNumber = 'DataNumber' in request.GET
        CheckFilterStatus = 'FilterStatus' in request.GET
        FilterStatus = {}
        status = "All"
        DataNumber = 10
        SearchQuery = ''
        TicketsList = []

        if CheckDataNumber:
            DataNumber = int(request.GET['DataNumber'])

        if CheckFilterStatus:
            status = request.GET['FilterStatus']

            if status != "All":
                FilterStatus['ticketID__status'] = status

        if CheckSearchQuery:
            SearchQuery = request.GET['SearchQuery']
            TicketsList = tickets_models.AssignTicket.objects.filter(Q(ticketID__ticket_number__icontains=SearchQuery)
                                                                     | Q(ticketID__title__icontains=SearchQuery) | Q(
                ticketID__description__icontains=SearchQuery) | Q(ticketID__status__icontains=SearchQuery)
                | Q(ticketID__priority__icontains=SearchQuery) | Q(ticketID__category__name__icontains=SearchQuery)
                | Q(ticketID__userID__first_name__icontains=SearchQuery) | Q(ticketID__userID__last_name__icontains=SearchQuery), is_removed=False, userID=request.user.id, **FilterStatus)
        else:
            TicketsList = tickets_models.AssignTicket.objects.filter(
                is_removed=False, userID=request.user.id, **FilterStatus).order_by('-created_at')

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
            'TotalAssigned': TotalAssigned,
            'TotalAccept': TotalAccept,
            'TotalInprogress': TotalInprogress,
            'TotalIClosed': TotalIClosed,
            'TotalIAssigned': TotalIAssigned,
            'Status': status
        }
        return render(request, 'Layout/Agent/agent_dashboard.html', context)

    # for client Dashboard
    if request.user.is_client == True:

        client_tickets = tickets_models.Tickets.objects.filter(
            userID=request.user.id, is_delete=False).count()
        active_tickets = tickets_models.Tickets.objects.filter(
            ~Q(status="Closed"), userID=request.user.id, is_delete=False).count()
        closed_tickets = tickets_models.Tickets.objects.filter(
            Q(status="Closed"), userID=request.user.id, is_delete=False).count()
        CheckSearchQuery = 'SearchQuery' in request.GET
        CheckDataNumber = 'DataNumber' in request.GET
        DataNumber = 10
        SearchQuery = ''
        TicketsList = []

        if CheckDataNumber:
            DataNumber = int(request.GET['DataNumber'])

        if CheckSearchQuery:
            SearchQuery = request.GET['SearchQuery']
            TicketsList = tickets_models.Tickets.objects.filter(Q(ticket_number__icontains=SearchQuery)
                                                                | Q(title__icontains=SearchQuery)
                                                                | Q(description__icontains=SearchQuery)
                                                                | Q(status__icontains=SearchQuery)
                                                                | Q(priority__icontains=SearchQuery)
                                                                | Q(category__name__icontains=SearchQuery)
                                                                | Q(userID__first_name__icontains=SearchQuery)
                                                                | Q(userID__last_name__icontains=SearchQuery), userID=request.user.id, is_delete=False)
        else:
            TicketsList = tickets_models.Tickets.objects.filter(
                userID=request.user.id, is_delete=False).order_by('-created_at')

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
            'Pages': Pages,
            'AllClientTickets': client_tickets,
            'active_tickets': active_tickets,
            'closed_tickets': closed_tickets

        }

        return render(request, 'Layout/Customer/client_dashboard.html', context)

    # anonymous user
    return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def Department(request):
    if request.user.has_perm('Users.view_department') and not request.user.is_client:
        return render(request, 'Layout/Admin/Department/departments.html')
    else:
        return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def Profile(request):
    return render(request, 'Auth/profile.html')


@login_required(login_url='Login')
def Users(request):
    if not request.user.is_client and request.user.has_perm('Users.add_users') or request.user.has_perm('Users.add_agent'):
        context = {
            'page': request.session['user_page_indicator'] 
        }
        return render(request, 'Layout/Admin/Users/add_user.html' , context)
    else:
        return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def Clients(request):
    if not request.user.is_client and request.user.has_perm('Users.add_client'):
        return render(request, 'Layout/Admin/Client/add_client.html')
    else:
        return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def ClientList(request):
    if not request.user.is_client and request.user.has_perm('Users.view_client'):
        CheckSearchQuery = 'SearchQuery' in request.GET
        CheckDataNumber = 'DataNumber' in request.GET
        DataNumber = 10
        SearchQuery = ''
        Users = ''
        ClientsList = []

        if CheckDataNumber:
            DataNumber = int(request.GET['DataNumber'])

        if CheckSearchQuery:
            SearchQuery = request.GET['SearchQuery']
            ClientsList = models.Users.objects.filter(Q(username__icontains=SearchQuery) | Q(email__icontains=SearchQuery) | Q(
                first_name__icontains=SearchQuery) | Q(last_name__icontains=SearchQuery) | Q(phone__icontains=SearchQuery) | Q(position__position_name__icontains=SearchQuery) | Q(department__dept_name__icontains=SearchQuery), is_client=True, is_delete=False)
        else:
            ClientsList = models.Users.objects.filter(
                is_client=True, is_delete=False)

        paginator = Paginator(ClientsList, DataNumber)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        Pages = paginator.get_elided_page_range(
            page_obj.number, on_each_side=0, on_ends=1)

        context = {
            'page_obj': page_obj,
            'SearchQuery': SearchQuery,
            'DataNumber': DataNumber,
            'TotalClients': len(ClientsList),
            'Pages': Pages
        }
        return render(request, 'Layout/Admin/Client/client_list.html', context)

    else:
        return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def UsersList(request):
    if not request.user.is_client and request.user.has_perm('Users.view_users'):
        CheckSearchQuery = 'SearchQuery' in request.GET
        CheckDataNumber = 'DataNumber' in request.GET
        DataNumber = 10
        SearchQuery = ''
        UsersList = []

        if CheckDataNumber:
            DataNumber = int(request.GET['DataNumber'])

        if CheckSearchQuery:
            SearchQuery = request.GET['SearchQuery']
            UsersList = models.Users.objects.filter(Q(username__icontains=SearchQuery) | Q(email__icontains=SearchQuery) | Q(
                first_name__icontains=SearchQuery) | Q(last_name__icontains=SearchQuery) | Q(phone__icontains=SearchQuery) | Q(position__position_name__icontains=SearchQuery) | Q(department__dept_name__icontains=SearchQuery), Q(is_superuser=True) | Q(is_admin=True), is_delete=False)
        else:
            UsersList = models.Users.objects.filter(
                Q(is_superuser=True) | Q(is_admin=True), is_delete=False)

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

        # Store session to manage go back button for agent and admin users
        request.session['user_page_indicator'] = 'UsersList'

        return render(request, 'Layout/Admin/Users/user_lists.html', context)
    else:
        return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def AgentsList(request):
    if not request.user.is_client and request.user.has_perm('Users.view_agent'):
        CheckSearchQuery = 'SearchQuery' in request.GET
        CheckDataNumber = 'DataNumber' in request.GET
        DataNumber = 10
        SearchQuery = ''
        AgentsList = []

        if CheckDataNumber:
            DataNumber = int(request.GET['DataNumber'])

        if CheckSearchQuery:
            SearchQuery = request.GET['SearchQuery']
            AgentsList = models.Users.objects.filter(Q(username__icontains=SearchQuery) | Q(email__icontains=SearchQuery) | Q(
                first_name__icontains=SearchQuery) | Q(last_name__icontains=SearchQuery) | Q(phone__icontains=SearchQuery) | Q(position__position_name__icontains=SearchQuery) | Q(department__dept_name__icontains=SearchQuery), is_agent=True, is_delete=False)
        else:
            AgentsList = models.Users.objects.filter(
                is_agent=True, is_delete=False)

        paginator = Paginator(AgentsList, DataNumber)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        Pages = paginator.get_elided_page_range(
            page_obj.number, on_each_side=0, on_ends=1)

        context = {
            'page_obj': page_obj,
            'SearchQuery': SearchQuery,
            'DataNumber': DataNumber,
            'TotalAgents': len(AgentsList),
            'Pages': Pages
        }

        # Store session to manage go back button for agent and admin users
        request.session['user_page_indicator'] = 'AgentsList'

        return render(request, 'Layout/Admin/Agents/agent_list.html', context)
    else:
        return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def Positions(request):
    if not request.user.is_client and request.user.has_perm('Users.view_position'):
        return render(request, 'Layout/Admin/Position/positions.html')
    else:
        return render(request, 'Auth/404.html')

# Data Managements


@login_required(login_url='Login')
def ManagePosition(request, id):
    try:
        if id == 0:
            # Get All Positions

            if request.method == 'GET':
                if not request.user.is_client and request.user.has_perm('Users.view_position'):
                    Positions = models.Position.objects.filter(is_delete=False)
                    message = []
                    for xPositions in range(0, len(Positions)):
                        message.append({
                            'id': Positions[xPositions].id,
                            'name': Positions[xPositions].position_name,
                            'created_at': PreviewDate(Positions[xPositions].created_at, True),
                            'modified_at': 'No Modified' if Positions[xPositions].modified_at is None else PreviewDate(Positions[xPositions].modified_at, True),
                        })
                    return JsonResponse({'isError': False, 'Message': message}, status=200)
                else:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

            # Post New Positions
            if request.method == 'POST':
                if not request.user.is_client and request.user.has_perm('Users.add_position'):
                    name = request.POST.get('name')

                    if models.Position.objects.filter(position_name=name).exists():
                        return JsonResponse({'isError': True, 'Message': name+' already exists'})
                    else:

                        Position = models.Position(position_name=name)
                        Position.save()
                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Users Module / Position Table"
                        action = "Created new position name of " + name
                        sendTrials(request, username, names,
                                   avatar, action, module)
                        message = {
                            'isError': False,
                            'Message': 'New Position has been successfully created'
                        }
                        return JsonResponse(message, status=200)
                else:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

        else:
            # Get Single Position And Check if the user has the permisison
            if request.method == 'GET':
                if not request.user.is_client and request.user.has_perm('Users.view_position'):

                    Position = models.Position.objects.get(
                        id=id, is_delete=False)

                    message = {
                        'id': Position.id,
                        'name': Position.position_name,
                    }
                    return JsonResponse({'isError': False, 'Message': message}, status=200)

                else:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

            # Delete Position And Check if the user has the permisison
            if request.method == 'DELETE':
                if not request.user.is_client and request.user.has_perm('Users.delete_position'):
                    positions = models.Position.objects.get(
                        id=id, is_delete=False)
                    checkUser = models.Users.objects.filter(
                        position=positions.id).exists()
                    if checkUser:
                        return JsonResponse({'isError': True, 'Message': 'Cannot delete some instances of model because they are referenced through restricted foreign keys'}, status=200)
                    else:
                        pname = positions.position_name
                        positions.is_delete = True
                        positions.save()
                        username = request.user.username
                        name = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Users Module / Position"
                        action = "Deleted position name of " + pname
                        sendTrials(request, username, name,
                                   avatar, action, module)
                        message = {
                            'isError': False,
                            'Message': pname+' has been successfully deleted!!'
                        }
                        return JsonResponse(message, status=200)

                else:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

            # Update Position And Check if the user has the permisison
            if request.method == 'POST':
                if not request.user.is_client and request.user.has_perm('Users.change_position'):
                    name = request.POST.get('name')

                    Position = models.Position.objects.get(
                        id=id, is_delete=False)
                    if models.Position.objects.filter(position_name=name).exists() and name.casefold() != Position.position_name.casefold():
                        return JsonResponse({'isError': True, 'Message': 'Position already exists'})
                    else:
                        if name == Position.position_name:
                            action = "Edited position name of " + name
                        else:
                            action = "Edited position name of " + Position.position_name + ' to '+name
                        Position.position_name = name
                        # Position.modified_at = str(currentTime)
                        Position.save()
                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Users Module / Position Table"

                        sendTrials(request, username, names,
                                   avatar, action, module)
                        return JsonResponse({'isError': False, 'Message': 'Position has been successfully updated'}, status=200)

                else:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)
    except Exception as error:
        username = request.user.username
        name = request.user.first_name + ' ' + request.user.last_name
        sendException(
            request, username, name, error)
        message = {
            'isError': True,
            'Message': 'On Error Occurs . Please try again or contact system administrator'
        }
        return JsonResponse(message, status=200)


@login_required(login_url='Login')
def ManageDepartment(request, id):
    try:
        if id == 0:
            # Get All Departments
            if request.method == 'GET':
                if not request.user.is_client and request.user.has_perm('Users.view_department'):
                    Departments = models.Department.objects.filter(
                        is_delete=False)
                    message = []
                    for xDeptments in range(0, len(Departments)):
                        message.append({
                            'id': Departments[xDeptments].id,
                            'name': Departments[xDeptments].dept_name,
                            'created_at': PreviewDate(Departments[xDeptments].created_at, True),
                            'modified_at': 'No Modified' if Departments[xDeptments].modified_at is None else PreviewDate(Departments[xDeptments].modified_at, True),
                        })
                    return JsonResponse({'isError': False, 'Message': message}, status=200)
                else:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)
            # Post New Departments
            if request.method == 'POST':
                if not request.user.is_client and request.user.has_perm('Users.add_department'):
                    name = request.POST.get('name')

                    if models.Department.objects.filter(dept_name=name).exists():
                        return JsonResponse({'isError': True, 'Message': name+' already exists'})
                    else:

                        Department = models.Department(dept_name=name)
                        Department.save()
                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Users Module / department Table"
                        action = "Created new department name of " + name
                        sendTrials(request, username, names,
                                   avatar, action, module)
                        message = {
                            'isError': False,
                            'Message': 'New Department has been successfully created'
                        }
                        return JsonResponse(message, status=200)
                else:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

        else:
            # Get Single Departments And Check if the user has the permisison
            if request.method == 'GET':
                if not request.user.is_client and request.user.has_perm('Users.view_department'):
                    Departments = models.Department.objects.get(
                        id=id, is_delete=False)
                    message = {
                        'id': Departments.id,
                        'name': Departments.dept_name,
                    }
                    return JsonResponse({'isError': False, 'Message': message}, status=200)

                else:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

            # Delete Departments And Check if the user has the permisison
            if request.method == 'DELETE':
                if not request.user.is_client and request.user.has_perm('Users.delete_department'):

                    Departments = models.Department.objects.get(
                        id=id, is_delete=False)
                    checkDepartment = models.Users.objects.filter(
                        department=Departments.id).exists()
                    if checkDepartment:
                        return JsonResponse({'isError': True, 'Message': 'Cannot delete some instances of model because they are referenced through restricted foreign keys'}, status=200)
                    else:
                        Dname = Departments.dept_name
                        Departments.is_delete = True
                        Departments.save()
                        username = request.user.username
                        name = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Users Module / Department"
                        action = "Deleted department name of " + name
                        sendTrials(request, username, name,
                                   avatar, action, module)
                        message = {
                            'isError': False,
                            'Message': Dname+' has been successfully deleted!!'
                        }
                        return JsonResponse(message, status=200)

                else:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

            # Update Departments And Check if the user has the permisison
            if request.method == 'POST':
                if not request.user.is_client and request.user.has_perm('Users.change_department'):
                    name = request.POST.get('name')
                    Department = models.Department.objects.get(
                        id=id, is_delete=False)
                    if models.Department.objects.filter(dept_name=name).exists() and name.casefold() != Department.dept_name.casefold():
                        return JsonResponse({'isError': True, 'Message': name+' already exists'})
                    else:
                        if name == Department.dept_name:
                            action = "Edited department name of " + name
                        else:
                            action = "Edited department name of " + Department.dept_name + ' to '+name
                        Department.dept_name = name
                        # Department.modified_at = currentTime
                        Department.save()
                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Users Module / Department Table"

                        sendTrials(request, username, names,
                                   avatar, action, module)
                        return JsonResponse({'isError': False, 'Message': 'Department has been successfully updated'}, status=200)

                else:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)
    except Exception as error:
        username = request.user.username
        name = request.user.first_name + ' ' + request.user.last_name
        sendException(
            request, username, name, error)
        message = {
            'isError': True,
            'Message': 'On Error Occurs . Please try again or contact system administrator'
        }
        return JsonResponse(message, status=200)


@login_required(login_url='Login')
def ManageUsers(request, id):
    try:
        if id == 0:
            if request.method == 'POST':
                Type = request.POST.get('type')
                fname = request.POST.get('fname')
                lname = request.POST.get('lname')
                phone = request.POST.get('phone')
                email = request.POST.get('email').lower()
                position = request.POST.get('position')
                department = request.POST.get('department')
                gender = request.POST.get('gender')
                image = request.FILES['image']

                extention = image.name.split(".")[-1]
                extension_types = ['JPEG', 'jpeg', 'JPG', 'jpg', 'png', "PNG"]

                if request.user.is_client:
                    return render(request, 'Auth/404.html')

                if not extention in extension_types:
                    return JsonResponse({'isError': True, 'Message': 'This ' + image.name+'  does not support image extentions.Please upload Image'})

                if image.size > 2621440:
                    return JsonResponse({'isError': True, 'Message': image.name+'  file is more than 2mb size'})

                if models.Users.objects.filter(email=email).exists():
                    return JsonResponse({'isError': True, 'Message': email+' already exists'})

                if len(phone) > 3:
                    return JsonResponse({'isError': True, 'Message': 'Phone Number are allowed Only 3 digits '})

                # if models.Users.objects.filter(phone=phone).exists():
                #     return JsonResponse({'isError': True, 'Message': 'This Phone already exists'})

                if position == '':
                    return JsonResponse({'isError': True, 'Message': 'Select Position'})

                if department == '':
                    return JsonResponse({'isError': True, 'Message': 'Select Department'})

                is_clients = True if Type == 'Client' else False
                is_agents = True if Type == 'Agent' else False
                is_admins = True if Type == 'Admin' else False
                is_supers = True if Type == 'Super' else False

                if Type == 'Client' and request.user.has_perm('Users.add_client'):
                    response = models.Users.create_user(
                        fname, lname, email, phone, gender,  position, department, image, is_admins, is_agents, is_clients, is_supers, request)

                    if response['isError'] == False:
                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Users Module / users"
                        action = "Created new client name of " + fname+" "+lname
                        sendTrials(request, username, names,
                                   avatar, action, module)
                        message = {
                            'isError': False,
                            'Message': fname+' has been successfully added'
                        }
                        return JsonResponse(message, status=200)
                    else:
                        return JsonResponse(response, status=200)

                elif Type == 'Admin' or Type == 'Agent' and request.user.has_perm('Users.add_users'):
                    response = models.Users.create_user(
                        fname, lname, email, phone, gender,  position, department, image, is_admins, is_agents, is_clients, is_supers, request)

                    if response['isError'] == False:
                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Users Module / users Table"
                        action = f"Created new {Type.lower()} name of " + \
                            fname+" "+lname
                        sendTrials(request, username, names,
                                   avatar, action, module)
                        message = {
                            'isError': False,
                            'Message': fname+' has been successfully added'
                        }
                        return JsonResponse(message, status=200)
                    else:
                        return JsonResponse(response, status=200)

                elif Type == 'Super' and request.user.is_superuser:
                    response = models.Users.create_user(
                        fname, lname, email, phone, gender,  position, department, image, is_admins, is_agents, is_clients, is_supers, request)

                    if response['isError'] == False:
                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Users Module / users Table"
                        action = "Created new superuser name of " + fname+" "+lname
                        sendTrials(request, username, names,
                                   avatar, action, module)
                        message = {
                            'isError': False,
                            'Message': fname+' has been successfully added'
                        }
                        return JsonResponse(message, status=200)
                    else:
                        return JsonResponse(response, status=200)
                else:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)
        else:
            # Get Single USERS And Check if the user has the permisison
            if request.method == 'GET':
                if not request.user.is_client and request.user.has_perm('Users.view_users') or request.user.has_perm('Users.view_client') or request.user.has_perm('Users.view_agent'):
                    user = models.Users.objects.get(id=id, is_delete=False)
                    message = {
                        'id': user.id,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'phone': user.phone,
                        'gender': user.gender,
                        'department': 'N/A' if user.department is None else user.department.id,
                        'position': 'N/A' if user.position is None else user.position.id,
                    }
                    return JsonResponse({'isError': False, 'Message': message}, status=200)

                else:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

            # Update USERS And Check if the user has the permisison
            if request.method == 'POST':
                if not request.user.is_client and request.user.has_perm('Users.change_users') or request.user.has_perm('Users.change_client') or request.user.has_perm('Users.view_agent'):
                    fname = request.POST.get('fname').strip()
                    lname = request.POST.get('lname').strip()
                    phone = request.POST.get('phone')
                    email = request.POST.get('email').lower()
                    position = request.POST.get('position')
                    department = request.POST.get('department')
                    gender = request.POST.get('gender')
                    User = models.Users.objects.get(id=id)
                    Department = models.Department.objects.get(id=department)
                    Position = models.Position.objects.get(id=position)
                    if models.Users.objects.filter(phone=phone).exists() and phone.casefold() != User.phone.casefold():
                        return JsonResponse({'isError': True, 'Message': "This phone number ("+phone+') already exists'})
                    if len(phone) > 3:
                        return JsonResponse({'isError': True, 'Message': 'Phone Number are allowed Only 3 digits '})

                    if models.Users.objects.filter(email=email).exists() and email.casefold() != User.email.casefold():
                        return JsonResponse({'isError': True, 'Message': "This email ("+email+') already exists'})

                    User.first_name = fname
                    User.last_name = lname
                    User.email = email
                    User.phone = phone
                    User.gender = gender
                    User.department = Department
                    User.position = Position
                    User.save()

                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Users Module / Department Table"
                    action = 'Edited user'
                    sendTrials(request, username, names,
                               avatar, action, module)
                    return JsonResponse({'isError': False, 'Message': 'User has been successfully updated'}, status=200)

                else:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)
    except Exception as error:
        username = request.user.username
        name = request.user.first_name + ' ' + request.user.last_name
        sendException(
            request, username, name, error)
        message = {
            'isError': True,
            'Message': 'On Error Occurs . Please try again or contact system administrator'
        }
        return JsonResponse(message, status=200)


@login_required(login_url='Login')
def ChangePassword(request):
    try:
        type = request.POST.get('type')

        if type is None:
            return render(request, 'Auth/404.html')

        if type == 'ChangePassword' and request.method == 'POST':
            if not request.user.is_client and request.user.has_perm('Users.change_password'):
                userID = models.Users.objects.get(
                    id=request.POST['user'], is_delete=False)
                password = request.POST.get('password')
                confirm = request.POST.get('confirm')

                if password == '':
                    return JsonResponse({'isError': True, "Message": "Please enter password"})
                if confirm == '':
                    return JsonResponse({'isError': True, "Message": "Please enter confirmation password"})
                if password != confirm:
                    return JsonResponse({'isError': True, "Message": "passwords are not matched"})

                userID.set_password(password)
                userID.save()

                username = request.user.username
                names = request.user.first_name + ' ' + request.user.last_name
                avatar = str(request.user.avatar)
                module = "Users Module / Users Table"
                action = f'Changed password for {userID.first_name} {userID.first_name} ({userID.username})'
                sendTrials(request, username, names,
                           avatar, action, module)
                return JsonResponse({'isError': False, 'Message': "User's password has been successfully updated"}, status=200)
            else:
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)

        if type == 'ChangeProfile' and request.method == 'POST':
            is_accapted = False

            if not request.user.is_client and request.user.has_perm('Users.change_users') or request.user.has_perm('Users.change_agent') or request.user.has_perm('Users.change_client'):
                is_accapted = True

            if is_accapted == False:
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)

            # Now change the user's profile
            userid = models.Users.objects.get(
                id=request.POST['userid'], is_delete=False)
            try:
                image = request.FILES['image']
            except KeyError:
                image = ''

            if image is None or image == '':
                return JsonResponse({'isError': True, 'Message': "Upload image file"})

            extention = image.name.split(".")[-1]
            extension_types = ['JPEG', 'jpeg', 'JPG', 'jpg', 'png', "PNG"]

            if not extention in extension_types:
                return JsonResponse({'isError': True, 'Message': 'This ' + image.name+'  does not support image extentions.Please upload Image'})

            if image.size > 2621440:
                return JsonResponse({'isError': True, 'Message': image.name+'  file is more than 2mb size'})

            userid.avatar = image
            userid.save()

            username = request.user.username
            names = request.user.first_name + ' ' + request.user.last_name
            avatar = str(request.user.avatar)
            module = "Users Module / users"
            action = "Edit user's profile name of " + \
                userid.first_name+" "+userid.last_name
            sendTrials(request, username, names,
                       avatar, action, module)

            return JsonResponse({'isError': False, 'Message': 'Profile has been updated'})

        return render(request, 'Auth/404.html')
    except Exception as error:
        username = request.user.username
        name = request.user.first_name + ' ' + request.user.last_name
        sendException(
            request, username, name, error)
        message = {
            'isError': True,
            'Message': 'On Error Occurs . Please try again or contact system administrator'
        }
        return JsonResponse(message, status=200)


@login_required(login_url='Login')
def get_users_links(request):
    Type = request.POST.get('Type')
    CategoryType = request.POST.get('Category')

    if Type == 'get_all_position':
        Positions = models.Position.objects.filter(is_delete=False)
        message = []
        for xPositions in range(0, len(Positions)):
            message.append({
                'id': Positions[xPositions].id,
                'name': Positions[xPositions].position_name,
            })
        return JsonResponse({'isError': False, 'Message': message}, status=200)

    if Type == 'get_all_categories':
        categories = ticket_models.Category.objects.filter(
            is_delete=False, type=CategoryType)
        message = []
        for xCategory in range(0, len(categories)):
            message.append({
                'id': categories[xCategory].id,
                'name': categories[xCategory].name,
            })
        return JsonResponse({'isError': False, 'Message': message}, status=200)

    if Type == 'get_all_department':
        Departments = models.Department.objects.filter(is_delete=False)
        message = []
        for xDeptments in range(0, len(Departments)):
            message.append({
                'id': Departments[xDeptments].id,
                'name': Departments[xDeptments].dept_name,

            })
        return JsonResponse({'isError': False, 'Message': message}, status=200)
    if Type == 'get_all_projects':
        Projects = project_models.Project.objects.filter(
            is_delete=False, is_active=True)
        message = []
        for xProjects in range(0, len(Projects)):
            message.append({
                'id': Projects[xProjects].id,
                'name': Projects[xProjects].title,

            })
        return JsonResponse({'isError': False, 'Message': message}, status=200)


# Functions
def sendTrials(request, username, name, avatar, action, module, model='', brand=''):
    username = username
    name = name
    avatar = avatar
    ip = request.META.get('REMOTE_ADDR')
    get_client_agent = request.META['HTTP_USER_AGENT']
    try:
        detect_os = httpagentparser.detect(
            get_client_agent)['os']['name']
    except KeyError:
        detect_os = get_client_agent
    try:
        browser = httpagentparser.detect(get_client_agent)[
            'browser']['name']
    except KeyError:
        browser = get_client_agent
    action = action
    module = module
    user_agent = str(ip) + ","
    user_agent += str(detect_os) + ',' if brand == '' else brand + ','
    user_agent += browser if model == '' else model
    audit_trails = models.AuditTrials(
        Avatar=avatar,
        Name=name,
        Username=username,
        Actions=action,
        Module=module,
        operating_system=detect_os if brand == '' else brand,
        ip_address=ip,
        browser=browser if model == '' else model,
        user_agent=user_agent)

    audit_trails.save()

    return {
        'title': "Audit Trials Saved Successfully!!",
    }


def PreviewDate(date_string, is_datetime, add_time=True):
    if is_datetime:
        new_date = date_string
        if add_time:
            date_string = new_date.strftime("%a") + ', ' + new_date.strftime(
                "%b") + ' ' + str(new_date.day) + ', ' + str(new_date.year) + '  ' + new_date.strftime("%I") + ':' + new_date.strftime("%M") + ':' + new_date.strftime("%S") + ' ' + new_date.strftime("%p")
        else:
            date_string = new_date.strftime("%a") + ', ' + new_date.strftime(
                "%b") + ' ' + str(new_date.day) + ', ' + str(new_date.year)
    else:
        date_string = str(date_string)
        date_string = date_string.split('-')

        new_date = datetime(int(date_string[0]), int(
            date_string[1]), int(date_string[2]))

        date_string = new_date.strftime("%a") + ', ' + new_date.strftime(
            "%b") + ' ' + str(new_date.day) + ', ' + str(new_date.year)

    return date_string


def sendException(request, username, name, error, avatar='', model='', brand=''):
    username = username
    Name = name
    ip = request.META.get('REMOTE_ADDR')
    get_client_agent = request.META['HTTP_USER_AGENT']
    try:
        detect_os = httpagentparser.detect(
            get_client_agent)['os']['name']
    except KeyError:
        detect_os = get_client_agent
    try:
        browser = httpagentparser.detect(get_client_agent)[
            'browser']['name']
    except KeyError:
        browser = get_client_agent
    trace_err = traceback.format_exc()
    Expected_error = str(sys.exc_info()[0])
    field_error = str(sys.exc_info()[1])
    line_number = str(sys.exc_info()[-1].tb_lineno)
    user_agent = str(ip) + ","
    user_agent += str(detect_os) + ',' if brand == '' else brand + ','
    user_agent += browser if model == '' else model
    error_logs = models.ErrorLogs(
        Avatar=str(request.user.avatar) if avatar == '' else avatar,
        Name=Name,
        Username=username,
        ip_address=ip,
        browser=browser if model == '' else model,
        Expected_error=Expected_error,
        field_error=field_error,
        trace_back=str(trace_err),
        line_number=line_number,
        user_agent=user_agent)

    error_logs.save()

    return {
        'error': str(error),
        'isError': True,
        'title': "An error occurred please contact us"
    }


@login_required(login_url='Login')
def AuditTrials(request):
    if not request.user.is_client and request.user.has_perm('Users.view_audittrials'):
        # Checking if these values been sent throught GET Request Method
        CheckSearchQuery = 'SearchQuery' in request.GET
        CheckDataNumber = 'DataNumber' in request.GET
        DataNumber = 5
        SearchQuery = ''
        Audits = ''

        if CheckDataNumber:
            DataNumber = int(request.GET['DataNumber'])

        if CheckSearchQuery:
            SearchQuery = request.GET['SearchQuery']
            Audits = models.AuditTrials.objects.filter(Q(Username__icontains=SearchQuery) | Q(Name__icontains=SearchQuery) | Q(Module__icontains=SearchQuery) | Q(
                Actions__icontains=SearchQuery) | Q(date_of_action__icontains=SearchQuery) | Q(user_agent__icontains=SearchQuery)).order_by('-date_of_action')
        else:
            Audits = models.AuditTrials.objects.all().order_by('-date_of_action')

        paginator = Paginator(Audits, DataNumber)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        Pages = list(paginator.get_elided_page_range(
            page_obj.number, on_each_side=0, on_ends=1))

        context = {
            'page_obj': page_obj,
            'SearchQuery': SearchQuery,
            'DataNumber': DataNumber,
            'TotalUsers': len(Audits),
            'Pages': Pages
        }
        return render(request, 'Layout/Admin/Logs/audit_trial.html', context)
    else:
        return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def ErrorLogs(request):
    if not request.user.is_client and request.user.has_perm('Users.view_errorlogs'):
        # Checking if these values been sent throught GET Request Method
        CheckSearchQuery = 'SearchQuery' in request.GET
        CheckDataNumber = 'DataNumber' in request.GET
        DataNumber = 5
        SearchQuery = ''
        Errors = ''

        if CheckDataNumber:
            DataNumber = int(request.GET['DataNumber'])

        if CheckSearchQuery:
            SearchQuery = request.GET['SearchQuery']
            Errors = models.ErrorLogs.objects.filter(Q(Username__icontains=SearchQuery) | Q(Name__icontains=SearchQuery) | Q(Expected_error__icontains=SearchQuery) | Q(
                field_error__icontains=SearchQuery) | Q(line_number__icontains=SearchQuery) | Q(date_recorded__icontains=SearchQuery) | Q(user_agent__icontains=SearchQuery)).order_by('-date_recorded')
        else:
            Errors = models.ErrorLogs.objects.all().order_by('-date_recorded')

        paginator = Paginator(Errors, DataNumber)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        Pages = list(paginator.get_elided_page_range(
            page_obj.number, on_each_side=1, on_ends=1))

        context = {
            'page_obj': page_obj,
            'SearchQuery': SearchQuery,
            'DataNumber': DataNumber,
            'TotalUsers': len(Errors),
            'Pages': Pages
        }
        return render(request, 'Layout/Admin/Logs/errors_logs.html', context)
    else:
        return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def ManageErrorLogs(request, id):
    if id == 0:
        pass
    else:
        if request.method == 'GET':
            if not request.user.is_client and request.user.has_perm('Users.view_errorlogs'):
                try:
                    logs = models.ErrorLogs.objects.get(id=id)

                    message = {
                        'ID': logs.id,
                        'TraceBack': logs.trace_back
                    }

                    return JsonResponse({'isError': False, 'Message': message}, status=200)
                except Exception as error:
                    username = request.user.username
                    name = request.user.first_name + ' ' + request.user.last_name
                    sendException(
                        request, username, name, error)
                    message = {
                        'isError': True,
                        'Message': 'On Error Occurs . Please try again or contact system administrator'
                    }
                    return JsonResponse(message, status=200)
            else:
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)


@login_required(login_url='Login')
def ViewUserRolesReportPage(request):
    if not request.user.is_client and request.user.has_perm('Users.role_report'):
        return render(request, 'Layout/Roles/user_role_report.html')
    else:
        return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def SearchRole(request):
    if not request.user.is_client and request.user.has_perm('auth.add_permission') and request.user.has_perm('auth.view_permission') or request.user.has_perm('Users.manage_role_groups'):
        CheckSearch = 'Search' in request.GET

        context = {
            'Message': '',
            'Search': ''
        }

        if CheckSearch:
            Search = request.GET['Search']
            context['Search'] = Search

            # Check if the role exists
            check_permisison = Permission.objects.filter(codename=Search)

            if len(check_permisison) == 0:
                context['Message'] = 'This role does not exist'
            else:
                check_permisison = check_permisison[0]
                context["App"] = check_permisison.content_type.app_label
                context["Model"] = check_permisison.content_type.model
                context['Message'] = 'Yes'

        return render(request, 'Layout/Roles/search_role.html', context)
    else:
        return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def ViewRolesReportPage(request):
    if not request.user.is_client and request.user.has_perm('Users.role_report'):
        return render(request, 'Layout/Roles/role_report.html')
    else:
        return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def ViewRolesPage(request):
    if not request.user.is_client and request.user.has_perm('auth.view_permission') and request.user.has_perm('auth.add_permission'):
        return render(request, 'Layout/Roles/assign_role.html')
    else:
        return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def ViewEditGroupPage(request, group_id):
    if not request.user.is_client and request.user.has_perm('auth.view_group'):
        return render(request, 'Layout/Roles/edit_group.html', {'GroupID': group_id})
    else:
        return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def ViewGroupRolesPage(request):
    if not request.user.is_client and request.user.has_perm('Users.assign_user_to_group'):
        return render(request, 'Layout/Roles/assign_group.html')
    else:
        return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def ViewManageGroupPage(request):
    if not request.user.is_client and request.user.has_perm('auth.view_group'):
        return render(request, 'Layout/Roles/manage_group.html')
    else:
        return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def ManagePermission(request, id):
    if id == '0':
        if request.method == 'POST':
            if not request.user.is_client and request.user.has_perm('auth.add_permission'):
                Type = request.POST.get('type')
                User = request.POST.get('user')
                PermID = int(request.POST.get('permID'))
                if 'AD' in User or 'AG' in User or 'CL' in User:
                    try:
                        if 'AD' in User or 'AG' in User or 'CL' in User:
                            User = models.Users.objects.get(username=User)
                        else:
                            User = models.Users.objects.get(id=int(User))
                        # Get Permisison
                        P = Permission.objects.get(id=PermID)

                        if Type == 'Add':
                            User.user_permissions.add(P)
                        else:
                            User.user_permissions.remove(P)

                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Users-Permission Module"
                        if Type == 'Add':
                            action = 'Granted Permission to' + "_" + \
                                P.codename + " With username of " + User.username
                        else:
                            action = 'Permission Denied to' + "_" + \
                                P.codename + " With username of " + User.username

                        sendTrials(request, username, names,
                                   avatar, action, module)

                        isError = False
                        message = 'Permission Granted' if Type == 'Add' else 'Permission Denied'
                    except Exception as error:
                        username = request.user.username
                        name = request.user.first_name + ' ' + request.user.last_name
                        sendException(
                            request, username, name, error)
                        message = {
                            'isError': True,
                            'Message': 'On Error Occurs . Please try again or contact system administrator'
                        }
                        return JsonResponse(message, status=200)
                else:
                    isError = True
                    message = 'Invalid user or this user specified not allowed for taking permissions'
                return JsonResponse({'isError': isError, 'Message': message}, status=200)
            else:
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)
    else:
        if request.method == 'GET':
            if not request.user.is_client and request.user.has_perm('auth.view_permission'):
                if 'AG' in id or 'AD' in id or 'CL' in id:
                    if 'AG' in id or 'AD' in id or 'CL' in id:
                        User = models.Users.objects.filter(username=id)
                    else:
                        User = models.Users.objects.filter(id=int(id))

                    perms = Permission.objects.all().order_by('content_type')

                    if len(User) > 0:
                        if len(perms) < 0:
                            return JsonResponse({'isError': True, 'Message': 'No Permissions Available'}, status=200)
                        else:
                            id = 0
                            message = []
                            for xPerm in range(0, len(perms)):
                                # Checking if the user has prmisison
                                txt = perms[xPerm].content_type.app_label + \
                                    '.' + perms[xPerm].codename
                                isPermitted = User[0].has_perm(txt)

                                if id != perms[xPerm].content_type.id:

                                    # if len(message) > 0:
                                    #     message[len(message) - 1]['Actions'].append({
                                    #         'Action': perms[xPerm].codename,
                                    #         'isPermitted': isPermitted,
                                    #         'isSuperuser': User[0].is_superuser
                                    #     })

                                    id = perms[xPerm].content_type.id

                                    message.append({
                                        'App': perms[xPerm].content_type.app_label,
                                        'Model': perms[xPerm].content_type.model,
                                        'Actions': [
                                            {
                                                'Action': perms[xPerm].codename,
                                                'ID': perms[xPerm].id,
                                                'isPermitted': isPermitted,
                                                'isSuperuser': User[0].is_superuser
                                            }
                                        ]

                                    })
                                else:
                                    message[len(message) - 1]['Actions'].append({
                                        'Action': perms[xPerm].codename,
                                        'ID': perms[xPerm].id,
                                        'isPermitted': isPermitted,
                                        'isSuperuser': User[0].is_superuser
                                    })
                            # message[len(message) - 1]['Actions'].append({
                            #     'Action': perms[xPerm].codename,
                            #     'ID': perms[xPerm].id,
                            #     'isPermitted': isPermitted,
                            #     'isSuperuser': User[0].is_superuser
                            # })
                            return JsonResponse({'isError': False, 'Message': message}, status=200)
                    else:
                        return JsonResponse({'isError': True, 'Message': 'User does not exist'}, status=200)
                else:
                    return JsonResponse({'isError': True, 'Message': 'Invalid user or this user specified not allowed for taking permissions'}, status=200)
            else:
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)


@login_required(login_url='Login')
def ManageGroupPermission(request, id, _id):
    if id == '0':
        if request.method == 'POST':
            if not request.user.is_client and request.user.has_perm('Users.assign_user_to_group'):
                Type = request.POST.get('type')
                User = request.POST.get('user')
                PermID = int(request.POST.get('permID'))
                if 'AG' in User or 'AD' in User or 'CL' in User:
                    try:
                        if 'AG' in User or 'AD' in User or 'CL' in User:
                            User = models.Users.objects.get(username=User)
                        else:
                            User = models.Users.objects.get(id=int(User))
                        # Get Group
                        P = Group.objects.get(id=PermID)

                        if Type == 'Add':
                            User.groups.add(P)
                        else:
                            User.groups.remove(P)
                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Users-Permission Module"
                        if Type == 'Add':
                            action = "User with username of:" + '_' + \
                                User.username + " added group of " + P.name
                        else:
                            action = "User with username of:" + '_' + \
                                User.username + " removed group of " + P.name
                        sendTrials(request, username, names,
                                   avatar, action, module)

                        isError = False
                        message = 'User has been added to the group ' if Type == 'Add' else 'User has been removed from the group '
                    except Exception as error:
                        username = request.user.username
                        name = request.user.first_name + ' ' + request.user.last_name
                        sendException(
                            request, username, name, error)
                        message = {
                            'isError': True,
                            'Message': 'On Error Occurs . Please try again or contact system administrator'
                        }
                        return JsonResponse(message, status=200)
                else:
                    isError = True
                    message = 'Invalid user or this user specified not allowed for taking permissions'
                return JsonResponse({'isError': isError, 'Message': message}, status=200)
            else:
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)
    else:
        if request.method == 'GET':
            if request.user.has_perm('auth.view_permission') or request.user.has_perm('Users.assign_user_to_group'):
                if 'AG' in id or 'AD' in id or 'CL' in id:
                    if 'AG' in id or 'AD' in id or 'CL' in id:
                        User = models.Users.objects.filter(username=id)
                    else:
                        User = models.Users.objects.filter(id=int(id))

                    groups = Group.objects.all()

                    if len(User) > 0:
                        if len(groups) < 0:
                            return JsonResponse({'isError': True, 'Message': 'No Groups Available'}, status=200)
                        else:
                            id = 0
                            message = []
                            for xGroup in range(0, len(groups)):
                                message.append({
                                    'ID': groups[xGroup].id,
                                    'Count': groups[xGroup].permissions.all().count(),
                                    'Name': groups[xGroup].name,
                                    'IsJoined': True if len(User[0].groups.filter(name=groups[xGroup].name)) > 0 else False,
                                    'IsSuper': True if User[0].is_superuser > 0 else False,
                                })
                            return JsonResponse({'isError': False, 'Message': message}, status=200)
                    else:
                        return JsonResponse({'isError': True, 'Message': 'User does not exist'}, status=200)
                else:
                    return JsonResponse({'isError': True, 'Message': 'Invalid user or this user specified not allowed for taking permissions'}, status=200)
            else:
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)

        if request.method == 'POST':
            if request.user.has_perm('auth.view_group') or request.user.has_perm('Users.assign_user_to_group'):
                GroupID = int(id)

                try:
                    # Get Group
                    group = Group.objects.get(id=GroupID)
                    perms = group.permissions.filter(group=group)
                    message = []
                    isError = False
                    for xPerm in range(0, len(perms)):
                        message.append({
                            'Name': perms[xPerm].name,
                            'Codename': perms[xPerm].codename,
                            'ID': perms[xPerm].id,
                            'GroupID': group.id,
                            'App': perms[xPerm].content_type.app_label,
                            'Model': perms[xPerm].content_type.model,
                        })

                except Exception as error:
                    username = request.user.username
                    name = request.user.first_name + ' ' + request.user.last_name
                    sendException(
                        request, username, name, error)
                    message = {
                        'isError': True,
                        'Message': 'On Error Occurs . Please try again or contact system administrator'
                    }
                    return JsonResponse(message, status=200)
                return JsonResponse({'isError': isError, 'Message': message}, status=200)
            else:
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)

        if request.method == 'DELETE':
            if request.user.has_perm('auth.delete_permission') or request.user.has_perm('Users.remove_role_from_group'):
                GroupID = int(id)
                PermID = int(_id)

                try:
                    # Get Group
                    group = Group.objects.get(id=GroupID)
                    permission = Permission.objects.get(id=PermID)
                    # User = models.Users.objects.get(id=GroupID)
                    # Remove From The Group
                    perms = group.permissions.remove(permission)
                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Users-Permission Module"
                    action = "User with username of:" + '_' + username + \
                        "removed " + permission.codename + " from the group " + group.name
                    sendTrials(request, username, names,
                               avatar, action, module)
                    message = 'Permission removed from the group'
                    isError = False

                    return JsonResponse({'isError': isError, 'Message': message}, status=200)

                except RestrictedError:
                    return JsonResponse({'isError': True, 'Message': 'Cannot delete some instances of model because they are referenced through restricted foreign keys'}, status=200)
            else:
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)


@login_required(login_url='Login')
def PermissonReport(request):
    if request.method == 'POST':
        if not request.user.is_client and request.user.has_perm('Users.role_report'):
            Type = request.POST.get('type')
            message = ''
            Apps = []
            Modal = []
            Codes = []

            if Type == 'GetGroups':
                list = []
                groups = Group.objects.all()
                for xgroup in range(0, len(groups)):
                    list.append({
                        'GroupName': groups[xgroup].name,
                        'GroupID': groups[xgroup].id,
                    })
                message = {
                    'isError': False, 'Message': list
                }

            elif Type == 'GetApps':
                list = []
                contentType = ContentType.objects.all()
                for xApp in range(0, len(contentType)):
                    is_added = contentType[xApp].app_label in Apps
                    if is_added == False:
                        Apps.append(contentType[xApp].app_label)
                        list.append({
                            'AppName': contentType[xApp].app_label,
                        })
                message = {
                    'isError': False, 'Message': list
                }

            elif Type == 'GetModals':
                App = request.POST.get('app')
                list = []
                contentType = ContentType.objects.filter(app_label=App)
                for xModal in range(0, len(contentType)):
                    is_added = contentType[xModal].model in Modal
                    if is_added == False:
                        Modal.append(contentType[xModal].model)
                        list.append({
                            'ModalName': contentType[xModal].model,
                        })
                message = {
                    'isError': False, 'Message': list
                }

            elif Type == 'GetCodes':
                try:
                    App = request.POST.get('app')
                    Modal = request.POST.get('modal')
                    list = []
                    contentType = ContentType.objects.get(
                        app_label=App, model=Modal)
                    perms = Permission.objects.filter(
                        content_type=contentType.id)
                    for xCode in range(0, len(perms)):
                        list.append({
                            'CodeName': perms[xCode].codename,
                            'ContentID': perms[xCode].content_type.id,
                            'PermID': perms[xCode].id,
                        })
                    message = {
                        'isError': False, 'Message': list
                    }
                except Exception as error:
                    username = request.user.username
                    name = request.user.first_name + ' ' + request.user.last_name
                    sendException(
                        request, username, name, error)
                    message = {
                        'isError': True,
                        'Message': 'On Error Occurs . Please try again or contact system administrator'
                    }
                    return JsonResponse(message, status=200)
            elif Type == 'GetReport':
                report = request.POST.get('report')
                app = request.POST.get('app')
                modal = request.POST.get('modal')
                code = request.POST.get('code')
                group = request.POST.get('group')

                try:
                    list = []

                    if report == 'Role':
                        perm = Permission.objects.get(codename=code)
                        users = models.Users.objects.filter(
                            Q(groups__permissions=perm) | Q(user_permissions=perm)).distinct()

                        for xUser in range(0, len(users)):
                            avatar = users[xUser].avatar
                            list.append({
                                'Username': users[xUser].username,
                                'Name': users[xUser].first_name + ' ' + users[xUser].last_name,
                                'Email': users[xUser].email,
                                'Avatar': str(avatar)
                            })
                        message = {
                            'isError': False, 'Message': list
                        }

                    elif report == 'Group':
                        perm = Group.objects.get(name=group)
                        users = perm.user_set.all()

                        for xUser in range(0, len(users)):
                            avatar = users[xUser].avatar
                            list.append({
                                'Username': users[xUser].username,
                                'Name': users[xUser].first_name + ' ' + users[xUser].last_name,
                                'Email': users[xUser].email,
                                'Avatar': str(avatar)
                            })
                        message = {
                            'isError': False, 'Message': list
                        }

                except Exception as error:
                    username = request.user.username
                    name = request.user.first_name + ' ' + request.user.last_name
                    sendException(
                        request, username, name, error)
                    message = {
                        'isError': True,
                        'Message': 'On Error Occurs . Please try again or contact system administrator'
                    }
                    return JsonResponse(message, status=200)

            elif Type == 'GetUserReport':
                try:
                    report = request.POST.get('report')
                    user = request.POST.get('user')
                    userInstance = models.Users.objects.get(id=int(user))

                    list = []
                    if report == 'Role':
                        user_perms = Permission.objects.filter(
                            Q(user=userInstance) | Q(group__user=userInstance))

                        for xPerm in range(0, len(user_perms)):
                            list.append({
                                'App': user_perms[xPerm].content_type.app_label,
                                'Model': user_perms[xPerm].content_type.model,
                                'Codename': user_perms[xPerm].codename
                            })

                        message = {
                            'isError': False,
                            'Message': list
                        }

                    elif report == 'Group':
                        groups = Group.objects.filter(user=userInstance)

                        for xGroup in range(0, len(groups)):
                            list.append({
                                'GroupID': groups[xGroup].id,
                                'GroupName': groups[xGroup].name,
                                'Permissions': groups[xGroup].permissions.all().count(),
                            })

                        message = {
                            'isError': False,
                            'Message': list
                        }

                except Exception as error:
                    username = request.user.username
                    name = request.user.first_name + ' ' + request.user.last_name
                    sendException(
                        request, username, name, error)
                    message = {
                        'isError': True,
                        'Message': 'On Error Occurs . Please try again or contact system administrator'
                    }
                    return JsonResponse(message, status=200)

            return JsonResponse(message, status=200)

        else:
            message = {
                'isError': True,
                'Message': '401-Unauthorized access.you do not have permission to access this page.'
            }
            return JsonResponse(message, status=200)


@login_required(login_url='Login')
def ManageGroup(request, id):
    if id == '0':
        if request.method == 'POST':
            if not request.user.is_client and request.user.has_perm('auth.add_group'):
                Name = request.POST.get('name')

                if Group.objects.filter(name=Name).exists():
                    return JsonResponse({'isError': True, 'Message': 'This Group already exists'})
                else:
                    g = Group(name=Name)
                    g.save()
                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Users-Permission Module"
                    action = "Added new Group with Name of:" + '_' + Name
                    sendTrials(request, username, names,
                               avatar, action, module)

                    return JsonResponse({'isError': False, 'Message': 'New group has been created'})
            else:
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)

        if request.method == 'GET':
            if not request.user.is_client and request.user.has_perm('auth.view_group'):
                groups = Group.objects.all()
                if len(groups) < 0:
                    return JsonResponse({'isError': True, 'Message': 'No Groups Available'}, status=200)
                else:
                    id = 0
                    message = []
                    for xGroup in range(0, len(groups)):
                        message.append({
                            'ID': groups[xGroup].id,
                            'Count': groups[xGroup].permissions.all().count(),
                            'Name': groups[xGroup].name,
                        })
                    return JsonResponse({'isError': False, 'Message': message}, status=200)
            else:
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)
    else:
        if request.method == 'GET':
            if not request.user.is_client and request.user.has_perm('auth.view_group'):
                try:
                    group = Group.objects.get(id=id)
                    perms = Permission.objects.filter(~Q(codename='admission_officer'), ~Q(codename='head_of_hrm'), ~Q(
                        codename='admin_finance_office'), ~Q(codename='academic_office'), ~Q(codename='examination_office'), ~Q(codename='finance_branch')).order_by('content_type')
                    id = 0
                    message = []
                    for xPerm in range(0, len(perms)):
                        isGiven = True if len(group.permissions.filter(
                            id=perms[xPerm].id)) > 0 else False
                        if id != perms[xPerm].content_type.id:
                            id = perms[xPerm].content_type.id

                            message.append({
                                'App': perms[xPerm].content_type.app_label,
                                'Model': perms[xPerm].content_type.model,
                                'Actions': [
                                    {
                                        'Action': perms[xPerm].codename,
                                        'ID': perms[xPerm].id,
                                        'isGiven': isGiven
                                    }
                                ]

                            })
                        else:
                            message[len(message) - 1]['Actions'].append({
                                'Action': perms[xPerm].codename,
                                'ID': perms[xPerm].id,
                                'isGiven': isGiven
                            })

                    isError = False

                except Exception as error:
                    username = request.user.username
                    name = request.user.first_name + ' ' + request.user.last_name
                    sendException(
                        request, username, name, error)
                    message = {
                        'isError': True,
                        'Message': 'On Error Occurs . Please try again or contact system administrator'
                    }
                    return JsonResponse(message, status=200)
                return JsonResponse({'isError': isError, 'Message': message}, status=200)
            else:
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)

        if request.method == 'POST':
            if not request.user.is_client and request.user.has_perm('Users.manage_role_groups'):
                GroupID = int(id)
                PermID = int(request.POST.get('permID'))
                Type = request.POST.get('type')
                try:
                    # Get Group
                    group = Group.objects.get(id=GroupID)
                    # User = models.Users.objects.get(id=GroupID)
                    permission = Permission.objects.get(id=PermID)
                    # Add To The Group
                    if Type == 'Add':
                        perms = group.permissions.add(permission)
                    else:
                        perms = group.permissions.remove(permission)
                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Users-Permission Module"
                    if Type == 'Remove':
                        action = permission.codename + " removed from the group of " + group.name
                    else:
                        action = permission.codename + " Added to the group of " + group.name
                    sendTrials(request, username, names,
                               avatar, action, module)

                    message = 'Permission removed from the group' if Type == 'Remove' else 'Permission added to the group'
                    isError = False

                except Exception as error:
                    username = request.user.username
                    name = request.user.first_name + ' ' + request.user.last_name
                    sendException(
                        request, username, name, error)
                    message = {
                        'isError': True,
                        'Message': 'On Error Occurs . Please try again or contact system administrator'
                    }
                    return JsonResponse(message, status=200)
                return JsonResponse({'isError': isError, 'Message': message}, status=200)
            else:
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)

        if request.method == 'DELETE':
            if not request.user.is_client and request.user.has_perm('auth.delete_group'):
                try:
                    GroupID = int(id)
                    group = Group.objects.get(id=GroupID)
                    group.delete()
                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Users-Permission Module"
                    action = "Deleted Group with Name of:" + '_' + group.name
                    sendTrials(request, username, names,
                               avatar, action, module)

                    return JsonResponse({'isError': False, 'Message': "Group has been deleted successfully"}, status=200)
                except RestrictedError:
                    return JsonResponse({'isError': True, 'Message': 'Cannot delete some instances of model because they are referenced through restricted foreign keys'}, status=200)
            else:
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)

        if request.method == 'PATCH':
            if not request.user.is_client and request.user.has_perm('auth.view_group'):
                GroupID = int(id)
                group = Group.objects.get(id=GroupID)
                message = {
                    'id': group.id,
                    'Name': group.name,
                }
                return JsonResponse({'isError': False, 'Message': message}, status=200)
            else:
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)


@login_required(login_url='Login')
def RenameGroup(request):
    if request.method == 'POST':
        if not request.user.is_client and request.user.has_perm('auth.change_group'):
            Name = request.POST.get('name')
            ID = request.POST.get('ID')

            try:
                G = Group.objects.get(id=ID)
                if Group.objects.filter(name=Name).exists() and Name != G.name:
                    return JsonResponse({'isError': True, 'Message': 'This Group already exists'})
                else:
                    G.name = Name
                    G.save()
                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Users-Permission Module"
                    action = "Updated Group with Name of:" + '_' + Name
                    sendTrials(request, username, names,
                               avatar, action, module)

                    return JsonResponse({'isError': False, 'Message': 'Group has been renamed'})
            except Exception as error:
                username = request.user.username
                name = request.user.first_name + ' ' + request.user.last_name
                sendException(
                    request, username, name, error)
                message = {
                    'isError': True,
                    'Message': 'On Error Occurs . Please try again or contact system administrator'
                }
                return JsonResponse(message, status=200)
        else:

            message = {
                'isError': True,
                'Message': '401-Unauthorized access.you do not have permission to access this page.'
            }
            return JsonResponse(message, status=200)


@login_required(login_url='Login')
def SearchEngine(request, search, type):
    if request.user.is_client:
        return render(request, 'Auth/404.html')

    # type = yes if student else no => staff and admins
    if ',' in type:
        type = type.split(',')
    else:
        type = [type]

    CheckAdmin = False if 'AD' not in type else True
    CheckAgent = False if 'AG' not in type else True
    CheckClient = False if 'CL' not in type else True
    # CheckEmployee = False if type != 'EMM' else True # If Employee Existed Or Diactivated! The Student's Results Of Marks And Attendance Should Be Seen

    searchFields = {}

    if CheckAdmin:
        searchFields['is_admin'] = True
        searchFields['is_superuser'] = True

    if CheckAgent:
        searchFields['is_agent'] = True

    if CheckClient:
        searchFields['is_client'] = True

    # search_filter = Q(**searchFields, _connector=Q.OR)

    if request.method == 'GET':
        searchQuery = models.Users.objects.filter(Q(**searchFields, _connector=Q.OR), Q(username__icontains=search) | Q(email__icontains=search) | Q(
            first_name__icontains=search) | Q(last_name__icontains=search), is_delete=False)

        message = []
        userType = ''
        for xSearch in range(0, len(searchQuery)):
            if searchQuery[xSearch].is_superuser:
                userType = 'Superuser'
            elif searchQuery[xSearch].is_admin:
                userType = 'Admin'
            elif searchQuery[xSearch].is_client:
                userType = 'Client'
            elif searchQuery[xSearch].is_agent:
                userType = 'Agent'

            if searchQuery[xSearch].is_active == True:
                message.append({
                    'ID': searchQuery[xSearch].id,
                    'Username': searchQuery[xSearch].username,
                    'Name': searchQuery[xSearch].first_name + ' ' + searchQuery[xSearch].last_name,
                    'Email': searchQuery[xSearch].email,
                    'Phone': searchQuery[xSearch].phone,
                    'Type': userType
                })
        return JsonResponse({'Message': message}, status=200)
