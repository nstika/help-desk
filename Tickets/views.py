from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from Users.views import PreviewDate, sendException, sendTrials
from django.db.models.deletion import RestrictedError
from django.core.paginator import Paginator
from django.db.models import Q
from . import models
from Users import models as user_models
from Projects import models as project_models
from django.core.exceptions import *

# Create your views here.


@login_required(login_url='Login')
def ViewTicketDetails(request, ids):
    if request.user.has_perm('Tickets.view_tickets') or request.user.is_agent or request.user.is_client:

        try:
            getticketdetails = models.Tickets.objects.get(
                id=ids)
            # Checking if another user (agent) accepted the task
            check_if_user_accepted = models.AssignTicket.objects.filter(
                ticketID=ids, is_accepted=True, is_removed=False, is_assigned=True)
            if len(check_if_user_accepted) > 0 and request.user.is_agent:
                check_if_user_accepted = check_if_user_accepted[0]

                if check_if_user_accepted.userID != request.user:
                    context = {
                        'isError': True,
                        'error': f"This ticket ( {getticketdetails.ticket_number} - {getticketdetails.title}) has been accepted by another user...",
                    }
                    return render(request, 'Layout/Admin/Tickets/view_tickers.html', context)

            # ids = getticketdetails.id
            if request.user.has_perm('Tickets.view_tickets') or request.user.is_client:
                getassignedTicket = models.AssignTicket.objects.filter(
                    ticketID=ids, is_removed=False)
            else:
                getassignedTicket = models.AssignTicket.objects.filter(
                    ticketID=ids, userID=request.user.id, is_removed=False)

            if request.user.is_agent and models.AssignTicket.objects.filter(userID=request.user.id,
                                                                            ticketID=ids, is_removed=False).exists() == False and not request.user.has_perm('Tickets.view_tickets'):
                return render(request, 'Auth/404.html')
            # check if client ticket ID is correct
            if request.user.is_client and models.Tickets.objects.filter(userID=request.user.id,
                                                                        id=ids, is_delete=False).exists() == False:
                return render(request, 'Auth/404.html')
            is_accepted = True
            if request.user.is_agent:
                is_accepted = models.AssignTicket.objects.filter(userID=request.user.id,
                                                                 ticketID=ids, is_accepted=True, is_removed=False).exists()

            is_assigned = models.AssignTicket.objects.filter(
                ticketID=ids, userID=request.user.id, is_removed=False).exists()

            # Get Ticket Replies
            replies = models.ReplyTicket.objects.filter(
                ticketID=getticketdetails.id)
            context = {
                'isError': False,
                'ticket': getticketdetails,
                'assigned': getassignedTicket,
                'replies': replies,
                'is_accepted': is_accepted,
                'is_assigned': is_assigned,
            }
            return render(request, 'Layout/Admin/Tickets/view_tickers.html', context)
        except ObjectDoesNotExist as error:

            username = request.user.username
            name = request.user.first_name + ' ' + request.user.last_name
            message = ""
            message = sendException(
                request, username, name, error)
            return render(request, 'Auth/404.html')
        except ValidationError as error:

            username = request.user.username
            name = request.user.first_name + ' ' + request.user.last_name
            message = ""
            message = sendException(
                request, username, name, error)
            return render(request, 'Auth/404.html')
        except Exception as error:
            username = request.user.username
            name = request.user.first_name + ' ' + request.user.last_name
            message = ""
            message = sendException(
                request, username, name, error)

        return render(request, 'Layout/Admin/Tickets/view_tickers.html', {'Message': message})
    else:
        return render(request, 'Auth/404.html')


@login_required(login_url='Login')
def TicketRreport(request, id):
    if request.user.has_perm('Tickets.view_tickets') and not request.user.is_client:

        try:
            user = models.Users.objects.get(id=id)
            accepted_removed = models.AssignTicket.objects.filter(
                userID=id, is_removed=True, is_accepted=True)
            others = models.AssignTicket.objects.filter(Q(is_accepted=True) | Q(is_accepted=False),
                                                        userID=id, is_removed=False).order_by('-is_accepted')
            unaccepted = models.AssignTicket.objects.filter(
                userID=id, is_accepted=False)
            context = {
                'Accepted_Removed': accepted_removed,
                'Others': others,
                'User': user
            }

            return render(request, 'Layout/Admin/Tickets/ticketreport.html', context)
        except Exception as error:
            username = request.user.username
            name = request.user.first_name + ' ' + request.user.last_name
            message = sendException(
                request, username, name, error)
            return render(request,  'Auth/404.html')
    else:
        message = {
            'isError': True,
            'Message': '401-Unauthorized access.you do not have permission to access this page.'
        }
        return JsonResponse(message, status=200)


@login_required(login_url='Login')
def TicketCategory(request):
    if request.user.has_perm('Tickets.view_category') and not request.user.is_client:
        CheckSearchQuery = 'SearchQuery' in request.GET
        CheckDataNumber = 'DataNumber' in request.GET
        DataNumber = 10
        SearchQuery = ''
        CategoryList = []

        if CheckDataNumber:
            DataNumber = int(request.GET['DataNumber'])

        if CheckSearchQuery:
            SearchQuery = request.GET['SearchQuery']
            CategoryList = models.Category.objects.filter(
                Q(name__icontains=SearchQuery) | Q(created_at__icontains=SearchQuery) | Q(modified_at__icontains=SearchQuery), is_delete=False, type='Ticket')
        else:
            CategoryList = models.Category.objects.filter(
                is_delete=False, type='Ticket')

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
        return render(request, 'Layout/Admin/Categories/ticket_category.html', context)
    else:
        return render(request,  'Auth/404.html')


