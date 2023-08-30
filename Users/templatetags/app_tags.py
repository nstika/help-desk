from django import template
register = template.Library()
from Projects.models import Notifications

@register.simple_tag
def fatch_badge_notications(user , type):
    return Notifications.fatch_badge_notication(user)[type]


@register.simple_tag
def fatch_list_notications(user , type):
    return Notifications.fatch_notications(user , type)
