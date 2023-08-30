from django.urls import path
from . import views

urlpatterns = [
    path('profile', views.Profile, name='Profile'),
    path('dashboard', views.Dashboard, name='Dashboard'),
    path('department', views.Department, name='Department'),
    path('position', views.Positions, name='Positions'),
    path('add_users', views.Users, name='Users'),
    path('user_lists', views.UsersList, name='UsersList'),
    path('agent_lists', views.AgentsList, name='AgentsList'),
    path('add_clients', views.Clients, name='Clients'),
    path('clients', views.ClientList, name='ClientList'),
    path('audit_trials', views.AuditTrials, name='AuditTrials'),
    path('error_logs', views.ErrorLogs, name='ErrorLogs'),
    # Data Managements
    path('manage_positions/<int:id>',
         views.ManagePosition, name='ManagePosition'),
    path('manage_departments/<int:id>',
         views.ManageDepartment, name='ManageDepartment'),
    path('manage_users/<int:id>',
         views.ManageUsers, name='ManageUsers'),
    path('change_password',
         views.ChangePassword, name='ChangePassword'),
    path('get_users_links', views.get_users_links),
    path('manage_error_log/<int:id>', views.ManageErrorLogs),

    # Roles
    path('user_roles_report', views.ViewUserRolesReportPage, name='UserRolesReport'),
    path('search_role', views.SearchRole, name='SearchRole'),
    path('roles_report', views.ViewRolesReportPage, name='RolesReport'),
    path('single_roles', views.ViewRolesPage, name='SingleRoles'),
    path('group_roles', views.ViewGroupRolesPage, name='GroupRoles'),
    path('manage_group', views.ViewManageGroupPage, name='ManageGroup'),
    path('edit_group/<int:group_id>', views.ViewEditGroupPage, name='EditGroup'),
    path('manage_permission/<str:id>',
         views.ManagePermission, name='ManageRoles'),
    path('manage_permission_report',
         views.PermissonReport, name='PermissonReport'),
    path('manage_group_permission/<str:id>/<str:_id>',
         views.ManageGroupPermission, name='ManageGroups'),
    path('manage_group/<str:id>',
         views.ManageGroup),
    path('rename_group',
         views.RenameGroup),

    path('search_engine/<str:search>/<str:type>', views.SearchEngine),
]
