from django.urls import path
from . import views

urlpatterns = [
    path('manage_tasks/<str:id>', views.ManageTasks, name='ManageTasks'),
    path('tasks', views.Tasks, name='tasks'),
    path('notifications', views.Notifications, name='Notifications'),
    path('AgentTasks', views.AgentTasks, name='AgentTasks'),
    path('projects', views.Projects, name='projects'),
    path('manager_projects', views.ManagerProjects, name='ManagerProjects'),
    path('project-information/<str:id>',
         views.ProjectsInformation, name='project-information'),
    path('task-details/<str:ids>',
         views.ViewTaskDetails, name='task-details'),
    path('manage_project/<str:id>', views.ManageProject),
    path('manage_project_attachments/<int:id>', views.ManageProjectFiles),
    path('manage_task_attachments/<int:id>', views.ManageTaskFiles),
    path('manage_task_notes/<int:id>', views.ManageTaskNotes),
    path('manage_project_notes/<int:id>', views.ManageProjectNotes),
    path('assign_task/<int:ids>', views.ManageAssignTask,
         name='ManageAssignTask'),
    path('task_progress/<int:id>', views.ManageTaskProgress,
         name='ManageTaskProgress'),
    path('manage_comments/<str:id>', views.ManageComments, name='ManageComments'),
]
