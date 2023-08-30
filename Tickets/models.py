from django.db import models
from datetime import datetime, timezone
import uuid
from Users.models import Users, Department
from django.urls import reverse

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=30, null=True, blank=True)
    created_at = models.DateTimeField(default=datetime.today)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_delete = models.BooleanField(default=False)

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

    class Meta:
        db_table = 'category'


class Tickets(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.TextField()
    image_file = models.FileField(
        null=True, blank=True, upload_to="TicketFiles/")
    status = models.CharField(max_length=50)
    priority = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT)
    userID = models.ForeignKey(Users, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(default=datetime.today)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(
        Users, on_delete=models.RESTRICT, null=True, blank=True, related_name='created_by_user')
    is_delete = models.BooleanField(default=False)

    class Meta:
        db_table = 'tickets'
        ordering = ['-ticket_number']
        permissions = [('change_status_ticket', 'Can change status tickets'),
                       ('change_priority_ticket', 'Can change priority tickets')]

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse('ViewTicketDetails', args=[str(self.id)])

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

    def checkImage(self):
        if self.image_file is None or self.image_file == '':
            return True
        return False

    def getImageDetails(self):
        if self.image_file is not None or self.image_file != '':
            file = self.image_file
            split_file = file.name.split('/')[-1].split('.')
            return {
                'size': pretty_size(file.size),
                'extension': split_file[1],
                'name': 'Ticket-Image.'
            }


# bytes pretty-printing
UNITS_MAPPING = [
    (1 << 50, ' PB'),
    (1 << 40, ' TB'),
    (1 << 30, ' GB'),
    (1 << 20, ' MB'),
    (1 << 10, ' KB'),
    (1, (' byte', ' bytes')),
]


def pretty_size(bytes, units=UNITS_MAPPING):
    for factor, suffix in units:
        if bytes >= factor:
            break
    amount = int(bytes / factor)

    if isinstance(suffix, tuple):
        singular, multiple = suffix
        if amount == 1:
            suffix = singular
        else:
            suffix = multiple
    return str(amount) + suffix


class AssignTicket(models.Model):
    userID = models.ForeignKey(Users, on_delete=models.RESTRICT)
    ticketID = models.ForeignKey(Tickets, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(default=datetime.today)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_accepted = models.BooleanField(default=False)
    is_removed = models.BooleanField(default=False)
    is_assigned = models.BooleanField(default=True)
    assigned_by = models.ForeignKey(
        Users, on_delete=models.RESTRICT, null=True, blank=True, related_name='assigned_by_user')

    class Meta:
        db_table = 'assign_ticket'

    def getStatus(self):
        if self.is_accepted:
            return "Accepted"

        if not self.is_accepted:
            return "Not Accepted"

        return "Unknow"


class ReplyTicket(models.Model):
    userID = models.ForeignKey(Users, on_delete=models.RESTRICT)
    ticketID = models.ForeignKey(Tickets, on_delete=models.RESTRICT)
    message = models.TextField()
    created_at = models.DateTimeField(default=datetime.today)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'reply_ticket'


def getCurrentDate():
    time = datetime.now(timezone.utc)
    return time


# Adding computer leases for tickets
class ComputerLease(models.Model):
    computer_tag = models.CharField(max_length=500, null=True, blank=True)
    full_name = models.CharField(max_length=500)
    username = models.CharField(max_length=500, null=True, blank=True)
    office_key = models.CharField(max_length=500, null=True, blank=True)
    office_type = models.CharField(max_length=500)
    windows_key = models.CharField(max_length=500 , null=True, blank=True)
    windows_type = models.CharField(max_length=500)
    location = models.CharField(max_length=500)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    bitlocker_recovery_keys = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(
        default=datetime.today, null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_delete = models.BooleanField(default=False)

    
    class Meta:
        db_table = 'computers'
        
        
    def get_full_name(self):
        if self.full_name is None:
            return 'N/A'
        
        return self.full_name
    
    
    def get_username(self):
        if self.username is None:
            return 'N/A'
        
        return self.username
    
    
    def get_created_date(self):
        timedelta = getCurrentDate() - self.created_at
        seconds = timedelta.days * 24 * 3600 + timedelta.seconds
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        if days > 29:
            return self.created_at

        if days > 0:
            return f"{days} {'day' if days == 1 else 'days'} ago"

        if hours > 0:
            return f"{hours} {'hour' if hours == 1 else 'hours'} ago"

        if minutes > 0:
            return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"

        return f"{seconds} {'second' if seconds == 1 else 'seconds'} ago"

    def get_modified_date(self):
        if getCurrentDate() > self.modified_at:
            timedelta = getCurrentDate() - self.modified_at
        else:
            timedelta = self.modified_at - getCurrentDate()
        
        seconds = timedelta.days * 24 * 3600 + timedelta.seconds
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        if days > 29:
            return self.modified_at

        if days > 0:
            return f"{days} {'day' if days == 1 else 'days'} ago"

        if hours > 0:
            return f"{hours} {'hour' if hours == 1 else 'hours'} ago"

        if minutes > 0:
            return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"

        return f"{seconds} {'second' if seconds == 1 else 'seconds'} ago"