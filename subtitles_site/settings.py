import os

# Build paths inside the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'django-insecure-replace-this'
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'subtitles',
]

MIDDLEWARE = []

ROOT_URLCONF = 'subtitles_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'subtitles', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {},
    },
]

WSGI_APPLICATION = 'subtitles_site.wsgi.application'

STATIC_URL = '/static/'

# مسارات الملفات الثابتة أثناء التطوير
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]