import logging

import requests
from django.conf import settings
from django.views.debug import ExceptionReporter
from waffle import switch_is_active


class DiscordExceptionHandler(logging.Handler):
    def emit(self, record):
        if not switch_is_active('LOG_TO_DISCORD'):
            return

        try:
            request = record.request
            subject = '%s (%s IP): %s' % (
                record.levelname,
                ('internal' if request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS
                 else 'EXTERNAL'),
                record.getMessage()
            )
        except Exception:
            subject = '%s: %s' % (
                record.levelname,
                record.getMessage()
            )
            request = None

        subject = subject.replace('\n', '\\n').replace('\r', '\\r')

        if record.exc_info:
            exc_info = record.exc_info
        else:
            exc_info = (None, record.getMessage(), None)

        reporter = ExceptionReporter(request, *exc_info)
        data = reporter.get_traceback_data()

        location = f' at {request.path_info}' if request else ''
        heading = f"{data.get('exception_type', 'Report')}{location}"
        exception_value = data.get('exception_value', 'No exception message supplied')
        fields = [
            {
                'name': 'Subject',
                'value': subject,
                'inline': True
            },
            {
                'name': heading,
                'value': exception_value,
                'inline': False
            },

        ]

        if request:
            if request.GET != {}:
                fields.append({
                    'name': 'GET parameters',
                    'value': str(dict(request.GET)),
                    'inline': False
                })
            if request.POST != {}:
                fields.append({
                    'name': 'POST parameters',
                    'value': str(dict(request.POST)),
                    'inline': False
                })

        json = {
            'embeds': [{
                'title': 'SC2 Ladder Exception',
                'fields': fields,
                'footer': {
                    'text': ''
                }
            }]
        }

        requests.post(settings.DISCORD_WEBHOOK, json=json)
