import uuid
from django.db import models
from Tickets.models import Category
from datetime import date, datetime, timezone
from django.urls import reverse
from django.db.models import Sum


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    projectID = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT)
    priority = models.CharField(max_length=50)
    manager = models.ForeignKey('Users.Users', on_delete=models.RESTRICT)
    start = models.DateTimeField()
    end = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    thumbnail = models.FileField(upload_to="projects/thumbnails/")
    is_delete = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        'Users.Users', on_delete=models.RESTRICT,  related_name='created_by_project_user')
    created_at = models.DateTimeField(default=datetime.today)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'project'
        ordering = ['-projectID']
        permissions = [
            ('project_visibility', 'Manager can view their assigned projects')
        ]

    def set_inactive(self):
        self.is_active = False
        self.save()

    def calculate_remaining_days(self):
        timedelta = self.end - getCurrentDate()
        seconds = timedelta.days * 24 * 3600 + timedelta.seconds
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        if self.end < getCurrentDate():
            return "Deadline End"

        if days > 0:
            return f"{days} {'day' if days == 1 else 'days'}"

        if hours > 0:
            return f"{hours} {'hour' if hours == 1 else 'hours'}"

        if minutes > 0:
            return f"{minutes} {'minute' if minutes == 1 else 'minutes'}"

        return f"{seconds} {'second' if seconds == 1 else 'seconds'}"

    def getprojectSummary(self):
        # This thing was created yesterday, it's called raja, the time it was meant to be completed is over, the time to be completed is east.
        summary = f"This project was created at {beautify_time(self.created_at)}, "

        if self.end < getCurrentDate():
            summary += "the time it was meant to be completed is over."
            return summary

        summary += f"the time to be completed is {beautify_time(self.end)}, and there are {self.calculate_remaining_days()} left"
        return summary

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

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse('project-information', args=[str(self.id)])


class ProjectNote(models.Model):
    noteID = models.CharField(max_length=100, null=True, blank=True)
    note = models.TextField()
    projectID = models.ForeignKey(Project, on_delete=models.RESTRICT)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.today)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['-noteID']
        db_table = 'project_note'

    def get_short_notes(self):
        return self.note if len(self.note) <= 10 else f"{self.note[0:10]}....."


