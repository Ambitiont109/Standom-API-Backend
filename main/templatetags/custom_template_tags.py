from django import template
from django.urls import reverse
from main.models import User, Campaign

register = template.Library()


@register.simple_tag
def navactive(request, urls):
    if request.path in (reverse(url) for url in urls.split()):
        return "active"
    return ""


@register.simple_tag
def getUserCount():
    return User.objects.exclude(is_superuser=True).count()


@register.simple_tag
def getCampaignCount():
    return Campaign.objects.all().count()