@login_required(login_url='Login')
def TaskCategory(request):
    if request.user.has_perm('Tickets.view_category') and not request.user.is_client:
        CheckSearchQuery = 'SearchQuery' in request.GET
        CheckDataNumber = 'DataNumber' in request.GET
        DataNumber = 10
        SearchQuery = ''
        CategoryList = []

        if CheckDataNumber:
            DataNumber = int(request.GET['DataNumber'])

        if CheckSearchQuery:
            SearchQuery = request.GET['SearchQuery']
            CategoryList = models.Category.objects.filter(
                Q(name__icontains=SearchQuery) | Q(created_at__icontains=SearchQuery) | Q(modified_at__icontains=SearchQuery), is_delete=False, type='Task')
        else:
            CategoryList = models.Category.objects.filter(
                is_delete=False, type='Task')

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
        return render(request, 'Layout/Admin/Categories/task_category.html', context)
    else:
        return render(request,  'Auth/404.html')


@login_required(login_url='Login')
def ProjectCategory(request):
    if request.user.has_perm('Tickets.view_category') and not request.user.is_client:
        CheckSearchQuery = 'SearchQuery' in request.GET
        CheckDataNumber = 'DataNumber' in request.GET
        DataNumber = 10
        SearchQuery = ''
        CategoryList = []

        if CheckDataNumber:
            DataNumber = int(request.GET['DataNumber'])

        if CheckSearchQuery:
            SearchQuery = request.GET['SearchQuery']
            CategoryList = models.Category.objects.filter(
                Q(name__icontains=SearchQuery) | Q(created_at__icontains=SearchQuery) | Q(modified_at__icontains=SearchQuery), is_delete=False, type='Project')
        else:
            CategoryList = models.Category.objects.filter(
                is_delete=False, type='Project')

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
        return render(request, 'Layout/Admin/Categories/project_category.html', context)
    else:
        return render(request,  'Auth/404.html')


@login_required(login_url='Login')
def AddTickets(request):
    if request.user.has_perm('Tickets.add_tickets') and not request.user.is_client:
        return render(request, 'Layout/Admin/Tickets/add_tickets.html')
    else:
        return render(request,  'Auth/404.html')


@login_required(login_url='Login')
def CreateClientTicket(request):
    if request.user.is_client:
        return render(request, 'Layout/Customer/client_ticket.html')
    else:
        return render(request,  'Auth/404.html')


@login_required(login_url='Login')
def ViewTicketsPage(request):
    if request.user.has_perm('Tickets.view_tickets') and not request.user.is_client:
        CheckSearchQuery = 'SearchQuery' in request.GET
        CheckDataNumber = 'DataNumber' in request.GET
        CheckFilterStatus = 'FilterStatus' in request.GET
        FilterStatus = {}
        status = "All"
        DataNumber = 10
        SearchQuery = ''
        TicketsList = []

        if CheckFilterStatus:
            status = request.GET['FilterStatus']

            if status != "All":
                FilterStatus['status'] = status

        if CheckDataNumber:
            DataNumber = int(request.GET['DataNumber'])

        if CheckSearchQuery:
            SearchQuery = request.GET['SearchQuery']
            TicketsList = models.Tickets.objects.filter(Q(ticket_number__icontains=SearchQuery)
                                                        | Q(title__icontains=SearchQuery) | Q(
                description__icontains=SearchQuery) | Q(status__icontains=SearchQuery)
                | Q(priority__icontains=SearchQuery) | Q(category__name__icontains=SearchQuery)
                | Q(userID__first_name__icontains=SearchQuery) | Q(userID__last_name__icontains=SearchQuery), **FilterStatus, is_delete=False)
        else:
            TicketsList = models.Tickets.objects.filter(
                **FilterStatus, is_delete=False).order_by('-created_at')

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
            'Status': status
        }
        return render(request, 'Layout/Admin/Tickets/tickets.html', context)
    else:
        return render(request,  'Auth/404.html')


@login_required(login_url='Login')
def Computers(request):
    if request.user.has_perm('Tickets.view_computerlease') and not request.user.is_client:
        CheckSearchQuery = 'SearchQuery' in request.GET
        CheckDataNumber = 'DataNumber' in request.GET
        status = "All"
        DataNumber = 10
        SearchQuery = ''
        TicketsList = []

        if CheckDataNumber:
            DataNumber = int(request.GET['DataNumber'])

        if CheckSearchQuery:
            SearchQuery = request.GET['SearchQuery']
            TicketsList = models.ComputerLease.objects.filter(Q(computer_tag__icontains=SearchQuery)
                                                        | Q(full_name__icontains=SearchQuery) | Q(
                username__icontains=SearchQuery) | Q(office_key__icontains=SearchQuery)
                | Q(office_type__icontains=SearchQuery) | Q(windows_key__icontains=SearchQuery)
                | Q(windows_type__icontains=SearchQuery) | Q(location__icontains=SearchQuery) | Q(bitlocker_recovery_keys__icontains=SearchQuery)|  Q(department__dept_name__icontains=SearchQuery), is_delete=False)
        else:
            TicketsList = models.ComputerLease.objects.filter(
                is_delete=False).order_by('-created_at')

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
            'Status': status,
            'Departments': user_models.Department.objects.all(),
        }
        return render(request, 'Layout/Admin/Tickets/computers.html', context)
    else:
        return render(request,  'Auth/404.html')


