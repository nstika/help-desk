from Users import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout', views.Logout, name='Logout'),
    path('', views.Login, name='Login'),
    path('users/', include('Users.users_urls')),
    path('tickets/', include('Tickets.tickets_urls')),
    path('recycle/', include('RecycleBin.recycle_urls')),
    path('project/', include('Projects.project_urls')),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
