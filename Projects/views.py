from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from Users.views import PreviewDate, sendException, sendTrials
from django.db.models.deletion import RestrictedError
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from . import models
from Users import models as user_models
from Tickets import models as tickets_models
from django.core.exceptions import *
# Create your views here.
from datetime import datetime
today = datetime.now()


@login_required(login_url='Login')
def ViewTaskDetails(request, ids):
    try:
        task = models.Task.objects.get(id=ids)

        is_granted = False

        # If the user is agent is the manager
        if task.projectID.manager.id == request.user.id and request.user.has_perm('Projects.project_visibility'):
            is_granted = True

        # if the user is admin and has the view project rule
        if request.user.has_perm('Projects.view_task') or request.user.is_agent:
            is_granted = True

    
        if is_granted:
            gettasks = models.Task.objects.get(id=ids)
            # Checking if another user (agent) accepted the task
            check_if_user_accepted = models.AssignTask.objects.filter(
                taskID=ids, is_accepted=True, is_removed=False, is_assigned=True)
            if len(check_if_user_accepted) > 0 and request.user.is_agent:
                check_if_user_accepted = check_if_user_accepted[0]

                if check_if_user_accepted.userID != request.user:
                    context = {
                        'isError': True,
                        'error':  f"This Task ( {gettasks.task_number} - {gettasks.title}) has been accepted by another user..."


                    }
                    return render(request, 'Layout/Admin/Tasks/taskdetail.html', context)

            # Getting project's deadlines is today
            set_inactive_project_task()

            # Getting tasks

            # Getting task files
            files = models.TaskFile.objects.filter(
                taskID=ids, is_delete=False)

            # Getting assigned tasks
            getassignedTicket = models.AssignTask.objects.filter(
                taskID=ids,  is_removed=False)

            # Is accpeted will be true by default is the user is not agent
            is_accepted = True
            # If the user is agent then he will different then the admin
            if request.user.is_agent:
                # Get tasks assigned to this user
                getassignedTicket = models.AssignTask.objects.filter(
                    taskID=ids, userID=request.user.id, is_removed=False)

                # Checking if he is accepted this task
                is_accepted = models.AssignTask.objects.filter(userID=request.user.id,
                                                               taskID=ids, is_accepted=True, is_removed=False).exists()

            # Getting task progress / activities
            getTaskProgress = models.TaskProgess.objects.filter(
                taskID=ids,  is_delete=False)
            TotalProgress = models.TaskProgess.objects.filter(
                taskID=ids).aggregate(Sum('work_completion'))['work_completion__sum']
            if TotalProgress is None:
                RemainingProgress = 100.0
                TotalProgress = 0.0
            else:
                RemainingProgress = 100-TotalProgress

            # Getting task notes
            notes = models.TaskNote.objects.filter(
                taskID=ids, is_delete=False)

            is_assigned = models.AssignTask.objects.filter(
                taskID=ids, is_assigned=True, is_accepted=True, is_removed=False).exists()

            # Get task comments
            replies = models.TaskComments.objects.filter(taskID=ids)

            context = {
                'isError': False,
                'task': gettasks,
                'assigned': getassignedTicket,
                'is_accepted': is_accepted,
                'is_assigned': is_assigned,
                'Progress': getTaskProgress,
                'TotalProgress': TotalProgress,
                'RemainingProgress': RemainingProgress,
                'Files': files,
                'Notes': notes,
                'replies': replies
            }
            return render(request, 'Layout/Admin/Tasks/taskdetail.html', context)

        else:
            return render(request, 'Auth/404.html')

    except ObjectDoesNotExist as error:
        username = request.user.username
        name = request.user.first_name + ' ' + request.user.last_name
        sendException(
            request, username, name, error)
        return render(request, 'Auth/404.html')

    except ValidationError as error:
        username = request.user.username
        name = request.user.first_name + ' ' + request.user.last_name
        sendException(
            request, username, name, error)
        return render(request, 'Auth/404.html')

    except Exception as error:
        username = request.user.username
        name = request.user.first_name + ' ' + request.user.last_name
        sendException(
            request, username, name, error)
        context = {
            'isError': True,
            'error': "On Error Occurs . Please try refresh the page or contact system administrator",

        }
        return render(request, 'Layout/Admin/Tasks/taskdetail.html', context)


@login_required(login_url='Login')
def Notifications(request):
    models.Notifications.make_seen(request.user)
    context = {
        'messages': models.Notifications.objects.filter(userID=request.user),
    }
    return render(request, 'Layout/notifications.html', context)


@login_required(login_url='Login')
def Tasks(request):
    if request.user.has_perm('Projects.view_task') and not request.user.is_client:
        # Getting project's deadlines is today
        try:
            set_inactive_project_task()

            CheckSearchQuery = 'SearchQuery' in request.GET
            CheckDataNumber = 'DataNumber' in request.GET
            CheckFilterStatus = 'FilterStatus' in request.GET
            FilterStatus = {}
            status = "All"
            DataNumber = 10
            SearchQuery = ''
            TaskList = []
            if CheckFilterStatus:
                status = request.GET['FilterStatus']
                if status != "All":
                    FilterStatus['status'] = status

            if CheckDataNumber:
                DataNumber = int(request.GET['DataNumber'])

            if CheckSearchQuery:
                SearchQuery = request.GET['SearchQuery']
                TaskList = models.Task.objects.filter(Q(task_number__icontains=SearchQuery)
                                                      | Q(title__icontains=SearchQuery) | Q(
                    projectID__title__icontains=SearchQuery) | Q(status__icontains=SearchQuery)
                    | Q(priority__icontains=SearchQuery) | Q(category__name__icontains=SearchQuery), **FilterStatus, is_delete=False)
            else:
                TaskList = models.Task.objects.filter(
                    **FilterStatus, is_delete=False).order_by('-created_at')

            paginator = Paginator(TaskList, DataNumber)

            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            Pages = paginator.get_elided_page_range(
                page_obj.number, on_each_side=0, on_ends=1)

            context = {
                'isError': False,
                'page_obj': page_obj,
                'SearchQuery': SearchQuery,
                'DataNumber': DataNumber,
                'TotalTickets': len(TaskList),
                'Pages': Pages,
                'Status': status
            }
            return render(request, 'Layout/Admin/Tasks/tasks.html', context)
        except Exception as error:
            username = request.user.username
            name = request.user.first_name + ' ' + request.user.last_name
            sendException(
                request, username, name, error)
            context = {
                'isError': True,
                'error': "On Error Occurs . Please try refresh the page or contact system administrator",

            }
            return render(request, 'Layout/Admin/Tasks/tasks.html', context)
    else:
        return render(request,  'Auth/404.html')


@login_required(login_url='Login')
def AgentTasks(request):
    if request.user.is_agent:
        CheckSearchQuery = 'SearchQuery' in request.GET
        CheckDataNumber = 'DataNumber' in request.GET
        CheckFilterStatus = 'FilterStatus' in request.GET
        FilterStatus = {}
        status = "All"
        DataNumber = 10
        SearchQuery = ''
        TaskList = []

        # Getting project's deadlines is today
        set_inactive_project_task()

        if CheckFilterStatus:
            status = request.GET['FilterStatus']
            if status != "All":
                FilterStatus['taskID__status'] = status

        if CheckDataNumber:
            DataNumber = int(request.GET['DataNumber'])

        if CheckSearchQuery:
            SearchQuery = request.GET['SearchQuery']
            TaskList = models.AssignTask.objects.filter(Q(taskID__task_number__icontains=SearchQuery)
                                                        | Q(taskID__title__icontains=SearchQuery) | Q(
                taskID__description__icontains=SearchQuery) | Q(
                taskID__projectID__title__icontains=SearchQuery)
                | Q(taskID__priority__icontains=SearchQuery) | Q(taskID__status__icontains=SearchQuery) | Q(taskID__category__name__icontains=SearchQuery), **FilterStatus, userID=request.user.id, is_assigned=True, is_removed=False)
        else:
            TaskList = models.AssignTask.objects.filter(
                **FilterStatus, userID=request.user.id, is_assigned=True, is_removed=False).order_by('-created_at')

        paginator = Paginator(TaskList, DataNumber)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        Pages = paginator.get_elided_page_range(
            page_obj.number, on_each_side=0, on_ends=1)

        context = {
            'page_obj': page_obj,
            'SearchQuery': SearchQuery,
            'DataNumber': DataNumber,
            'TotalTasks': len(TaskList),
            'Pages': Pages,
            'Status': status
        }
        return render(request, 'Layout/Admin/Tasks/agent-tasks.html', context)
    else:
        return render(request,  'Auth/404.html')