@login_required(login_url='Login')
def ManageComputer(request, action):
    # Catching excpetions
    try:

        # Add new computer information
        if action == 'AddComputer':
            if request.method == 'POST':
                if request.user.has_perm('Tickets.add_computerlease'):
                    computer_tag = request.POST.get('computer_tag')
                    full_name = request.POST.get('full_name')
                    username = request.POST.get('username')
                    office_key = request.POST.get('office_key')
                    office_type = request.POST.get('office_type')
                    windows_key = request.POST.get('windows_key')
                    windows_type = request.POST.get('windows_type')
                    location = request.POST.get('location')
                    department = request.POST.get('department')
                    bitlocker_recovery_keys = request.POST.get(
                        'bitlocker_recovery_keys')

                    if full_name == '' or full_name == None or full_name == 'null':
                        return JsonResponse({'isError': False, 'Message': 'Please enter a full name'})

                    # Later will be modified
                    if computer_tag == '' or computer_tag == None or computer_tag == 'null':
                        computer_tag = None
                        # return JsonResponse({'isError': True , 'Message': 'Please enter a computer tag'})

                    # Later will be modified
                    if office_key == '' or office_key == None or office_key == 'null':
                        office_key = None
                        # return JsonResponse({'isError': True , 'Message': 'Please enter office key'})

                    if office_type == '' or office_type == None or office_type == 'null':
                        return JsonResponse({'isError': True, 'Message': 'Please enter office type'})

                    # Later will be modified
                    if windows_key == '' or windows_key == None or windows_key == 'null':
                        windows_key = None
                        # return JsonResponse({'isError': True , 'Message': 'Please enter windows key'})

                    if windows_type == '' or windows_type == None or windows_type == 'null':
                        return JsonResponse({'isError': True, 'Message': 'Please enter windows type'})

                    if location == '' or location == None or location == 'null':
                        return JsonResponse({'isError': True, 'Message': 'Please enter location'})

                    if department == '' or department == None or department == 'null':
                        return JsonResponse({'isError': True, 'Message': 'Please select department'})

                    if bitlocker_recovery_keys == '' or bitlocker_recovery_keys == None or bitlocker_recovery_keys == 'null':
                        bitlocker_recovery_keys = None
                        # return JsonResponse({'isError': True , 'Message': 'Please enter bitlocker recovery keys'})

                    if username == '' or username == None or username == 'null':
                        username = None

                    # Get instances from the database
                    department = user_models.Department.objects.get(
                        id=department)

                    # save the computer's details in the database
                    save_computer = models.ComputerLease(
                        computer_tag=computer_tag,
                        full_name=full_name,
                        username=username,
                        office_key=office_key,
                        office_type=office_type,
                        windows_key=windows_key,
                        windows_type=windows_type,
                        location=location,
                        department=department,
                        bitlocker_recovery_keys=bitlocker_recovery_keys,
                    )

                    save_computer.save()

                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    action = f"{names} has added new computer"
                    module = "Ticket Module / Tickets"
                    sendTrials(request, username, names,
                               avatar, action, module)
                    return JsonResponse({'isError': False, 'Message': "New computer has been added"})

                else:
                    message = {
                        'isError': True,
                        'Message': '404-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

        # Update existing computer information
        if action == 'EditComputer':
            if request.method == 'POST':
                if request.user.has_perm('Tickets.change_computerlease'):
                    computer_tag = request.POST.get('computer_tag')
                    full_name = request.POST.get('full_name')
                    username = request.POST.get('username')
                    office_key = request.POST.get('office_key')
                    office_type = request.POST.get('office_type')
                    windows_key = request.POST.get('windows_key')
                    windows_type = request.POST.get('windows_type')
                    location = request.POST.get('location')
                    computer_id = request.POST.get('computer_id')
                    department = request.POST.get('department')
                    bitlocker_recovery_keys = request.POST.get(
                        'bitlocker_recovery_keys')

                    if full_name == '' or full_name == None or full_name == 'null':
                        return JsonResponse({'isError': False, 'Message': 'Please enter a full name'})

                    # Later will be modified
                    if computer_tag == '' or computer_tag == None or computer_tag == 'null':
                        computer_tag = None
                        # return JsonResponse({'isError': True , 'Message': 'Please enter a computer tag'})

                    # Later will be modified
                    if office_key == '' or office_key == None or office_key == 'null':
                        office_key = None
                        # return JsonResponse({'isError': True , 'Message': 'Please enter office key'})

                    if office_type == '' or office_type == None or office_type == 'null':
                        return JsonResponse({'isError': True, 'Message': 'Please enter office type'})

                    # Later will be modified
                    if windows_key == '' or windows_key == None or windows_key == 'null':
                        windows_key = None
                        # return JsonResponse({'isError': True , 'Message': 'Please enter windows key'})

                    if windows_type == '' or windows_type == None or windows_type == 'null':
                        return JsonResponse({'isError': True, 'Message': 'Please enter windows type'})

                    if location == '' or location == None or location == 'null':
                        return JsonResponse({'isError': True, 'Message': 'Please enter location'})

                    if department == '' or department == None or department == 'null':
                        return JsonResponse({'isError': True, 'Message': 'Please select department'})

                    if bitlocker_recovery_keys == '' or bitlocker_recovery_keys == None or bitlocker_recovery_keys == 'null':
                        bitlocker_recovery_keys = None
                        # return JsonResponse({'isError': True , 'Message': 'Please enter bitlocker recovery keys'})

                    if username == '' or username == None or username == 'null':
                        username = None

                    # Get instances from the database
                    department = user_models.Department.objects.get(
                        id=department)
                    save_computer = models.ComputerLease.objects.get(
                        id=computer_id)

                    # save the computer's details in the database
                    save_computer.computer_tag = computer_tag
                    save_computer.full_name = full_name
                    save_computer.username = username
                    save_computer.office_type = office_type
                    save_computer.office_key = office_key
                    save_computer.windows_key = windows_key
                    save_computer.windows_type = windows_type
                    save_computer.location = location
                    save_computer.department = department
                    save_computer.bitlocker_recovery_keys = bitlocker_recovery_keys
                    save_computer.save()

                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    action = f"{names} has added new computer"
                    module = "Ticket Module / Tickets"
                    sendTrials(request, username, names,
                               avatar, action, module)
                    return JsonResponse({'isError': False, 'Message': "Computer has been updated successfully"})

                else:
                    message = {
                        'isError': True,
                        'Message': '404-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

        # Get computer's information
        if action == 'GetComputer':
            if request.method == 'POST':
                if request.user.has_perm('Tickets.view_computerlease'):
                    compuetr_id = request.POST.get('computer_id')

                    computer = models.ComputerLease.objects.get(id=compuetr_id)

                    return JsonResponse({
                        'isError': False,
                        'Message': {
                            'id': computer.id,
                            'computer_tag': computer.computer_tag,
                            'full_name': computer.full_name,
                            'username': computer.username,
                            'office_key': computer.office_key,
                            'office_type': computer.office_type,
                            'windows_key': computer.windows_key,
                            'windows_type': computer.windows_type,
                            'location': computer.location,
                            'department': computer.department.id,
                            'bitlocker_recovery_keys': computer.bitlocker_recovery_keys
                        }
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


@login_required(login_url='Login')
def ManageTickets(request, id):
    Type = request.POST.get('Type')
    if id == '0':

        # Post New Ticket
        if request.method == 'POST':

            try:
                title = request.POST.get('title')
                description = request.POST.get('descrption')
                priority = request.POST.get('priority')
                userid = request.POST.get('userid')
                category = request.POST.get('category')
                try:
                    ticket_image = request.FILES['ticket_image']
                except KeyError:
                    ticket_image = None

                ticketnumber = generateTicketNumber()
                Categories = models.Category.objects.get(
                    id=category, is_delete=False)
                if ticket_image is not None:
                    extention = ticket_image.name.split(".")[-1]
                extension_types = ['JPEG', 'jpeg', 'JPG', 'jpg', 'png', "PNG"]
                if ticket_image is not None and not extention in extension_types:
                    return JsonResponse({'isError': True, 'Message': 'This Feild Only supports jpeg,jpg,png extensions.'})
                if ticket_image is not None and ticket_image.size > 2621440:
                    return JsonResponse({'isError': True, 'Message': ticket_image.name + '  file is more than 2MB size'})

                if Type == 'AddTicket' and request.user.has_perm('Tickets.add_tickets') and not request.user.is_client:

                    Users = user_models.Users.objects.get(
                        id=userid, is_delete=False)

                    create_ticket = models.Tickets(ticket_number=ticketnumber, title=title, description=description,
                                                   status='On-Hold', priority=priority, image_file=ticket_image, category=Categories, userID=Users)
                    create_ticket.save()
                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Ticket Module  / Ticket"
                    action = "Created new Ticket with the ticket No " + \
                        str(ticketnumber)
                    sendTrials(request, username, names,
                               avatar, action, module)
                    message = {
                        'isError': False,
                        'Message': 'New Ticket has been successfully created'
                    }
                    return JsonResponse(message, status=200)

                elif Type == 'ClientTicket' and request.user.is_client:
                    Users = user_models.Users.objects.get(
                        id=request.user.id, is_delete=False)
                    create_ticket = models.Tickets(ticket_number=ticketnumber, title=title, description=description,
                                                   status='On-Hold', image_file=ticket_image, category=Categories, userID=Users)
                    create_ticket.save()
                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Ticket Module  / Ticket"
                    action = "Created new Ticket with the ticket No " + \
                        str(ticketnumber)
                    sendTrials(request, username, names,
                               avatar, action, module)
                    message = {
                        'isError': False,
                        'Message': 'New Ticket has been successfully created'
                    }
                    return JsonResponse(message, status=200)

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

    else:
        # Get Single ticket And Check if the user has the permisison
        if request.method == 'GET':
            if request.user.has_perm('Tickets.change_tickets') and not request.user.is_client:
                try:
                    Tickets = models.Tickets.objects.get(
                        id=id, is_delete=False)

                    message = {
                        'id': Tickets.id,
                        'title': Tickets.title,
                        'description': Tickets.description,
                        'priority': Tickets.priority,
                        'category': Tickets.category.id,
                        'client': {
                            'id': Tickets.userID.id,
                            'username': Tickets.userID.username,
                            'name': Tickets.userID.first_name + ' ' + Tickets.userID.last_name,
                        },

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

        # Update ticket And Check if the user has the permisison
        if request.method == 'POST':
            if Type == "change" and request.user.has_perm('Tickets.change_tickets') and not request.user.is_client:

                title = request.POST.get('title')
                description = request.POST.get('description')
                priority = request.POST.get('priority')
                userid = request.POST.get('userid')
                category = request.POST.get('category')
                Categories = models.Category.objects.get(
                    id=category, is_delete=False)
                Users = user_models.Users.objects.get(
                    id=userid, is_delete=False)
                try:
                    ticketsList = models.Tickets.objects.get(
                        id=id, is_delete=False)

                    ticketsList.title = title
                    ticketsList.description = description
                    ticketsList.priority = priority
                    ticketsList.userID = Users
                    ticketsList.category = Categories
                    ticketsList.save()
                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    action = "Updated Ticket with ticket Number of" + \
                        str(ticketsList.ticket_number)
                    module = "Ticket Module / Tickets"
                    sendTrials(request, username, names,
                               avatar, action, module)
                    return JsonResponse({'isError': False, 'Message': 'Ticket has been successfully updated'}, status=200)

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

            elif Type == "Changestatus" and request.user.has_perm('Tickets.change_status_ticket') and not request.user.is_client:
                status = request.POST.get('status')

                try:
                    ticketsList = models.Tickets.objects.get(
                        id=id, is_delete=False)

                    CheckAssign = models.AssignTicket.objects.filter(
                        ticketID=ticketsList.id).exists()
                    if CheckAssign == False:
                        return JsonResponse({'isError': True, 'Message': 'Sorry!! This ticket can not be assigned any agent'}, status=200)
                    else:
                        statuss = ticketsList.status

                        ticketsList.status = status
                        ticketsList.save()
                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        action = "Updated Ticket status of " + statuss + " to  " + \
                            status+" with ticket number of  " + ticketsList.ticket_number
                        module = "Ticket Module / Tickets"
                        sendTrials(request, username, names,
                                   avatar, action, module)
                        return JsonResponse({'isError': False, 'Message': 'Ticket status has been successfully updated'}, status=200)

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

            elif Type == "ClientReopen" and request.user.is_client:
                status = "Re-Open"

                try:
                    ticketsList = models.Tickets.objects.get(
                        id=id, is_delete=False)
                    statuss = ticketsList.status

                    ticketsList.status = status
                    ticketsList.save()
                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    action = "Updated Ticket status of " + statuss + " to  " + \
                        status+" with ticket number of  " + ticketsList.ticket_number
                    module = "Ticket Module / Tickets"
                    sendTrials(request, username, names,
                               avatar, action, module)
                    return JsonResponse({'isError': False, 'Message': 'Ticket status has been successfully updated'}, status=200)

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

            elif Type == "Changepriority" and request.user.has_perm('Tickets.change_priority_ticket') and not request.user.is_client:
                priority = request.POST.get('priority')

                try:
                    ticketsList = models.Tickets.objects.get(
                        id=id, is_delete=False)
                    prioritys = ticketsList.priority

                    ticketsList.priority = priority
                    ticketsList.save()
                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    action = "Updated Ticket priority of " + prioritys + " to  " + \
                        priority+" with ticket number of  " + ticketsList.ticket_number
                    module = "Ticket Module / Tickets"
                    sendTrials(request, username, names,
                               avatar, action, module)
                    return JsonResponse({'isError': False, 'Message': 'Ticket priority has been successfully updated'}, status=200)

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

            elif Type == "Accept" and request.user.is_agent:

                try:
                    ticketsList = models.AssignTicket.objects.filter(
                        ticketID=id, is_removed=False).order_by('-is_accepted')
                    iscepts = ticketsList[0]

                    if iscepts.is_accepted == True:
                        return JsonResponse({'isError': True, 'Message': 'This Ticket already accept by '+iscepts.userID.first_name + ' '+iscepts.userID.last_name}, status=200)

                    else:
                        IDs = request.user.id
                        AcceptTicket = models.AssignTicket.objects.get(
                            ticketID=id, userID=IDs)
                        Changestatus = models.Tickets.objects.get(
                            id=id, is_delete=False)
                        Changestatus.status = "Inprogress"
                        AcceptTicket.is_accepted = True
                        AcceptTicket.save()
                        Changestatus.save()
                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        action = names + " has been accepted ticket number of " + \
                            AcceptTicket.ticketID.ticket_number
                        module = "Ticket Module / Tickets"
                        sendTrials(request, username, names,
                                   avatar, action, module)
                        return JsonResponse({'isError': False, 'Message': names + " has been accepted ticket number of " + AcceptTicket.ticketID.ticket_number}, status=200)

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

        # Delete ticket And Check if the user has the permisison
        if request.method == 'DELETE':
            if request.user.has_perm('Tickets.delete_tickets') and not request.user.is_client:
                try:

                    ticket = models.Tickets.objects.get(id=id, is_delete=False)
                    checkAssigned = models.AssignTicket.objects.filter(
                        ticketID=ticket.id, is_removed=False).exists()
                    checkReplies = models.ReplyTicket.objects.filter(
                        ticketID=ticket.id).exists()
                    if checkAssigned or checkReplies:
                        return JsonResponse({'isError': True, 'Message': 'Cannot delete some instances of model because they are referenced through restricted foreign keys'}, status=200)
                    else:
                        pname = ticket.ticket_number
                        ticket.is_delete = True
                        ticket.save()
                        username = request.user.username
                        name = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Ticket Module  / Ticket"
                        action = "Deleted Ticket with the Ticket Number of " + pname
                        sendTrials(request, username, name,
                                   avatar, action, module)
                        message = {
                            'isError': False,
                            'Message': pname+' has been successfully deleted!!'
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
            else:
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)


@login_required(login_url='Login')
def ManageCategory(request, id):
    if id == 0:

        # Post New category
        if request.method == 'POST':
            if request.user.has_perm('Tickets.add_category') and not request.user.is_client:
                name = request.POST.get('name')
                type = request.POST.get('type')
                try:

                    if not type in ['Ticket', 'Project', 'Task']:
                        return JsonResponse({'isError': True, 'Message': 'Unknown Ticket Type'})

                    if models.Category.objects.filter(name=name, type=type).exists():
                        return JsonResponse({'isError': True, 'Message': name+' already exists'})

                    Category = models.Category(name=name, type=type)
                    Category.save()
                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Ticket Module  / Category"
                    action = "Created new Category name of " + name
                    sendTrials(request, username, names,
                               avatar, action, module)
                    message = {
                        'isError': False,
                        'Message': 'New Category has been successfully created'
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
            else:
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)

    else:
        # Get Single Category And Check if the user has the permisison
        if request.method == 'GET':
            if request.user.has_perm('Tickets.view_category') and not request.user.is_client:
                try:
                    Category = models.Category.objects.get(
                        id=id, is_delete=False)

                    message = {
                        'id': Category.id,
                        'name': Category.name,
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

        # Delete Category And Check if the user has the permisison
        if request.method == 'DELETE':
            if request.user.has_perm('Tickets.delete_category') and not request.user.is_client:
                try:

                    category = models.Category.objects.get(
                        id=id, is_delete=False)
                    chechTicket = models.Tickets.objects.filter(
                        category=category.id).exists()
                    chechTask = project_models.Task.objects.filter(
                        category=category.id).exists()
                    chechProject = project_models.Project.objects.filter(
                        category=category.id).exists()

                    if chechTicket or chechTask or chechProject:
                        return JsonResponse({'isError': True, 'Message': 'Cannot delete some instances of model because they are referenced through restricted foreign keys'}, status=200)
                    else:
                        pname = category.name
                        category.is_delete = True
                        category.save()
                        username = request.user.username
                        name = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Ticket Module  / Category"
                        action = "Deleted Category name of " + pname
                        sendTrials(request, username, name,
                                   avatar, action, module)
                        message = {
                            'isError': False,
                            'Message': pname+' has been successfully deleted!!'
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
            else:
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)

        # Update Category And Check if the user has the permisison
        if request.method == 'POST':
            if request.user.has_perm('Tickets.change_category') and not request.user.is_client:
                name = request.POST.get('name')
                type = request.POST.get('type')

                try:
                    if not type in ['Ticket', 'Project', 'Task']:
                        return JsonResponse({'isError': True, 'Message': 'Unknown Ticket Type'})
                    Category = models.Category.objects.get(id=id)
                    if models.Category.objects.filter(name=name, type=type).exists() and name.casefold() != Category.name.casefold():
                        return JsonResponse({'isError': True, 'Message': 'Category already exists'})
                    else:
                        if name == Category.name:
                            action = "Edited Category name of " + name
                        else:
                            action = "Edited Category name of " + Category.name + ' to ' + name
                        Category.name = name
                        Category.type = type
                        Category.save()
                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Ticket Module  / Category"
                        sendTrials(request, username, names,
                                   avatar, action, module)
                        return JsonResponse({'isError': False, 'Message': 'Category has been successfully updated'}, status=200)

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
def ManageAssignTicket(request, ids):
    if ids == 0:
        # Post Assign Ticket
        if request.method == 'POST':
            if request.user.has_perm('Tickets.add_assignticket') and not request.user.is_client:
                userID = request.POST.get('user')
                TicketID = request.POST.get('ticket')
                try:
                    UserIDss = user_models.Users.objects.get(
                        id=userID, is_delete=False)
                    if models.AssignTicket.objects.filter(userID=userID, ticketID=TicketID, is_removed=False, is_accepted=False).exists():
                        return JsonResponse({'isError': True, 'Message': ' This ticket already assigned ' + UserIDss.first_name + " "+UserIDss.last_name})
                    elif models.AssignTicket.objects.filter(userID=userID, ticketID=TicketID, is_removed=False, is_accepted=True).exists():
                        return JsonResponse({'isError': True, 'Message': ' This ticket already assigned ' + UserIDss.first_name + " "+UserIDss.last_name})
                    elif models.AssignTicket.objects.filter(userID=userID, ticketID=TicketID, is_removed=True, is_accepted=True).exists():
                        UpdateRemove = models.AssignTicket.objects.get(
                            userID=userID, ticketID=TicketID, is_removed=True, is_accepted=True)
                        UpdateRemove.is_removed = False
                        UpdateRemove.is_accepted = False
                        UpdateRemove.is_assigned = True
                        UpdateRemove.assigned_by = request.user
                        UpdateRemove.save()
                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Ticket Module / Assign Tickets"
                        action = UpdateRemove.userID.first_name + ' ' + UpdateRemove.userID.last_name + \
                            " is assigned ticket name of " + UpdateRemove.ticketID.ticket_number
                        sendTrials(request, username, names,
                                   avatar, action, module)
                        message = {
                            'isError': False,
                            'Message': UpdateRemove.userID.first_name + ' ' + UpdateRemove.userID.last_name + " has been successfully assigned ticket name of " + UpdateRemove.ticketID.ticket_number
                        }
                        return JsonResponse(message, status=200)
                    elif models.AssignTicket.objects.filter(userID=userID, ticketID=TicketID, is_removed=True, is_accepted=False).exists():
                        UpdateRemove = models.AssignTicket.objects.get(
                            userID=userID, ticketID=TicketID, is_removed=True, is_accepted=False)
                        UpdateRemove.is_removed = False
                        UpdateRemove.is_accepted = False
                        UpdateRemove.is_assigned = True
                        UpdateRemove.assigned_by = request.user
                        UpdateRemove.save()
                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Ticket Module / Assign Tickets"
                        action = UpdateRemove.userID.first_name + ' ' + UpdateRemove.userID.last_name + \
                            " is assigned ticket name of " + UpdateRemove.ticketID.ticket_number
                        sendTrials(request, username, names,
                                   avatar, action, module)
                        message = {
                            'isError': False,
                            'Message': UpdateRemove.userID.first_name + ' ' + UpdateRemove.userID.last_name + " has been successfully assigned ticket name of " + UpdateRemove.ticketID.ticket_number
                        }
                        return JsonResponse(message, status=200)

                    else:

                        UserIDs = user_models.Users.objects.get(
                            id=userID, is_delete=False)
                        Tickets = models.Tickets.objects.get(
                            id=TicketID, is_delete=False)
                        Tickets.status = "Assigned"
                        AssignTicket = models.AssignTicket(
                            userID=UserIDs, ticketID=Tickets, assigned_by=request.user, is_assigned=True)
                        AssignTicket.save()
                        Tickets.save()
                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Ticket Module / Assign Tickets"
                        action = UserIDs.first_name + ' ' + UserIDs.last_name + \
                            " is assigned ticket name of " + Tickets.title
                        sendTrials(request, username, names,
                                   avatar, action, module)
                        message = {
                            'isError': False,
                            'Message': UserIDs.first_name + ' ' + UserIDs.last_name + " has been successfully assigned ticket name of " + Tickets.title
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
            else:
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)

    else:
        # Get Single Assign Tickets And Check if the user has the permisison
        if request.method == 'GET':
            if request.user.has_perm('Tickets.view_assignticket') and not request.user.is_client:
                try:
                    AssignTickets = models.AssignTicket.objects.get(id=ids)
                    message = {
                        'id': AssignTickets.id,
                        'userID': AssignTickets.userID.id,
                        'userName': AssignTickets.userID.first_name+" "+AssignTickets.userID.last_name,
                        'ticketID': AssignTickets.ticketID.id,
                        'ticketTittle': AssignTickets.ticketID.title,
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

        # Delete Assign Tickets And Check if the user has the permisison
        if request.method == 'DELETE':
            if request.user.has_perm('Tickets.delete_assignticket') and not request.user.is_client:
                try:

                    DeleteAssing = models.AssignTicket.objects.get(id=ids)
                    # checkStatus = models.AssignTicket.objects.filter(
                    #     ticketID=DeleteAssing)
                    DeleteAssing.is_removed = True
                    DeleteAssing.is_assigned = False

                    tname = DeleteAssing.ticketID.title
                    UserName = DeleteAssing.userID.first_name + \
                        ' ' + DeleteAssing.userID.last_name + ""
                    DeleteAssing.save()
                    CheckAssign = models.AssignTicket.objects.filter(
                        ticketID=DeleteAssing.ticketID, is_assigned=True, is_accepted=True).exists()
                    Checkstatus = models.AssignTicket.objects.filter(
                        ticketID=DeleteAssing.ticketID, is_assigned=True, is_accepted=False).exists()

                    if CheckAssign == True:
                        ChangeTicketStatus = models.Tickets.objects.get(
                            id=DeleteAssing.ticketID.id)
                        ChangeTicketStatus.status = "Inprogress"
                        ChangeTicketStatus.save()
                    if Checkstatus == True:
                        ChangeTicketStatus = models.Tickets.objects.get(
                            id=DeleteAssing.ticketID.id)
                        ChangeTicketStatus.status = "Assigned"
                        ChangeTicketStatus.save()
                    if CheckAssign == False and Checkstatus == False:
                        ChangeTicketStatus = models.Tickets.objects.get(
                            id=DeleteAssing.ticketID.id)
                        ChangeTicketStatus.status = "On-Hold"
                        ChangeTicketStatus.save()

                    username = request.user.username
                    name = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Ticket Module / Assign Tickets"
                    action = UserName + " is removed ticket name of " + tname

                    sendTrials(request, username, name,
                               avatar, action, module)
                    message = {
                        'isError': False,
                        'Message': UserName + " has been successfully removed ticket name of " + tname,
                    }
                    return JsonResponse(message, status=200)
                except RestrictedError:
                    return JsonResponse({'isError': True, 'Message': 'Cannot delete some instances of model because they are referenced through restricted foreign keys'}, status=200)
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

        # Update  Assign Tickets And Check if the user has the permisison
        if request.method == 'POST':
            if request.user.has_perm('Tickets.change_assignticket') and not request.user.is_client:
                userID = request.POST.get('user')
                TicketID = request.POST.get('ticket')

                try:

                    if models.AssignTicket.objects.filter(userID=userID, ticketID=TicketID).exists():
                        return JsonResponse({'isError': True, 'Message': ' This ticket already exists'})
                    else:
                        ChangeAssignTickets = models.AssignTicket.objects.get(
                            id=id)
                        tname = ChangeAssignTickets.ticketID.title
                        UserName = ChangeAssignTickets.userID.first_name + \
                            ' ' + ChangeAssignTickets.userID.last_name + ""
                        UserIDs = user_models.Users.objects.get(
                            id=userID, is_delete=False)
                        Tickets = models.AssignTicket.objects.get(
                            id=TicketID, is_delete=False)
                        ChangeAssignTickets.userID = UserIDs
                        ChangeAssignTickets.ticketID = Tickets
                        ChangeAssignTickets.save()
                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Ticket Module / Assign Tickets"
                        action = UserName + " is changed ticket name of " + tname + \
                            'to '+UserIDs.first_name + ' ' + UserIDs.last_name
                        sendTrials(request, username, names,
                                   avatar, action, module)
                        return JsonResponse({'isError': False, 'Message': UserName + " has been successfully changed ticket name of " + tname + 'to '+UserIDs.first_name + ' ' + UserIDs.last_name}, status=200)

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


# Generating username for each user by counting from the last username
def generateTicketNumber():
    user = models.Tickets.objects.all()
    letter = 'TC'

    if len(user) > 0:
        ticket_number = user[0].ticket_number
        serial = int(ticket_number[2:])
    else:
        serial = 0

    serial += 1
    if serial < 10:
        serial = '0000' + str(serial)
    elif serial < 100:
        serial = '000' + str(serial)
    elif serial < 1000:
        serial = '00' + str(serial)
    elif serial < 10000:
        serial = '0' + str(serial)
    return letter + str(serial)


@login_required(login_url='Login')
def ManageReplies(request, id):
    try:
        if id == '0':
            if request.method == 'POST':
                if request.user.is_client or request.user.has_perm('Tickets.add_replyticket'):
                    ticketID = request.POST['ticketID']
                    userID = request.POST['userID']
                    message = request.POST['message']
                    try:

                        get_ticket = models.Tickets.objects.get(
                            id=ticketID, is_delete=False)
                        get_user = user_models.Users.objects.get(
                            id=userID, is_delete=False)

                        if get_user.is_client and get_ticket.userID.id != get_user.id:
                            return JsonResponse({'isError': True, 'Message': 'Unauthorized user'})

                        save_reply = models.ReplyTicket(
                            ticketID=get_ticket, userID=get_user, message=message)
                        save_reply.save()

                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        action = f"{get_user.first_name} {get_user.last_name} has posted comment on {get_ticket.title } ticket"
                        module = "Ticket Module / Tickets"
                        sendTrials(request, username, names,
                                   avatar, action, module)
                        return JsonResponse({'isError': False, 'Message': "Message has been posted"})
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
        else:
            if request.method == 'POST':
                if request.user.is_client or request.user.has_perm('Tickets.change_replyticket'):
                    ticketID = request.POST['ticketID']
                    userID = request.POST['userID']
                    message = request.POST['message']
                    reply = request.POST['reply']

                    get_ticket = models.Tickets.objects.get(
                        id=ticketID, is_delete=False)
                    get_user = user_models.Users.objects.get(
                        id=userID, is_delete=False)

                    if get_user.is_client and get_ticket.userID.id != get_user.id:
                        return JsonResponse({'isError': True, 'Message': 'Unauthorized yuser'})

                    update_replay = models.ReplyTicket.objects.get(id=reply)
                    update_replay.userID = get_user
                    update_replay, ticketID = get_ticket
                    update_replay.message = message
                    update_replay.save()

                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    action = f"{get_user.first_name} {get_user.last_name} update comment on {get_ticket.title } ticket"
                    module = "Ticket Module / Tickets"
                    sendTrials(request, username, names,
                               avatar, action, module)
                    return JsonResponse({'isError': False, 'Message': "Message has been posted"})
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