class ProjectFile(models.Model):
    title = models.CharField(max_length=500, null=True, blank=True)
    projectID = models.ForeignKey(Project, on_delete=models.RESTRICT)
    file = models.FileField(upload_to="projects/files/")
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.today)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'project_file'

    def getImageDetails(self):
        if self.file is not None or self.file != '':
            file = self.file
            split_file = file.name.split('/')[-1].split('.')

            icon = 'ri-file-list-line'
            color = 'primary'

            if split_file[1].lower() == 'pdf':
                icon = 'ri-file-pdf-line'
                color = 'danger'

            if split_file[1].lower() == 'ppt' or split_file[1].lower() == 'pptx':
                icon = 'ri-file-ppt-2-line'
                color = 'danger'

            if split_file[1].lower() == 'doc' or split_file[1].lower() == 'docx':
                icon = 'ri-file-word-2-line'
                color = 'secondary'

            if split_file[1].lower() == 'png' or split_file[1].lower() == 'jpg' or split_file[1].lower() == 'jpeg':
                icon = 'ri-image-2-fill'
                color = 'success'

            if split_file[1].lower() == 'txt':
                icon = 'ri-file-text-line'
                color = 'dark'

            if split_file[1].lower() == 'xlsx':
                icon = 'ri-file-excel-2-line'
                color = 'success'

            return {
                'size': pretty_size(file.size),
                'extension': split_file[1].upper(),
                'name': 'Ticket-Image.',
                'icon': icon,
                'color': color,
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


def beautify_time(time):
    year = time.strftime('%Y')
    month = time.strftime('%m')
    day = time.strftime('%d')
    minute = time.strftime('%M')
    hour = int(time.strftime('%H'))
    hour = f"0{hour}" if hour < 10 else str(hour)
    return f"{year}-{month}-{day} {hour}:{minute}"


# Task
class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_number = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.RESTRICT)
    projectID = models.ForeignKey(Project, on_delete=models.RESTRICT)
    status = models.CharField(max_length=50)
    priority = models.CharField(max_length=50)
    start = models.DateField()
    end = models.DateField()
    document = models.FileField(upload_to="projects/tasks/documents/")
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.today)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'task'
        ordering = ['-task_number']

        permissions = [
            ('change_priority_task', 'Can change priority tasks')]

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse('task-details', args=[str(self.id)])

    def calculate_remaining_days(self):

        timedelta = self.end - getCurrentDate(is_datetime=False)
        seconds = timedelta.days * 24 * 3600 + timedelta.seconds
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        if self.end < getCurrentDate(is_datetime=False):
            return "Deadline End"

        if days > 0:
            return f"{days} {'day' if days == 1 else 'days'}"
        return "Deadline is to today"

    def set_inactive(self):
        self.is_active = False
        self.save()

    def get_progress(self):
        progress = TaskProgess.objects.filter(
            taskID=self.id, is_delete=False).aggregate(Sum('work_completion'))['work_completion__sum']

        if progress is None:
            return 0

        return int(progress)

    def get_assigned_user(self):
        assigned_user = AssignTask.objects.filter(
            taskID=self.id, is_assigned=True, is_accepted=True)

        if len(assigned_user) == 0:
            return '---'

        return assigned_user[0]

    def get_last_progress_date(self):
        last_progress_date = TaskProgess.objects.filter(
            taskID=self.id).order_by('-created_at')

        if len(last_progress_date) == 0:
            return '---'

        return last_progress_date[0].get_created_date()

    def get_attachments(self):
        files = TaskFile.objects.filter(
            taskID=self.id, is_delete=False).count()

        return int(files) if files > 10 else f"0{files}"

    def get_notes(self):
        notes = TaskNote.objects.filter(
            taskID=self.id, is_delete=False).count()

        return int(notes) if notes > 10 else f"0{notes}"

    def get_comments(self):
        comments = TaskComments.objects.filter(
            taskID=self.id).count()

        return int(comments) if comments > 10 else f"0{comments}"

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


class AssignTask(models.Model):
    userID = models.ForeignKey('Users.Users', on_delete=models.RESTRICT)
    taskID = models.ForeignKey(Task, on_delete=models.RESTRICT)
    is_accepted = models.BooleanField(default=False)
    is_removed = models.BooleanField(default=False)
    is_assigned = models.BooleanField(default=False)
    assigned_by = models.ForeignKey(
        'Users.Users', on_delete=models.RESTRICT, null=True, blank=True, related_name='assigned_task_by_user')
    created_at = models.DateTimeField(default=datetime.today)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'assign_task'


class TaskNote(models.Model):
    note = models.TextField()
    noteID = models.CharField(max_length=100, null=True, blank=True)
    userID = models.ForeignKey('Users.Users', on_delete=models.RESTRICT)
    taskID = models.ForeignKey(Task, on_delete=models.RESTRICT)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.today)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'task_note'
        ordering = ['-noteID']

    def get_short_notes(self):
        return self.note if len(self.note) <= 10 else f"{self.note[0:10]}....."