# End View Task

# Task Management


def set_inactive_project_task():
    # Getting project's deadlines is today
    deadline_ending_projects = models.Project.objects.filter(
        end__lt=today, is_active=True)

    for index, item in enumerate(deadline_ending_projects):
        item.set_inactive()

        # Send notification for the admin
        msg = f"The project {item.title}'s deadline has been closed"
        models.Notifications.save_notification(
            'Project', item.manager, item.id, msg, 'ri-projector-fill')

    deadline_ending_task = models.Task.objects.filter(
        end__lt=today, is_active=True)

    for index, item in enumerate(deadline_ending_task):
        item.set_inactive()

        # Send notification for the admin
        msg = f"The task {item.title}'s deadline has been closed"
        models.Notifications.save_notification(
            'Task', item.projectID.manager, item.id, msg, 'ri-task-line')

        get_assigned_user = models.AssignTask.objects.filter(
            taskID=item.id, is_accepted=True, is_assigned=True, is_removed=False)

        if len(get_assigned_user) > 0:
            get_assigned_user = get_assigned_user[0]
            # Send notification for the admin
            msg = f"The task {item.title}'s deadline has been closed"
            models.Notifications.save_notification(
                'Task', get_assigned_user.userID, item.id, msg, 'ri-task-line')


@login_required(login_url='Login')
def ManageTaskNotes(request, id):

    if id == 0:
        if request.method == 'POST':
            if not request.user.is_client and request.user.has_perm('Projects.add_tasknote'):
                try:
                    note = request.POST.get('note')
                    task = request.POST.get('task')

                    # Check if data is valid
                    if note == '' or note is None:
                        return JsonResponse({'isError': True, 'Message': 'Enter your note'})

                    TaskID = models.Task.objects.get(id=task)

                    if checkAssignedUserTask(TaskID.id, request.user)['isError'] == True:
                        return JsonResponse(checkAssignedUserTask(TaskID.id, request.user), status=200)

                    user = models.TaskNote.objects.filter(
                        taskID=TaskID.id)

                    if len(user) > 0:
                        noteID = user[0].noteID
                        serial = int(noteID[2:])
                    else:
                        serial = 0
                    noteID = generateSerialNumber('NT', serial)
                    save_task_note = models.TaskNote(
                        taskID=TaskID,  note=note, noteID=noteID, userID=request.user)
                    save_task_note.save()

                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Project Module / Task Note"
                    action = f'{request.user.first_name} is Created New Task Note number of  ( {save_task_note.noteID} ) with Task Number of  {save_task_note.taskID.task_number}'
                    sendTrials(request, username, names,
                               avatar, action, module)
                    return JsonResponse({'isError': False, 'Message': "Task note has been created successfully"}, status=200)

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
        if request.method == 'GET':
            if not request.user.has_perm('Projects.change_tasknote'):
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)
            try:

                GetTaskNote = models.TaskNote.objects.get(id=id)

                if checkAssignedUserTask(GetTaskNote.taskID.id, request.user)['isError'] == True:
                    return JsonResponse(checkAssignedUserTask(GetTaskNote.taskID.id, request.user), status=200)

                return JsonResponse({'isError': False, 'Message': {
                    'id': GetTaskNote.id,
                    'note': GetTaskNote.note,
                }})
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

        if request.method == 'POST':
            if not request.user.is_client and request.user.has_perm('Projects.change_tasknote'):
                try:
                    note = request.POST.get('note')
                    # Check if data is valid
                    if note == '' or note is None:
                        return JsonResponse({'isError': True, 'Message': 'Enter Task note'})
                    update_task_note = models.TaskNote.objects.get(id=id)

                    if checkAssignedUserTask(update_task_note.taskID.id, request.user)['isError'] == True:
                        return JsonResponse(checkAssignedUserTask(update_task_note.taskID.id, request.user), status=200)

                    update_task_note.note = note
                    update_task_note.save()

                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Project Module / Task"
                    action = f'Updated Task Note ( {update_task_note.get_short_notes()} ) by {request.user.first_name}'
                    sendTrials(request, username, names,
                               avatar, action, module)
                    return JsonResponse({'isError': False, 'Message': "Task note has been updated successfully"}, status=200)
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

        if request.method == 'DELETE':
            if not request.user.has_perm('Projects.delete_tasknote'):
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)
            try:

                DeleteTask = models.TaskNote.objects.get(id=id)

                if checkAssignedUserTask(DeleteTask.taskID.id, request.user)['isError'] == True:
                    return JsonResponse(checkAssignedUserTask(DeleteTask.taskID.id, request.user), status=200)

                DeleteTask.is_delete = True
                DeleteTask.save()

                username = request.user.username
                names = request.user.first_name + ' ' + request.user.last_name
                avatar = str(request.user.avatar)
                module = "Project Module / Task Note"
                action = f'Delete Task Note ( {DeleteTask.get_short_notes} ) by {request.user.first_name}'
                sendTrials(request, username, names,
                           avatar, action, module)
                return JsonResponse({'isError': False, 'Message': "Task note has been deleted successfully"})
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
def ManageTaskFiles(request, id):

    if id == 0:
        if request.method == 'POST':
            # if not request.user.is_client and request.user.has_perm('Projects.add_projectfile'):
            if request.user.has_perm('Projects.add_taskfile'):
                title = request.POST.get('title')
                task = request.POST.get('task')
                thumbnail = request.FILES.get('file')
                try:
                    task = models.Task.objects.get(id=task)

                    if request.user.is_agent:
                        if checkAssignedUserTask(task.id, request.user)['isError'] == True:
                            return JsonResponse(checkAssignedUserTask(task.id, request.user), status=200)

                    # Check if data is valid
                    if title == '' or title is None:
                        return JsonResponse({'isError': True, 'Message': 'Enter task title'})

                    if thumbnail == '' or thumbnail is None:
                        return JsonResponse({'isError': True, 'Message': f'Enter task thumbnail'})

                    # Check images extension
                    extention = thumbnail.name.split(".")[-1]
                    extention = extention.lower()

                    extension_types = ['jpg', 'png', 'jpeg', 'doc',
                                       'docx', 'ppt', 'pptx', 'pdf', 'txt', 'xlsx']
                    x = " , ".join(extension_types)

                    if not extention in extension_types:
                        return JsonResponse({'isError': True, 'Message': f"This field only supports {x}"})

                    if thumbnail.size > 2621440:
                        return JsonResponse({'isError': True, 'Message': thumbnail.name+'  file is more than 2mb size'})

                    thumbnail.name = f"{request.user.username}-" + \
                        remove_non_ascii_2(thumbnail.name)

                    save_Task_file = models.TaskFile(
                        taskID=task, file=thumbnail, title=title)
                    save_Task_file.save()

                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Project Module / Task"
                    action = f'Created New Task File ( {save_Task_file.title} ) by {request.user.first_name}'
                    sendTrials(request, username, names,
                               avatar, action, module)
                    return JsonResponse({'isError': False, 'Message': "Task file has been created successfully"}, status=200)
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
        if request.method == 'GET':
            if not request.user.has_perm('Projects.change_taskfile'):
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)
            try:

                TaskFile = models.TaskFile.objects.get(id=id)

                if checkAssignedUserTask(TaskFile.taskID.id, request.user)['isError'] == True:
                    return JsonResponse(checkAssignedUserTask(TaskFile.taskID.id, request.user), status=200)

                return JsonResponse({'isError': False, 'Message': {
                    'id': TaskFile.id,
                    'title': TaskFile.title,
                }})
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

        if request.method == 'POST':
            if not request.user.is_client and request.user.has_perm('Projects.change_taskfile'):
                title = request.POST.get('title')
                try:

                    # Check if data is valid
                    if title == '' or title is None:
                        return JsonResponse({'isError': True, 'Message': 'Enter project title'})

                    UpdateTaskFile = models.TaskFile.objects.get(id=id)

                    if checkAssignedUserTask(UpdateTaskFile.taskID.id, request.user)['isError'] == True:
                        return JsonResponse(checkAssignedUserTask(UpdateTaskFile.taskID.id, request.user), status=200)

                    UpdateTaskFile.title = title
                    UpdateTaskFile.save()

                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Project Module / Task File"
                    action = f'Updated Task File ( {UpdateTaskFile.title} ) by {request.user.first_name}'
                    sendTrials(request, username, names,
                               avatar, action, module)
                    return JsonResponse({'isError': False, 'Message': "Task file has been updated successfully"}, status=200)
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

        if request.method == 'DELETE':
            if not request.user.has_perm('Projects.delete_taskfile'):
                message = {
                    'isError': True,
                    'Message': '401-Unauthorized access.you do not have permission to access this page.'
                }
                return JsonResponse(message, status=200)
            try:

                TaskFileDelete = models.TaskFile.objects.get(id=id)

                if checkAssignedUserTask(TaskFileDelete.taskID.id, request.user)['isError'] == True:
                    return JsonResponse(checkAssignedUserTask(TaskFileDelete.taskID.id, request.user), status=200)

                TaskFileDelete.is_delete = True
                TaskFileDelete.save()

                username = request.user.username
                names = request.user.first_name + ' ' + request.user.last_name
                avatar = str(request.user.avatar)
                module = "Project Module / Task File "
                action = f'Delete Task File ( {TaskFileDelete.title} ) by {request.user.first_name}'
                sendTrials(request, username, names,
                           avatar, action, module)
                return JsonResponse({'isError': False, 'Message': "Task  file has been deleted successfully"})
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
def ManageTaskProgress(request, id):
    if id == '0':
        pass
    else:
        if request.method == 'GET':
            if request.user.is_agent and request.user.has_perm('Projects.change_taskprogess'):
                try:
                    TaskProgess = models.TaskProgess.objects.get(id=id)

                    if checkAssignedUserTask(TaskProgess.taskID.id, request.user)['isError'] == True:
                        return JsonResponse(checkAssignedUserTask(TaskProgess.taskID.id, request.user), status=200)

                    message = {
                        'id': TaskProgess.id,
                        'description': TaskProgess.description,
                        'work_completion': TaskProgess.work_completion,

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

        if request.method == 'POST':
            if request.user.is_agent and request.user.has_perm('Projects.change_taskprogess'):
                WorkCompletion = request.POST.get('WorkCompletion')
                Description = request.POST.get('Description')
                try:
                    TaskProgress = models.TaskProgess.objects.get(id=id)

                    if checkAssignedUserTask(TaskProgress.taskID.id, request.user)['isError'] == True:
                        return JsonResponse(checkAssignedUserTask(TaskProgress.taskID.id, request.user), status=200)

                    CurrentProgress = models.TaskProgess.objects.filter(
                        taskID=TaskProgress.taskID).aggregate(Sum('work_completion'))['work_completion__sum']
                    CurrentProgress = abs(
                        CurrentProgress-TaskProgress.work_completion)
                    if float(WorkCompletion) > 100:
                        return JsonResponse({'isError': True, 'Message': 'Work completion  must be less than 100'}, status=200)
                    if float(CurrentProgress) + float(WorkCompletion) > 100:
                        return JsonResponse({'isError': True, 'Message': f"Your remaining progress is {100.0 -CurrentProgress} %"}, status=200)
                    else:

                        TaskProgress.description = Description
                        TaskProgress.work_completion = WorkCompletion
                        TaskProgress.save()
                        totalprogess = models.TaskProgess.objects.filter(
                            taskID=TaskProgress.taskID).aggregate(Sum('work_completion'))['work_completion__sum']
                        if totalprogess is not None:
                            ChangeTaskStatus = models.Task.objects.get(
                                id=TaskProgress.taskID.id)
                            if totalprogess == 100:
                                ChangeTaskStatus.status = "Completed"
                                ChangeTaskStatus.save()
                            else:
                                ChangeTaskStatus.status = "Inprogress"
                                ChangeTaskStatus.save()

                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        action = f"{names}  update  Work completion   of {WorkCompletion}"
                        module = "Project Module / Task"
                        sendTrials(request, username, names,
                                   avatar, action, module)
                        return JsonResponse({'isError': False, 'Message': 'Task priority has been successfully added'}, status=200)

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
def ManageAssignTask(request, ids):
    if ids == 0:
        # Post Assign Ticket
        if request.method == 'POST':
            if request.user.has_perm('Projects.add_assigntask') and not request.user.is_client:
                userID = request.POST.get('user')
                TaskIDs = request.POST.get('task')
                try:
                    UserIDss = user_models.Users.objects.get(
                        id=userID, is_delete=False)

                    if models.AssignTask.objects.filter(userID=userID, taskID=TaskIDs, is_removed=False, is_accepted=False).exists():
                        return JsonResponse({'isError': True, 'Message': ' This task already assigned ' + UserIDss.first_name + " "+UserIDss.last_name})

                    elif models.AssignTask.objects.filter(userID=userID, taskID=TaskIDs, is_removed=False, is_accepted=True).exists():
                        return JsonResponse({'isError': True, 'Message': ' This task already assigned ' + UserIDss.first_name + " "+UserIDss.last_name})

                    elif models.AssignTask.objects.filter(Q(is_accepted=True) | Q(is_accepted=False), userID=userID, taskID=TaskIDs, is_removed=True).exists():
                        UpdateRemove = models.AssignTask.objects.get(Q(is_accepted=True) | Q(is_accepted=False),
                                                                     userID=userID, taskID=TaskIDs, is_removed=True)
                        UpdateRemove.is_removed = False
                        UpdateRemove.is_accepted = False
                        UpdateRemove.is_assigned = True
                        UpdateRemove.assigned_by = request.user
                        UpdateRemove.save()
                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Project Module / Assign Task"
                        action = UpdateRemove.userID.first_name + ' ' + UpdateRemove.userID.last_name + \
                            " is assigned task name of " + UpdateRemove.taskID.task_number
                        sendTrials(request, username, names,
                                   avatar, action, module)
                        message = {
                            'isError': False,
                            'Message': UpdateRemove.userID.first_name + ' ' + UpdateRemove.userID.last_name + " has been successfully task ticket name of " + UpdateRemove.taskID.task_number
                        }

                        # Send notification for the admin
                        msg = f"The task {UpdateRemove.taskID.title} has been assigned to {UpdateRemove.userID.get_full_name()}"
                        models.Notifications.save_notification(
                            'Task', UpdateRemove.taskID.projectID.manager, UpdateRemove.taskID.id, msg, 'ri-task-line')

                        # Send notification for the agent
                        msg = f"New task {UpdateRemove.taskID.title} has been assigned to you"
                        models.Notifications.save_notification(
                            'Task', UpdateRemove.userID, UpdateRemove.taskID.id, msg, 'ri-task-line')

                        return JsonResponse(message, status=200)

                    else:

                        UserIDs = user_models.Users.objects.get(
                            id=userID, is_delete=False)
                        getTask = models.Task.objects.get(
                            id=TaskIDs, is_delete=False)
                        getTask.status = "Assigned"
                        AssignTask = models.AssignTask(
                            userID=UserIDs, taskID=getTask, assigned_by=request.user, is_assigned=True)
                        AssignTask.save()
                        getTask.save()
                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Project Module / Assign Task"
                        action = UserIDs.first_name + ' ' + UserIDs.last_name + \
                            " is assigned ticket name of " + getTask.title + \
                            " ( " + getTask.task_number+")"
                        sendTrials(request, username, names,
                                   avatar, action, module)
                        message = {
                            'isError': False,
                            'Message': UserIDs.first_name + ' ' + UserIDs.last_name + " has been successfully assigned ticket name of " + getTask.title
                        }

                        # Send notification for the admin
                        msg = f"The task {getTask.title} has been assigned to {UserIDs.get_full_name()}"
                        models.Notifications.save_notification(
                            'Task', getTask.projectID.manager, getTask.id, msg, 'ri-task-line')

                        # Send notification for the agent
                        msg = f"New task {getTask.title} has been assigned to you"
                        models.Notifications.save_notification(
                            'Task', UserIDs, getTask.id, msg, 'ri-task-line')
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
            if request.user.has_perm('Projects.view_assigntask') and not request.user.is_client:
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
            if request.user.has_perm('Projects.delete_assigntask') and not request.user.is_client:
                try:

                    DeleteAssing = models.AssignTask.objects.get(id=ids)
                    # checkStatus = models.AssignTask.objects.filter(
                    #     ticketID=DeleteAssing)
                    DeleteAssing.is_removed = True
                    DeleteAssing.is_assigned = False

                    tname = DeleteAssing.taskID.title + \
                        " ("+DeleteAssing.taskID.task_number+")"
                    UserName = DeleteAssing.userID.first_name + \
                        ' ' + DeleteAssing.userID.last_name + ""

                    # Send notification for the admin
                    msg = f"The task {DeleteAssing.taskID.title} has been removed from {DeleteAssing.userID.get_full_name()}"
                    models.Notifications.save_notification(
                        'Task', DeleteAssing.taskID.projectID.manager, DeleteAssing.taskID.id, msg, 'ri-task-line')

                    # Send notification for the agent
                    msg = f"The task {DeleteAssing.taskID.title} has been removed from you"
                    models.Notifications.save_notification(
                        'Task', DeleteAssing.userID, DeleteAssing.taskID.id, msg, 'ri-task-line')

                    DeleteAssing.save()

                    CheckAssign = models.AssignTask.objects.filter(
                        taskID=DeleteAssing.taskID, is_assigned=True, is_accepted=True).exists()
                    Checkstatus = models.AssignTask.objects.filter(
                        taskID=DeleteAssing.taskID, is_assigned=True, is_accepted=False).exists()

                    if CheckAssign == True:
                        ChangeTicketStatus = models.Task.objects.get(
                            id=DeleteAssing.taskID.id)
                        ChangeTicketStatus.status = "Inprogress"
                        ChangeTicketStatus.save()
                    if Checkstatus == True:
                        ChangeTicketStatus = models.Task.objects.get(
                            id=DeleteAssing.taskID.id)
                        ChangeTicketStatus.status = "Assigned"
                        ChangeTicketStatus.save()
                    if CheckAssign == False and Checkstatus == False:
                        ChangeTicketStatus = models.Task.objects.get(
                            id=DeleteAssing.taskID.id)
                        ChangeTicketStatus.status = "On-Hold"
                        ChangeTicketStatus.save()

                    username = request.user.username
                    name = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Project Module / Assign Task"
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

                    if models.AssignTask.objects.filter(userID=userID, ticketID=TicketID).exists():
                        return JsonResponse({'isError': True, 'Message': ' This ticket already exists'})
                    else:
                        ChangeAssignTask = models.AssignTask.objects.get(
                            id=ids)
                        tname = ChangeAssignTask.taskID.title
                        UserName = ChangeAssignTask.userID.first_name + \
                            ' ' + ChangeAssignTask.userID.last_name + ""
                        UserIDs = user_models.Users.objects.get(
                            id=userID, is_delete=False)
                        Tickets = models.AssignTask.objects.get(
                            id=TicketID, is_delete=False)
                        ChangeAssignTask.userID = UserIDs
                        ChangeAssignTask.taskID = Tickets
                        ChangeAssignTask.save()
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


@login_required(login_url='Login')
def ManageTasks(request, id):
    Type = request.POST.get('Type')
    if id == '0':

        # Post New Task
        if request.method == 'POST':
            try:
                ProjectName = request.POST.get('ProjectName')
                title = request.POST.get('title')
                Agent = request.POST.get('Agent')
                StartDate = request.POST.get('StartDate')
                EndDate = request.POST.get('EndDate')
                Category = request.POST.get('Category')
                Priority = request.POST.get('Priority')
                Description = request.POST.get('Description')
                if ProjectName == "" or ProjectName is None:
                    return JsonResponse({'isError': True, 'Message': 'Please Select project name'})
                if Agent == "" or Agent is None:
                    return JsonResponse({'isError': True, 'Message': 'Please Enter Agent Name'})
                if EndDate < StartDate:
                    return JsonResponse({'isError': True, 'Message': 'Please end date must greater than or equal to start date'})

                try:
                    Documents = request.FILES['Documents']
                except KeyError:
                    Documents = None

                if Documents is not None:
                    extention = Documents.name.split(".")[-1]
                extension_types = ['JPEG', 'jpeg', 'JPG',
                                   'jpg', 'png', "PNG", 'pdf', 'PDF']
                if Documents is not None and not extention in extension_types:
                    return JsonResponse({'isError': True, 'Message': 'This Feild Only supports jpeg,jpg,png extensions.'})
                if Documents is not None and Documents.size > 2621440:
                    return JsonResponse({'isError': True, 'Message': Documents.name + '  file is more than 2MB size'})
                if Type == 'Addtask' and request.user.has_perm('Projects.add_task') and not request.user.is_client:
                    Project = models.Project.objects.get(
                        id=ProjectName, is_delete=False)
                    if EndDate > str(Project.end):
                        return JsonResponse({'isError': True, 'Message': 'Please end date must less than or equal to the project start date'})

                    Users = user_models.Users.objects.get(
                        id=Agent, is_delete=False)
                    Categories = models.Category.objects.get(
                        id=Category, is_delete=False)

                    Task_numbers = models.Task.objects.all()

                    if len(Task_numbers) > 0:
                        task_number = Task_numbers[0].task_number
                        serial = int(task_number[3:])
                    else:
                        serial = 0
                    task_number = generateSerialNumber('TSK', serial)

                    CreateTasks = models.Task(task_number=task_number, title=title, description=Description, category=Categories,
                                              projectID=Project, status='On-Hold', priority=Priority, start=StartDate, end=EndDate,
                                              document=Documents)
                    CreateTasks.save()
                    AssignTask = models.AssignTask(
                        userID=Users, taskID=CreateTasks, is_assigned=True)
                    AssignTask.save()
                    CreateTasks.status = "Assigned"
                    CreateTasks.save()

                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Project Module  / Tasks"
                    action = "Created new task with the Task No " + \
                        str(task_number)
                    sendTrials(request, username, names,
                               avatar, action, module)
                    action1 = Users.first_name + ' ' + Users.last_name + \
                        " is assigned ticket name of " + CreateTasks.task_number
                    sendTrials(request, username, names,
                               avatar, action1, module)
                    message = {
                        'isError': False,
                        'Message': 'New Tasks has been successfully created'
                    }

                    # Send notification for the admin
                    msg = f"New task {CreateTasks.title} has been created for {CreateTasks.projectID.title} and the task has been assigned to {Users.get_full_name()}"
                    models.Notifications.save_notification(
                        'Task', CreateTasks.projectID.manager, CreateTasks.id, msg, 'ri-task-line')

                    # Send notification for the agent
                    msg = f"New task {CreateTasks.title} has been assigned to you"
                    models.Notifications.save_notification(
                        'Task', Users, CreateTasks.id, msg, 'ri-task-line')

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
        # Get Single Task And Check if the user has the permisison
        if request.method == 'GET':
            if request.user.has_perm('Projects.view_task') and not request.user.is_client:
                try:
                    Tasks = models.Task.objects.get(
                        id=id, is_delete=False)

                    message = {
                        'id': Tasks.id,
                        'title': Tasks.title,
                        'description': Tasks.description,
                        'priority': Tasks.priority,
                        'category': Tasks.category.id,
                        'projectID': Tasks.projectID.id,
                        'start': Tasks.start,
                        'end': Tasks.end,


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

        # Update Task And Check if the user has the permisison
        if request.method == 'POST':
            if Type == "change" and request.user.has_perm('Projects.change_task') and not request.user.is_client:

                ProjectName = request.POST.get('ProjectName')
                title = request.POST.get('title')
                StartDate = request.POST.get('StartDate')
                EndDate = request.POST.get('EndDate')
                Category = request.POST.get('Category')
                Priority = request.POST.get('Priority')
                Description = request.POST.get('Description')

                if ProjectName == "" or ProjectName is None:
                    return JsonResponse({'isError': True, 'Message': 'Please Select project name'})
                
                if EndDate < StartDate:
                    return JsonResponse({'isError': True, 'Message': 'Please end date must greater than or equal to start date'})

                
                try:
                    ChangeTask = models.Task.objects.get(
                        id=id, is_delete=False)
                    Categories = models.Category.objects.get(
                        id=Category, is_delete=False)
                    Project = models.Project.objects.get(
                        id=ProjectName, is_delete=False)

                    if EndDate > str(Project.end):
                        return JsonResponse({'isError': True, 'Message': 'Please end date must less than or equal to the project start date'})


                    ChangeTask.title = title
                    ChangeTask.description = Description
                    ChangeTask.category = Categories
                    ChangeTask.projectID = Project
                    ChangeTask.priority = Priority
                    ChangeTask.start = StartDate
                    ChangeTask.end = EndDate

                    if EndDate > StartDate:
                        ChangeTask.is_active = True

                    ChangeTask.save()
                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    action = "Updated task with task Number of" + \
                        str(ChangeTask.task_number)
                    module = "Project Module / Tasks"
                    sendTrials(request, username, names,
                               avatar, action, module)
                    return JsonResponse({'isError': False, 'Message': 'Tasks has been successfully updated'}, status=200)

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

            elif Type == "Changestatus" and request.user.has_perm('Projects.change_priority_task') and not request.user.is_client:
                status = request.POST.get('status')

                try:
                    TaskStatus = models.Task.objects.get(
                        id=id, is_delete=False)

                    CheckAssign = models.AssignTask.objects.filter(
                        taskID=TaskStatus.id).exists()
                    if CheckAssign == False:
                        return JsonResponse({'isError': True, 'Message': 'Sorry!! This Task can not be assigned any agent'}, status=200)
                    else:
                        statuss = TaskStatus.status

                        TaskStatus.status = status
                        TaskStatus.save()
                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        action = "Updated Task status of " + statuss + " to  " + \
                            status+" with Task number of  " + TaskStatus.task_number
                        module = "Project Module / Task"
                        sendTrials(request, username, names,
                                   avatar, action, module)
                        return JsonResponse({'isError': False, 'Message': 'Task status has been successfully updated'}, status=200)

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

            elif Type == "Changepriority" and request.user.has_perm('Projects.change_priority_task') and not request.user.is_client:
                priority = request.POST.get('priority')

                try:
                    Taskpriority = models.Task.objects.get(
                        id=id, is_delete=False)
                    prioritys = Taskpriority.priority

                    Taskpriority.priority = priority
                    Taskpriority.save()
                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    action = "Updated task priority of " + prioritys + " to  " + \
                        priority+" with ticket number of  " + Taskpriority.task_number
                    module = "Project Module / Task"
                    sendTrials(request, username, names,
                               avatar, action, module)
                    return JsonResponse({'isError': False, 'Message': 'Task priority has been successfully updated'}, status=200)

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

            elif Type == "Progress" and request.user.is_agent and request.user.has_perm('Projects.add_taskprogess'):
                WorkCompletion = request.POST.get('WorkCompletion')
                Description = request.POST.get('Description')
                try:
                    CurrentProgress = models.TaskProgess.objects.filter(
                        taskID=id).aggregate(Sum('work_completion'))['work_completion__sum']
                    if CurrentProgress is None:
                        CurrentProgress = 0

                    if float(WorkCompletion) > 100:
                        return JsonResponse({'isError': True, 'Message': 'Work completion  must be less than 100'}, status=200)
                    if float(CurrentProgress) + float(WorkCompletion) > 100:
                        return JsonResponse({'isError': True, 'Message': 'Only Remaining Progress is ' + str(CurrentProgress) + "%"}, status=200)
                    else:
                        TaskIDs = models.Task.objects.get(id=id)
                        TaskProgress = models.TaskProgess(
                            taskID=TaskIDs, description=Description, work_completion=float(WorkCompletion))
                        TaskProgress.save()
                        totalprogess = models.TaskProgess.objects.filter(
                            taskID=TaskProgress.taskID).aggregate(Sum('work_completion'))['work_completion__sum']
                        if totalprogess is not None:
                            ChangeTaskStatus = models.Task.objects.get(
                                id=TaskProgress.taskID.id)
                            if totalprogess == 100:
                                ChangeTaskStatus.status = "Completed"
                                ChangeTaskStatus.save()
                            else:
                                ChangeTaskStatus.status = "Inprogress"
                                ChangeTaskStatus.save()
                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        action = f"{names}  added  Work completion   of {WorkCompletion}"
                        module = "Project Module / Task"
                        sendTrials(request, username, names,
                                   avatar, action, module)
                        return JsonResponse({'isError': False, 'Message': 'Task priority has been successfully added'}, status=200)

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
                    Tasklists = models.AssignTask.objects.filter(
                        taskID=id, is_removed=False).order_by('-is_accepted')
                    iscepts = Tasklists[0]

                    if iscepts.is_accepted == True:
                        return JsonResponse({'isError': True, 'Message': 'This Ticket already accept by '+iscepts.userID.first_name + ' '+iscepts.userID.last_name}, status=200)

                    else:
                        IDs = request.user.id
                        AcceptTask = models.AssignTask.objects.get(
                            taskID=id, userID=IDs)
                        Changestatus = models.Task.objects.get(
                            id=id, is_delete=False)
                        Changestatus.status = "Inprogress"
                        AcceptTask.is_accepted = True
                        AcceptTask.save()
                        Changestatus.save()

                        # Send notification for the admin
                        msg = f"{AcceptTask.userID.get_full_name()} has accepted the task {Changestatus.title}"
                        models.Notifications.save_notification(
                            'Task', Changestatus.projectID.manager, Changestatus.id, msg, 'ri-task-line')

                        username = request.user.username
                        names = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        action = names + " has been accepted ticket number of " + \
                            AcceptTask.taskID.task_number
                        module = "Ticket Module / Tickets"
                        sendTrials(request, username, names,
                                   avatar, action, module)
                        return JsonResponse({'isError': False, 'Message': names + " has been accepted ticket number of " + AcceptTask.taskID.task_number}, status=200)

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

        # Delete Task And Check if the user has the permisison
        if request.method == 'DELETE':
            if request.user.has_perm('Projects.delete_task') and not request.user.is_client:
                try:

                    TasksDelete = models.Task.objects.get(
                        id=id, is_delete=False)
                    checkAssigned = models.AssignTask.objects.filter(
                        taskID=TasksDelete.id, is_removed=False).exists()
                    checkComment = models.TaskComments.objects.filter(
                        taskID=TasksDelete.id).exists()
                    checkNote = models.TaskNote.objects.filter(
                        taskID=TasksDelete.id, is_delete=False).exists()
                    checkfile = models.TaskFile.objects.filter(
                        taskID=TasksDelete.id, is_delete=False).exists()

                    if checkAssigned or checkComment or checkNote or checkfile:
                        return JsonResponse({'isError': True, 'Message': 'Cannot delete some instances of model because they are referenced through restricted foreign keys'}, status=200)
                    else:
                        pname = TasksDelete.task_number
                        TasksDelete.is_delete = True
                        TasksDelete.save()
                        username = request.user.username
                        name = request.user.first_name + ' ' + request.user.last_name
                        avatar = str(request.user.avatar)
                        module = "Project Module  / Task"
                        action = "Deleted Task with the Task Number of " + pname
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


# End Task Management


@login_required(login_url='Login')
def Projects(request):
    if request.user.has_perm('Projects.view_project') and not request.user.is_client:
        # Getting project's deadlines is today
        set_inactive_project_task()

        CheckSearchQuery = 'SearchQuery' in request.GET
        CheckDataNumber = 'DataNumber' in request.GET
        DataNumber = 10
        SearchQuery = ''
        projectsList = []

        if CheckDataNumber:
            DataNumber = int(request.GET['DataNumber'])

        if CheckSearchQuery:
            SearchQuery = request.GET['SearchQuery']
            projectsList = models.Project.objects.filter(Q(projectID__icontains=SearchQuery) | Q(title__icontains=SearchQuery) | Q(
                priority__icontains=SearchQuery) | Q(is_active__icontains=SearchQuery), is_delete=False)
        else:
            projectsList = models.Project.objects.filter(is_delete=False)

        paginator = Paginator(projectsList, DataNumber)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        Pages = paginator.get_elided_page_range(
            page_obj.number, on_each_side=0, on_ends=1)

        # Get project categories
        categories = tickets_models.Category.objects.filter(type='Project')

        context = {
            'page_obj': page_obj,
            'SearchQuery': SearchQuery,
            'DataNumber': DataNumber,
            'projectsList': len(projectsList),
            'Pages': Pages,
            'Categories': categories
        }
        return render(request, 'Layout/Admin/Project/project.html', context)
    else:
        return render(request,  'Auth/404.html')


@login_required(login_url='Login')
def ManagerProjects(request):
    if request.user.is_admin or request.user.is_superuser:
        # Getting project's deadlines is today
        set_inactive_project_task()

        CheckSearchQuery = 'SearchQuery' in request.GET
        CheckDataNumber = 'DataNumber' in request.GET
        DataNumber = 10
        SearchQuery = ''
        projectsList = []

        if CheckDataNumber:
            DataNumber = int(request.GET['DataNumber'])

        if CheckSearchQuery:
            SearchQuery = request.GET['SearchQuery']
            projectsList = models.Project.objects.filter(Q(projectID__icontains=SearchQuery) | Q(title__icontains=SearchQuery) | Q(
                priority__icontains=SearchQuery) | Q(is_active__icontains=SearchQuery), manager=request.user, is_delete=False)
        else:
            projectsList = models.Project.objects.filter(
                manager=request.user, is_delete=False)

        paginator = Paginator(projectsList, DataNumber)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        Pages = paginator.get_elided_page_range(
            page_obj.number, on_each_side=0, on_ends=1)

        context = {
            'page_obj': page_obj,
            'SearchQuery': SearchQuery,
            'DataNumber': DataNumber,
            'projectsList': len(projectsList),
            'Pages': Pages,
        }
        return render(request, 'Layout/Admin/Project/manager_projects.html', context)
    else:
        return render(request,  'Auth/404.html')


@login_required(login_url='Login')
def ManageProject(request, id):
    try:
        if id == '0':
            if request.method == 'POST':
                if not request.user.is_client and request.user.has_perm('Projects.add_project'):
                    title = request.POST.get('title')
                    thumbnail = request.FILES.get('thumbnail')
                    category = request.POST.get('category')
                    priority = request.POST.get('priority')
                    status = request.POST.get('status')
                    start = request.POST.get('start')
                    end = request.POST.get('end')
                    manager = request.POST.get('manager')

                    # Check if data is valid
                    if title == '' or title is None:
                        return JsonResponse({'isError': True, 'Message': 'Enter project title'})

                    if category == '' or category is None:
                        return JsonResponse({'isError': True, 'Message': 'Select project category'})

                    if priority == '' or priority is None:
                        return JsonResponse({'isError': True, 'Message': 'Select project priority'})

                    if status == '' or status is None:
                        return JsonResponse({'isError': True, 'Message': 'Select project status'})

                    if start == '' or start is None:
                        return JsonResponse({'isError': True, 'Message': 'Enter project start date'})

                    if end == '' or end is None:
                        return JsonResponse({'isError': True, 'Message': 'Enter project end date'})

                    if manager == '' or manager is None:
                        return JsonResponse({'isError': True, 'Message': 'Enter project manager'})

                    if start >= end:
                        return JsonResponse({'isError': True, 'Message': "Start date must be less then the end date"})

                    if thumbnail == '' or thumbnail is None:
                        return JsonResponse({'isError': True, 'Message': f'Enter project thumbnail'})

                    # Check images extension
                    extention = thumbnail.name.split(".")[-1]
                    extention = extention.lower()
                    extension_types = ['jpg', 'jpeg', 'png']
                    x = " , ".join(extension_types)
                    if not extention in extension_types:
                        return JsonResponse({'isError': True, 'Message': f"This field only supports {x}"})

                    if thumbnail.size > 2621440:
                        return JsonResponse({'isError': True, 'Message': thumbnail.name+'  file is more than 2mb size'})

                    category = models.Category.objects.get(id=category)
                    manager = user_models.Users.objects.get(id=manager)

                    user = models.Project.objects.all()

                    if len(user) > 0:
                        projectID = user[0].projectID
                        serial = int(projectID[2:])
                    else:
                        serial = 0
                    projectID = generateSerialNumber('PR', serial)
                    save_project = models.Project(projectID=projectID,
                                                  title=title, category=category, manager=manager, priority=priority, is_active=True if status == 'Active' else False, start=start, end=end, thumbnail=thumbnail, created_by=request.user)

                    save_project.save()

                    # Send notification
                    msg = f"Project of {save_project.title} has been assigned to you by {request.user.get_full_name()}"
                    models.Notifications.save_notification(
                        'Project', manager, save_project.id, msg, 'ri-projector-fill')

                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Project Module / Project"
                    action = f'Created New Project ( {save_project.title} ) by {request.user.first_name}'
                    sendTrials(request, username, names,
                               avatar, action, module)
                    return JsonResponse({'isError': False, 'Message': "Project has been created successfully"}, status=200)

                else:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

        elif id == 'change-manager':
            if request.method == 'POST':
                if not request.user.is_client and request.user.has_perm('Projects.change_project'):
                    user = request.POST.get('user')
                    project = request.POST.get('project')

                    # Check if data is valid
                    if user == '' or user is None or user == 'undefined':
                        return JsonResponse({'isError': True, 'Message': 'Enter project manager'})

                    update_project = models.Project.objects.get(
                        projectID=project)
                    user = user_models.Users.objects.get(id=int(user))
                    prev_manager = update_project.manager
                    update_project.manager = user
                    update_project.save()

                    if prev_manager.id != user.id:
                        # Send notification
                        msg = f"Project of {update_project.title} has been removed from you by {request.user.get_full_name()}"
                        models.Notifications.save_notification(
                            'Project', prev_manager, update_project.id, msg, 'ri-projector-fill')

                        # Send notification
                        msg = f"Project of {update_project.title} has been assigned to you by {request.user.get_full_name()}"
                        models.Notifications.save_notification(
                            'Project', user, update_project.id, msg, 'ri-projector-fill')

                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Project Module / Project"
                    action = f'Updated Project Manager ( {update_project.title} ) by {request.user.first_name}'
                    sendTrials(request, username, names,
                               avatar, action, module)
                    return JsonResponse({'isError': False, 'Message': "Project manager has been updated successfully"}, status=200)

                else:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

        else:
            if request.method == 'GET':
                if not request.user.has_perm('Projects.view_project'):
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

                project = models.Project.objects.get(projectID=id)
                # 2022-11-30T13:00

                return JsonResponse({'isError': False, 'Message': {
                    'projectID': project.projectID,
                    'title': project.title,
                    'start': beautify_time(project.start),
                    'end':  beautify_time(project.end),
                    'category': project.category.id,
                    'priority': project.priority,
                    'status': 'Active' if project.is_active else 'Inactive',
                    'manager': {
                        'id': project.manager.id,
                        'name': f"{project.manager.username} - {project.manager.first_name} {project.manager.last_name}({project.manager.getUserType()})"
                    }

                }})

            if request.method == 'POST':
                if not request.user.is_client and request.user.has_perm('Projects.change_project'):
                    title = request.POST.get('title')
                    category = request.POST.get('category')
                    priority = request.POST.get('priority')
                    status = request.POST.get('status')
                    start = request.POST.get('start')
                    end = request.POST.get('end')
                    manager = request.POST.get('manager')

                    # Check if data is valid
                    if title == '' or title is None:
                        return JsonResponse({'isError': True, 'Message': 'Enter project title'})

                    if category == '' or category is None:
                        return JsonResponse({'isError': True, 'Message': 'Select project category'})

                    if priority == '' or priority is None:
                        return JsonResponse({'isError': True, 'Message': 'Select project priority'})

                    if status == '' or status is None:
                        return JsonResponse({'isError': True, 'Message': 'Select project status'})

                    if start == '' or start is None:
                        return JsonResponse({'isError': True, 'Message': 'Enter project start date'})

                    if end == '' or end is None:
                        return JsonResponse({'isError': True, 'Message': 'Enter project end date'})

                    if manager == '' or manager is None:
                        return JsonResponse({'isError': True, 'Message': 'Enter project manager'})

                    if start >= end:
                        return JsonResponse({'isError': True, 'Message': "Start date must be less then the end date"})

                    category = models.Category.objects.get(id=category)
                    manager = user_models.Users.objects.get(id=manager)

                    update_project = models.Project.objects.get(projectID=id)
                    update_project.category = category
                    update_project.manager = manager
                    update_project.title = title
                    update_project.start = start
                    update_project.end = end
                    update_project.priority = priority
                    update_project.is_active = True if status == 'Active' else False
                    update_project.save()

                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Project Module / Project"
                    action = f'Updated Project ( {update_project.title} ) by {request.user.first_name}'
                    sendTrials(request, username, names,
                               avatar, action, module)
                    return JsonResponse({'isError': False, 'Message': "Project has been updated successfully"}, status=200)

                else:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

            if request.method == 'DELETE':
                if not request.user.has_perm('Projects.delete_project'):
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

                project = models.Project.objects.get(projectID=id)

                checkTask = models.Task.objects.filter(
                    projectID=project.id, is_delete=False).exists()
                checkNote = models.ProjectNote.objects.filter(
                    projectID=project.id, is_delete=False).exists()
                checkfile = models.ProjectFile.objects.filter(
                    projectID=project.id, is_delete=False).exists()

                if checkTask or checkNote or checkfile:
                    return JsonResponse({'isError': True, 'Message': 'Cannot delete some instances of model because they are referenced through restricted foreign keys'}, status=200)

                project.is_delete = True
                project.save()

                username = request.user.username
                names = request.user.first_name + ' ' + request.user.last_name
                avatar = str(request.user.avatar)
                module = "Project Module / Project"
                action = f'Delete Project ( {project.title} ) by {request.user.first_name}'
                sendTrials(request, username, names,
                           avatar, action, module)
                return JsonResponse({'isError': False, 'Message': "Project has been deleted successfully"})

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
def ManageProjectFiles(request, id):
    try:
        if id == 0:
            if request.method == 'POST':
                project = request.POST.get('project')
                project = models.Project.objects.get(projectID=project)

                is_granted = False
                # if the user is admin and has the view project rule
                if request.user.is_admin or request.user.is_superuser and request.user.has_perm('Projects.add_projectfile'):
                    is_granted = True

                # If the user is agent is the manager
                if request.user.is_admin and project.manager.id == request.user.id and request.user.has_perm('Projects.project_visibility'):
                    is_granted = True

                if is_granted:
                    title = request.POST.get('title')
                    project = request.POST.get('project')
                    thumbnail = request.FILES.get('file')

                    # Check if data is valid
                    if title == '' or title is None:
                        return JsonResponse({'isError': True, 'Message': 'Enter project title'})

                    if thumbnail == '' or thumbnail is None:
                        return JsonResponse({'isError': True, 'Message': f'Enter project thumbnail'})

                    # Check images extension
                    extention = thumbnail.name.split(".")[-1]
                    extention = extention.lower()

                    extension_types = ['jpg', 'png', 'jpeg', 'doc',
                                       'docx', 'ppt', 'pptx', 'pdf', 'txt', 'xlsx']
                    x = " , ".join(extension_types)

                    if not extention in extension_types:
                        return JsonResponse({'isError': True, 'Message': f"This field only supports {x}"})

                    if thumbnail.size > 2621440:
                        return JsonResponse({'isError': True, 'Message': thumbnail.name+'  file is more than 2mb size'})

                    thumbnail.name = f"{request.user.username}-" + \
                        remove_non_ascii_2(thumbnail.name)

                    save_project_file = models.ProjectFile(
                        projectID=project, file=thumbnail, title=title)
                    save_project_file.save()

                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Project Module / Project"
                    action = f'Created New Project File ( {save_project_file.title} ) by {request.user.first_name}'
                    sendTrials(request, username, names,
                               avatar, action, module)
                    return JsonResponse({'isError': False, 'Message': "Project file has been created successfully"}, status=200)

                else:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

        else:
            if request.method == 'GET':
                project = models.ProjectFile.objects.get(id=id).projectID

                is_granted = False
                # if the user is admin and has the view project rule
                if request.user.is_admin or request.user.is_superuser and request.user.has_perm('Projects.change_projectfile'):
                    is_granted = True

                # If the user is agent is the manager
                if request.user.is_admin and project.manager.id == request.user.id and request.user.has_perm('Projects.project_visibility'):
                    is_granted = True

                if not is_granted:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

                project = models.ProjectFile.objects.get(id=id)
                # 2022-11-30T13:00

                return JsonResponse({'isError': False, 'Message': {
                    'id': project.id,
                    'title': project.title,
                }})

            if request.method == 'POST':
                project = models.ProjectFile.objects.get(id=id).projectID

                is_granted = False
                # if the user is admin and has the view project rule
                if request.user.is_admin or request.user.is_superuser and request.user.has_perm('Projects.change_projectfile'):
                    is_granted = True

                # If the user is agent is the manager
                if request.user.is_admin and project.manager.id == request.user.id and request.user.has_perm('Projects.project_visibility'):
                    is_granted = True

                if is_granted:
                    title = request.POST.get('title')

                    # Check if data is valid
                    if title == '' or title is None:
                        return JsonResponse({'isError': True, 'Message': 'Enter project title'})

                    update_project = models.ProjectFile.objects.get(id=id)
                    update_project.title = title
                    update_project.save()

                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Project Module / Project"
                    action = f'Updated Project File ( {update_project.title} ) by {request.user.first_name}'
                    sendTrials(request, username, names,
                               avatar, action, module)
                    return JsonResponse({'isError': False, 'Message': "Project file has been updated successfully"}, status=200)

                else:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

            if request.method == 'DELETE':
                project = models.ProjectFile.objects.get(id=id).projectID

                is_granted = False
                # if the user is admin and has the view project rule
                if request.user.is_admin or request.user.is_superuser and request.user.has_perm('Projects.delete_projectfile'):
                    is_granted = True

                # If the user is agent is the manager
                if request.user.is_admin and project.manager.id == request.user.id and request.user.has_perm('Projects.project_visibility'):
                    is_granted = True

                if not is_granted:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

                project_file = models.ProjectFile.objects.get(id=id)
                project_file.is_delete = True
                project_file.save()

                username = request.user.username
                names = request.user.first_name + ' ' + request.user.last_name
                avatar = str(request.user.avatar)
                module = "Project Module / Project"
                action = f'Delete Project FIle ( {project_file.title} ) by {request.user.first_name}'
                sendTrials(request, username, names,
                           avatar, action, module)
                return JsonResponse({'isError': False, 'Message': "Project file has been deleted successfully"})

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
def ManageProjectNotes(request, id):
    try:
        if id == 0:
            if request.method == 'POST':
                project = request.POST.get('project')
                project = models.Project.objects.get(projectID=project)

                is_granted = False
                # if the user is admin and has the view project rule
                if request.user.is_admin or request.user.is_superuser and request.user.has_perm('Projects.add_projectnote'):
                    is_granted = True

                # If the user is agent is the manager
                if request.user.is_admin and project.manager.id == request.user.id and request.user.has_perm('Projects.project_visibility'):
                    is_granted = True

                if is_granted:
                    note = request.POST.get('note')

                    # Check if data is valid
                    if note == '' or note is None:
                        return JsonResponse({'isError': True, 'Message': 'Enter your note'})

                    user = models.ProjectNote.objects.filter(
                        projectID=project.id)

                    if len(user) > 0:
                        noteID = user[0].noteID
                        serial = int(noteID[2:])
                    else:
                        serial = 0
                    noteID = generateSerialNumber('NT', serial)
                    save_project_note = models.ProjectNote(
                        projectID=project,  note=note, noteID=noteID)
                    save_project_note.save()

                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Project Module / Project Note"
                    action = f'Created New Project Note ( {save_project_note.get_short_notes()} ) by {request.user.first_name}'
                    sendTrials(request, username, names,
                               avatar, action, module)
                    return JsonResponse({'isError': False, 'Message': "Project note has been created successfully"}, status=200)
                else:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)
        else:
            if request.method == 'GET':
                project = models.ProjectNote.objects.get(id=id)

                is_granted = False
                # if the user is admin and has the view project rule
                if request.user.is_admin or request.user.is_superuser and request.user.has_perm('Projects.change_projectnote'):
                    is_granted = True

                # If the user is agent is the manager
                if request.user.is_admin and project.projectID.manager.id == request.user.id and request.user.has_perm('Projects.project_visibility'):
                    is_granted = True

                if not is_granted:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

                return JsonResponse({'isError': False, 'Message': {
                    'id': project.id,
                    'note': project.note,
                }})

            if request.method == 'POST':
                project = request.POST.get('project')
                project = models.Project.objects.get(projectID=project)

                is_granted = False
                # if the user is admin and has the view project rule
                if request.user.is_admin or request.user.is_superuser and request.user.has_perm('Projects.change_projectnote'):
                    is_granted = True

                # If the user is agent is the manager
                if request.user.is_admin and project.manager.id == request.user.id and request.user.has_perm('Projects.project_visibility'):
                    is_granted = True

                if is_granted:
                    note = request.POST.get('note')
                    project = request.POST.get('project')

                    # Check if data is valid
                    if note == '' or note is None:
                        return JsonResponse({'isError': True, 'Message': 'Enter project note'})

                    update_project_note = models.ProjectNote.objects.get(id=id)
                    update_project_note.note = note
                    update_project_note.save()

                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    module = "Project Module / Project"
                    action = f'Updated Project Note ( {update_project_note.get_short_notes()} ) by {request.user.first_name}'
                    sendTrials(request, username, names,
                               avatar, action, module)
                    return JsonResponse({'isError': False, 'Message': "Project note has been updated successfully"}, status=200)

                else:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

            if request.method == 'DELETE':
                project_note = models.ProjectNote.objects.get(id=id)

                is_granted = False
                # if the user is admin and has the view project rule
                if request.user.is_admin or request.user.is_superuser and request.user.has_perm('Projects.delete_projectnote'):
                    is_granted = True

                # If the user is agent is the manager
                if request.user.is_admin and project_note.projectID.manager.id == request.user.id and request.user.has_perm('Projects.project_visibility'):
                    is_granted = True

                if not is_granted:
                    message = {
                        'isError': True,
                        'Message': '401-Unauthorized access.you do not have permission to access this page.'
                    }
                    return JsonResponse(message, status=200)

                project_note.is_delete = True
                project_note.save()

                username = request.user.username
                names = request.user.first_name + ' ' + request.user.last_name
                avatar = str(request.user.avatar)
                module = "Project Module / Project"
                action = f'Delete Project Note ( {project_note.get_short_notes} ) by {request.user.first_name}'
                sendTrials(request, username, names,
                           avatar, action, module)
                return JsonResponse({'isError': False, 'Message': "Project note has been deleted successfully"})

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


def generateSerialNumber(letter, serial):
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


def beautify_time(time):
    year = time.strftime('%Y')
    month = time.strftime('%m')
    day = time.strftime('%d')
    minute = time.strftime('%M')
    hour = int(time.strftime('%H')) + 3
    hour = f"0{hour}" if hour < 10 else str(hour)
    return f"{year}-{month}-{day}T{hour}:{minute}"


def ProjectsInformation(request, id):
    try:
        project = models.Project.objects.get(id=id)

        is_granted = False

        # If the user is agent is the manager
        if project.manager.id == request.user.id and request.user.has_perm('Projects.project_visibility'):
            is_granted = True

        # if the user is admin and has the view project rule
        if request.user.has_perm('Projects.view_project'):
            is_granted = True

        if is_granted:
            # Getting project's deadlines is today
            set_inactive_project_task()

            # Send message to the manager to tell him that his project has been visited
            if project.manager.id != request.user.id:
                msg = f"Your project  {project.title} has been viewed by {request.user.get_full_name()}"
                models.Notifications.save_notification(
                    'Project', project.manager, id, msg, 'ri-projector-fill')

            project = models.Project.objects.get(id=id)

            files = models.ProjectFile.objects.filter(
                projectID=id, is_delete=False)
            notes = models.ProjectNote.objects.filter(
                projectID=id, is_delete=False)

            tasks = models.Task.objects.filter(
                projectID__id=id, is_delete=False)

            context = {
                'Project': project,
                'Files': files,
                'Notes': notes,
                'Tasks': tasks,
            }
            return render(request, "Layout/Admin/Project/project-information.html", context)

        else:
            return render(request,  'Auth/404.html')

    except Exception as error:
        username = request.user.username
        name = request.user.first_name + ' ' + request.user.last_name
        message = sendException(
            request, username, name, error)
        return render(request, 'Auth/404.html')


def remove_non_ascii_2(string):
    return string.encode('ascii', errors='ignore').decode()


@login_required(login_url='Login')
def ManageComments(request, id):
    try:
        if id == '0':
            if request.method == 'POST':
                if request.user.has_perm('Projects.add_taskcomments'):
                    taskID = request.POST['taskID']
                    userID = request.POST['userID']
                    message = request.POST['message']

                    get_user = user_models.Users.objects.get(
                        id=userID, is_delete=False)

                    if request.user.is_admin or request.user.is_superuser:
                        get_task = models.AssignTask.objects.filter(
                            taskID__id=taskID, taskID__is_delete=False)
                        get_taskID = get_task[0]
                    else:
                        get_task = models.AssignTask.objects.get(
                            taskID__id=taskID, taskID__is_delete=False, is_accepted=True, is_assigned=True, is_removed=False)
                        get_taskID = get_task
                        if checkAssignedUserTask(taskID, get_user)['isError'] == True:
                            return JsonResponse(checkAssignedUserTask(taskID, get_user), status=200)

                    save_reply = models.TaskComments(
                        taskID=get_taskID.taskID, userID=get_user, message=message)
                    save_reply.save()

                    username = request.user.username
                    names = request.user.first_name + ' ' + request.user.last_name
                    avatar = str(request.user.avatar)
                    action = f"{get_user.first_name} {get_user.last_name} has posted comment on {get_taskID.taskID.title } ticket"
                    module = "Project Module / Task Comment"
                    sendTrials(request, username, names,
                               avatar, action, module)

                    if save_reply.taskID.projectID.manager.id != get_user.id:
                        # Send notification for the admin
                        msg = f"{get_user.get_full_name()} posted comment on {save_reply.taskID.title}"
                        models.Notifications.save_notification(
                            'Task', save_reply.taskID.projectID.manager, save_reply.taskID.id, msg, 'ri-task-line')
                    else:
                        get_assigned_user = models.AssignTask.objects.filter(
                            taskID=save_reply.taskID.id, is_accepted=True, is_assigned=True, is_removed=False)

                        if len(get_assigned_user) > 0:
                            get_assigned_user = get_assigned_user[0]
                            # Send notification for the admin
                            msg = f"{save_reply.taskID.projectID.manager.get_full_name()} posted comment on {save_reply.taskID.title}"
                            models.Notifications.save_notification(
                                'Task', get_assigned_user.userID, save_reply.taskID.id, msg, 'ri-task-line')

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


def checkAssignedUserTask(task_id, user):
    get_task = models.AssignTask.objects.get(
        taskID=task_id, taskID__is_delete=False, is_accepted=True, is_assigned=True, is_removed=False)
    get_user = user

    if get_user.is_agent and get_task.userID.id != get_user.id:
        return {'isError': True, 'Message': '401-Unauthorized access.you do not have permission to access this page.'}

    return {'isError': False, 'Message': 'Authorized user'}
