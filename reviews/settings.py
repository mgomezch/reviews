from datetime import timedelta
from os import environ
from os.path import abspath, dirname, join
from sys import stdout


# Run with debugging disabled by default.  DEBUG must be a defined environment
# variable with the exact string value True in order to enable debugging.
DEBUG = environ.get('DEBUG', None) == 'True'


# Run with a default insecure secret key if DEBUG is True and no key is defined
# in the SECRET_KEY environment variable.
SECRET_KEY = (
    environ.get('SECRET_KEY', None) or
    (DEBUG and 'xyzzy')
)
if not SECRET_KEY:
    raise Exception('SECRET_KEY is not defined and DEBUG is False')


# Allow all hosts by default unless specified in the ALLOWED_HOST environment
# variable.
ALLOWED_HOSTS = [
    host
    for host in [environ.get('ALLOWED_HOST')]
    if host
] or ['*']


# Disable the Django Debug Toolbar's IP whitelist as internal IPs are not easy
# to predict for a Docker deployment.  We want debugging always if the DEBUG
# flag is True, and never if it isn't.  Production is not deployed with DEBUG
# set to True anyway, and if it were, we would have bigger problems than just
# the debug toolbar.
class Universe:
    def __contains__(self, key):
        return True
INTERNAL_IPS = Universe()


# Basic system paths:
BASE_DIR = dirname(dirname(abspath(__file__)))
PROJECT_ROOT = dirname(abspath(__file__))


# Basic application definition:
ROOT_URLCONF = 'reviews.urls'
WSGI_APPLICATION = 'reviews.wsgi.application'


# Despite this project being mostly a REST API, the Django Debug Toolbar,
# the API browser provided by the Django Rest Framework, and the Swagger
# documentation all require serving static files.  WhiteNoise serves them
# efficiently from the application server.  See http://whitenoise.evans.io/
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'
USE_ETAGS = True  # This improves caching of static resources


# Use a custom User model in case of future needs to change default user fields;
# see https://code.djangoproject.com/ticket/25313
AUTH_USER_MODEL = 'reviews.User'


# Most of Django does nonsensical things with timestamps unless these are set:
USE_TZ = True
TIME_ZONE = 'UTC'


# Security middleware settings:

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365  # One year

SECURE_PROXY_SSL_HEADER = (
    None
    if DEBUG
    else ('HTTP_X_FORWARDED_PROTO', 'https')
)


DATABASES = {

    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': environ.get('DATABASE_NAME', 'reviews'),
        'USER': environ.get('DATABASE_USER', 'reviews'),
        'PASSWORD': environ.get('DATABASE_PASSWORD', 'reviews'),
        'HOST': environ.get('DATABASE_HOST', 'postgres'),
        'PORT': environ.get('DATABASE_PORT', 5432),
    }

}


INSTALLED_APPS = [

    # Required by the Django admin app:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.admin',

    # Required by the Django Debug Toolbar:
    'django.contrib.staticfiles',
    'debug_toolbar',

    # Required by the CORS headers middleware:
    'corsheaders',

    # Required by the API implementation:
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',

    # This project's local apps:
    'reviews',
    'api',

]


# Send everything to standard output to be picked up by the Docker log engine:
LOGGING = {

    'version': 1,
    'disable_existing_loggers': False,

    'handlers': {

        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': stdout,
        },

    },

}


MIDDLEWARE = [

    # Enable several HTTP-related security features:
    'django.middleware.security.SecurityMiddleware',

    # Handle CORS requests and include appropriate response headers  to enable
    # scripts running inside browsers to perform requests to the API despite
    # being served from different origins:
    'corsheaders.middleware.CorsMiddleware',

    # Serve static files with WhiteNoise:
    'whitenoise.middleware.WhiteNoiseMiddleware',

    # Despite this project being mostly a REST API, the Django Debug Toolbar is
    # convenient for development:
    'debug_toolbar.middleware.DebugToolbarMiddleware',

    # Provide server-side sessions identified by HTTP cookies:
    'django.contrib.sessions.middleware.SessionMiddleware',

    # Generate ETags for responses:
    'django.middleware.common.CommonMiddleware',

    # Provide authenticated user information in requests:
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    # Provide page messages used by the Django admin app:
    'django.contrib.messages.middleware.MessageMiddleware',
]


# The Django Debug Toolbar and the admin site use Django templates:
TEMPLATES = [

    {
        'APP_DIRS': True,
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.csrf',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
            ],
        },
    },

]


REST_FRAMEWORK = {

    # Specify API version with a prefix path component in resource URIs:
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'ALLOWED_VERSIONS': (
        'v1',
    ),

    'DEFAULT_AUTHENTICATION_CLASSES': (

        # Support authentication by passing full user credentials on every
        # request through the Basic HTTP authentication scheme.  This is a very
        # simple and easy way to authenticate requests to the API, but it's not
        # ideal since the client has to send full, non-expiring credentials in
        # every request to the API.  See https://tools.ietf.org/html/rfc7617
        'rest_framework.authentication.BasicAuthentication',

        # Support authentication through session cookies.  This is convenient
        # for browsers, but browser-based clients should guard carefully against
        # cross-site request forgery attacks.
        'rest_framework.authentication.SessionAuthentication',

        # Support authentication through static, persistent tokens in a similar
        # way to manually managed session cookies.  This scheme allows for more
        # precise control of how credentials are stored in a client application
        # and when to provide them in a request, which means more manual work is
        # required to write a client, but certain cross-site request forgery
        # pitfalls may be more easily avoided.
        'rest_framework.authentication.TokenAuthentication',

        # Support authentication through JSON Web Tokens in a similar way to
        # manually managed session cookies.  This scheme is very similar to the
        # regular token authentication method, but credentials are verified
        # cryptographically instead of checked against a persistent static token
        # stored in the database, and issued tokens expire promptly unless
        # renewed periodically by the client.  See https://jwt.io/ and
        # http://getblimp.github.io/django-rest-framework-jwt/
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',

    ),

    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),

    # This requires authentication for all API resources by default:
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),

    # Pagination options:
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.CursorPagination',
    'PAGE_SIZE': 10,

    # The self-hyperlink in resource representations is called `url` by default,
    # which clashes with the name of at least one API resource called `url` as
    # well.  This changes the name of the self-hyperlink field to `self`.
    'URL_FIELD_NAME': 'self',

}


# Options for authentication via a session-like scheme using JSON Web Tokens;
# see http://getblimp.github.io/django-rest-framework-jwt/
JWT_AUTH = {
    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DELTA': timedelta(hours=1),
}
