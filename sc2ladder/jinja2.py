from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.utils import timezone
from jinja2 import Environment


def updated_ago(mod_time):
    d = timezone.now() - mod_time
    if d.days > 1:
        return f"{d.days} days ago"
    elif d.days == 1:
        return "1 day ago"
    elif d.seconds > 7200:
        return f"{int(d.seconds/3600)} hours ago"
    elif d.seconds > 3600:
        return "1 hour ago"
    elif d.seconds > 120:
        return f"{int(d.seconds/60)} minutes ago"
    elif d.seconds > 60:
        return "1 minute ago"
    else:
        return f"{d.seconds} seconds ago"


def environment(**options):
    env = Environment(**options)
    env.globals.update(
        {"static": staticfiles_storage.url, "url": reverse, "updated_ago": updated_ago}
    )
    return env
