import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BLIZZARD_CLIENT_ID = os.environ["BLIZZARD_CLIENT_ID"]
BLIZZARD_CLIENT_SECRET = os.environ["BLIZZARD_CLIENT_SECRET"]
DEFAULT_QUERY_LIMIT = 25
MAX_QUERY_LIMIT = 200

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
CONSTANCE_CONFIG = {
    "STEP_SIZE": (
        20,
        "Number of ladders to process into the database at once. Seperate from DB_BATCH_SIZE.",
        int,
    ),
    "AGE_LIMIT": (
        30,
        "Hide players who haven't been updated in this number of days.",
        int,
    ),
    "SC2API_BASEURL": (
        "kr.api.blizzard.com",
        "Base url to use for the SC2 API",
        str,
    ),
}

INSTALLED_APPS = [
    "app",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "waffle",
    "constance",
    "constance.backends.database",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "waffle.middleware.WaffleMiddleware",
]

ROOT_URLCONF = "sc2ladder.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [os.path.join(BASE_DIR, "app", "templates")],
        "APP_DIRS": False,
        "OPTIONS": {
            "environment": "sc2ladder.jinja2.environment",
            "extensions": ["waffle.jinja.WaffleExtension",],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "sc2ladder.wsgi.application"
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = "/static/"
