import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
import sys
import traceback
import httpagentparser

# Create your models here.


class Department(models.Model):
    dept_name = models.CharField(
        unique=True, max_length=50,)
    created_at = models.DateTimeField(default=datetime.datetime.today)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_delete = models.BooleanField(default=False)

    class Meta:
        db_table = 'departments'


class Position(models.Model):
    position_name = models.CharField(
        unique=True, max_length=100)
    created_at = models.DateTimeField(default=datetime.datetime.today)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_delete = models.BooleanField(default=False)

    class Meta:
        db_table = 'positions'


class Users(AbstractUser):

    email = models.EmailField(
        unique=True)
    gender = models.CharField(max_length=12)
    phone = models.CharField(max_length=25, unique=True, null=True,
                             )
    department = models.ForeignKey(
        Department, on_delete=models.RESTRICT, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.RESTRICT, null=True, blank=True
                                 )
    created_at = models.DateTimeField(default=datetime.datetime.today)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_agent = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    avatar = models.FileField(upload_to="avatars/")
    is_delete = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ['-username']
        db_table = "users"
        permissions = [
            ('change_password', "Can change user's passwprd"),
            ('add_client', "Can add client"),
            ('delete_client', "Can  client"),
            ('change_client', "Can add client"),
            ('view_client', "Can add client"),
            ('add_agent', "Can add agent"),
            ('delete_agent', "Can  agent"),
            ('change_agent', "Can add agent"),
            ('view_agent', "Can add agent"),
            ('manage_role_groups', 'Can Add Or Delete Role From The Group'),
            ('remove_role_from_group', 'Can Remove Role From Group'),
            ('assign_user_to_group', 'Can Assign User To Group'),
            ('role_report', 'Can See Roles Report'),
        ]

    def getModifedDate(self):
        if self.modified_at is None:
            return 'No Modified Date'
        else:
            return self.modified_at

    def getUserType(self):
        if self.is_superuser:
            return "Superuser"

        if self.is_admin:
            return "Admin"

        if self.is_agent:
            return "Agent"

        if self.is_client:
            return "Client"

        return "Anonymous"

    @classmethod
    def create_user(cls, fname, lname, email, phone, gender,  position, department, image, is_admins, is_agents, is_clients, is_supers, request):
        try:
            phone = None if phone == '' or phone == None or phone == 'null' else phone
            username = generateUsername(
                is_admins, is_agents, is_clients, is_supers)
            Positions = Position.objects.get(
                id=position)
            Departmentss = Department.objects.get(
                id=department)
            Users = cls(first_name=fname.strip(), last_name=lname.strip(), username=username,
                        phone=phone, gender=gender, email=email, position=Positions, department=Departmentss,
                        avatar=image, is_admin=is_admins, is_agent=is_agents, is_client=is_clients, is_superuser=is_supers
                        )
            Users.set_password('Help123')
            Users.save()

            return cls.sendMessage(False, 'New user has been created')
        except Exception as error:
            username = request.user.username
            name = request.user.first_name + ' ' + request.user.last_name
            message = sendException(
                request, username, name, error)
            return cls.sendMessage(True, 'On Error Occurs . Please try again or contact system administrator')

    @classmethod
    def sendMessage(cls, error, msg):
        return {
            'isError': error,
            'Message': msg
        }

    def get_modified_date(self):
        timedelta = getCurrentDate() - self.modified_at
        seconds = timedelta.days * 24 * 3600 + timedelta.seconds
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        if days > 0:
            return f"{days} {'day' if days == 1 else 'days'} ago"

        if hours > 0:
            return f"{hours} {'hour' if hours == 1 else 'hours'} ago"

        if minutes > 0:
            return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"

        return f"{seconds} {'second' if seconds == 1 else 'seconds'} ago"


# Generating username for each user by counting from the last username
def generateUsername(is_admins, is_agents, is_clients, is_supers):
    user = ''
    letter = ''
    if is_supers or is_admins:
        letter = 'AD'
        user = Users.objects.filter(Q(is_superuser=True) | Q(is_admin=True))
    elif is_clients:
        letter = 'CL'
        user = Users.objects.filter(is_client=True)
    elif is_agents:
        letter = 'AG'
        user = Users.objects.filter(is_agent=True)

    if len(user) > 0:
        username = user[0].username
        serial = int(username[2:])
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


class ErrorLogs(models.Model):
    Username = models.CharField(max_length=20)
    Name = models.CharField(max_length=500)
    Expected_error = models.CharField(max_length=500)
    field_error = models.CharField(max_length=500)
    trace_back = models.TextField(max_length=500)
    line_number = models.IntegerField()
    date_recorded = models.DateTimeField(default=datetime.datetime.today)
    browser = models.CharField(max_length=500)
    ip_address = models.CharField(max_length=500)
    user_agent = models.TextField(max_length=500)
    Avatar = models.FileField(upload_to="errorlogs/", null=True, blank=True)

    class Meta:
        db_table = 'errorlogs'


class AuditTrials(models.Model):
    Avatar = models.FileField(upload_to="trials/")
    Username = models.CharField(max_length=20)
    Name = models.CharField(max_length=200)
    Actions = models.CharField(max_length=400)
    Module = models.CharField(max_length=400)
    date_of_action = models.DateTimeField(default=datetime.datetime.today)
    operating_system = models.CharField(max_length=200)
    browser = models.CharField(max_length=200)
    ip_address = models.CharField(max_length=200)
    user_agent = models.TextField(max_length=200)

    class Meta:
        db_table = 'audittrials'

    def reduceActions(self):
        return f"{self.Actions[:217]}..." if len(self.Actions) > 217 else self.Actions


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
    error_logs = ErrorLogs(
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


def getCurrentDate():
    time = datetime.datetime.now(datetime.timezone.utc)
    return time
