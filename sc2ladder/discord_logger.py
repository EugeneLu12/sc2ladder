import logging

import requests
from django.conf import settings
from django.views.debug import ExceptionReporter
from waffle import flag_is_active


class DiscordExceptionHandler(logging.Handler):
    def emit(self, record):
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

        if not flag_is_active(request, 'LOG_TO_DISCORD'):
            return

        subject = subject.replace('\n', '\\n').replace('\r', '\\r')

        if record.exc_info:
            exc_info = record.exc_info
        else:
            exc_info = (None, record.getMessage(), None)

        reporter = ExceptionReporter(request, *exc_info)
        data = reporter.get_traceback_data()
        requests.post(settings.DISCORD_WEBHOOK, json={
            'embeds': [{
                'title': 'SC2 Ladder Exception',
                'fields': [
                    {
                        'name': 'Subject',
                        'value': subject,
                        'inline': False
                    },
                    {
                        'name': 'Message',
                        'value': data.get('exception_value', 'No message provided'),
                        'inline': False
                    },

                ],
                'footer': {
                    'text': ''
                }
            }]
        })
