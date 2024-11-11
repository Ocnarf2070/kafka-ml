"""
Django settings for autoweb project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'zbtes53q%twx0#&@$c-b2^299qv1fi4v3ldv*&u9po%bbd8asu' if os.environ.get('SECRET_KEY') is None else os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.environ.get('DEBUG') is None or os.environ.get('DEBUG')== '1' else False

ALLOWED_HOSTS = ['backend', 'frontend', '127.0.0.1', 'localhost', '[::1]'] if os.environ.get('ALLOWED_HOSTS') is None else os.environ.get('ALLOWED_HOSTS').split(',')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'automl.apps.AutomlConfig',
    'rest_framework',
    'corsheaders',
    'channels'
]

ASGI_APPLICATION = 'autoweb.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'autoweb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'autoweb.wsgi.application'

REST_FRAMEWORK = {
    'COERCE_DECIMAL_TO_STRING': False,
}

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

FRONTEND_URL = 'http://localhost' if os.environ.get('FRONTEND_URL') is None else os.environ.get('FRONTEND_URL')
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = [
    "http://localhost:4200",
    FRONTEND_URL
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'models')
MEDIA_URL = '/data/'

MODELS_DIR = 'pre/'
TRAINED_MODELS_DIR = 'trained/'

BOOTSTRAP_SERVERS = os.environ.get('BOOTSTRAP_SERVERS')
BOOTSTRAP_SERVERS_RABBITMQ = os.environ.get('BOOTSTRAP_SERVERS_RABBITMQ')
CONTROL_TOPIC = os.environ.get('CONTROL_TOPIC')
TENSORFLOW_TRAINING_MODEL_IMAGE = os.environ.get('TENSORFLOW_TRAINING_MODEL_IMAGE')
TENSORFLOW_INFERENCE_MODEL_IMAGE = os.environ.get('TENSORFLOW_INFERENCE_MODEL_IMAGE')

PYTORCH_TRAINING_MODEL_IMAGE = os.environ.get('PYTORCH_TRAINING_MODEL_IMAGE')
PYTORCH_INFERENCE_MODEL_IMAGE = os.environ.get('PYTORCH_INFERENCE_MODEL_IMAGE')

MODEL_LOGGER_TOPIC = "FEDERATED_MODEL_CONTROL_TOPIC" if os.environ.get('MODEL_LOGGER_TOPIC') is None else os.environ.get('MODEL_LOGGER_TOPIC')

TENSORFLOW_EXECUTOR_URL = "http://localhost:8001/" if os.environ.get('TFEXECUTOR_URL') is None else os.environ.get('TFEXECUTOR_URL')
PYTORCH_EXECUTOR_URL = "http://localhost:8002/" if os.environ.get('PTHEXECUTOR_URL') is None else os.environ.get('PTHEXECUTOR_URL')

KUBE_NAMESPACE = "kafkaml" if os.environ.get('KUBE_NAMESPACE') is None else os.environ.get('KUBE_NAMESPACE')

DATA_UPLOAD_MAX_MEMORY_SIZE = None