from .common import *

SECRET_KEY = '0c(i&aa$a5gt8#2mc&#7mw7mw_59vy3@$or#fphd6tbf2esjjo'
DEBUG = True
ALLOWED_HOSTS = ['*']

DB_BATCH_SIZE = 100
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTH_PASSWORD_VALIDATORS = []