class TaskFile(models.Model):
    title = models.CharField(max_length=500, null=True, blank=True)
    taskID = models.ForeignKey(Task, on_delete=models.RESTRICT)
    file = models.FileField(upload_to="projects/taks/files/")
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.today)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'task_file'

    def getImageDetails(self):
        if self.file is not None or self.file != '':
            file = self.file
            split_file = file.name.split('/')[-1].split('.')

            icon = 'ri-file-list-line'
            color = 'primary'

            if split_file[1].lower() == 'pdf':
                icon = 'ri-file-pdf-line'
                color = 'danger'

            if split_file[1].lower() == 'ppt' or split_file[1].lower() == 'pptx':
                icon = 'ri-file-ppt-2-line'
                color = 'danger'

            if split_file[1].lower() == 'doc' or split_file[1].lower() == 'docx':
                icon = 'ri-file-word-2-line'
                color = 'secondary'

            if split_file[1].lower() == 'png' or split_file[1].lower() == 'jpg' or split_file[1].lower() == 'jpeg':
                icon = 'ri-image-2-fill'
                color = 'success'

            if split_file[1].lower() == 'txt':
                icon = 'ri-file-text-line'
                color = 'dark'

            if split_file[1].lower() == 'xlsx':
                icon = 'ri-file-excel-2-line'
                color = 'success'

            return {
                'size': pretty_size(file.size),
                'extension': split_file[1].upper(),
                'name': 'Ticket-Image.',
                'icon': icon,
                'color': color,
            }


class TaskProgess(models.Model):
    taskID = models.ForeignKey(Task, on_delete=models.RESTRICT)
    description = models.TextField()
    work_completion = models.FloatField()
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.today)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'task_progress'

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


class TaskComments(models.Model):
    userID = models.ForeignKey('Users.Users', on_delete=models.RESTRICT)
    taskID = models.ForeignKey(Task, on_delete=models.RESTRICT)
    message = models.TextField()
    created_at = models.DateTimeField(default=datetime.today)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'task_comments'

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


def getCurrentDate(is_datetime=True):
    if is_datetime:
        time = datetime.now(timezone.utc)
    else:
        time = date.today()
    return time


class Notifications(models.Model):
    icon = models.CharField(max_length=100 , null=True, blank=True)
    type = models.CharField(max_length=100)
    message = models.TextField()
    projectID = models.ForeignKey(
        Project, null=True, blank=True, on_delete=models.RESTRICT)
    taskID = models.ForeignKey(
        Task, null=True, blank=True, on_delete=models.RESTRICT)
    ticketID = models.ForeignKey(
        'Tickets.Tickets', null=True, blank=True, on_delete=models.RESTRICT)
    userID = models.ForeignKey('Users.Users', on_delete=models.RESTRICT)
    is_delete = models.BooleanField(default=False)
    is_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.today)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at', 'userID']

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

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse('Notifications')

    @classmethod
    def save_notification(cls, type, user, source, message , icon):
        ticketID = None
        taskID = None
        projectID = None

        if type == 'Project':
            projectID = Project.objects.get(id=source)

        if type == 'Task':
            taskID = Task.objects.get(id=source)

        if type == 'Ticket':
            # ticketID = Tickets.objects.get(id=source)
            pass

        new_notification = cls(type=type, userID=user, message=message,
                               projectID=projectID, taskID=taskID, ticketID=ticketID , icon = icon)

        new_notification.save()

    @classmethod
    def make_seen(cls, user):
        unseen_notifications = cls.objects.filter(
            userID=user, is_seen=False, is_delete=False)

        for index, item in enumerate(unseen_notifications):
            item.is_seen = True
            item.save()

    @classmethod
    def fatch_badge_notication(cls,user):
        return {
            'All': cls.objects.filter(userID=user , is_seen=False , is_delete=False).count(),
            'Project': cls.objects.filter(userID=user , type ='Project' ,is_seen=False , is_delete=False).count(),
            'Task': cls.objects.filter(userID=user , type ='Task' ,is_seen=False , is_delete=False).count(),
            'Ticket': cls.objects.filter(userID=user , type ='Ticket' ,is_seen=False , is_delete=False).count(),
        }

    @classmethod
    def fatch_notications(cls, user , type):
        if type == 'All':
            return cls.objects.filter(userID=user, is_seen=False, is_delete=False)[0:5]

        return cls.objects.filter(userID=user, type=type, is_seen=False, is_delete=False)[0:5]
