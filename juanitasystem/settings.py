"""
Django settings for juanitasystem project.

Generated by 'django-admin startproject' using Django 5.0.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os # para gestionar variables de entorno
import dj_database_url # para gestionar la base de datos de desarrollo, en la nube

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'user',
    'proyect'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para desplegar
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'juanitasystem.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
             BASE_DIR / 'templates',  # Asegúrate de que esta línea esté configurada para agregar header.html y footer.html
        ],
        'APP_DIRS': True, # En la configuración TEMPLATES, agrega 'APP_DIRS': True, si no está activado, para que Django pueda buscar plantillas dentro de las aplicaciones.
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'proyect.context_processors.settings_variables', # Aquí se registra el context processor en la app proyect, para usar por el  ejemplo la API_KEY
            ],
        },
    },
]

WSGI_APPLICATION = 'juanitasystem.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Asegúrate de que esté configurado para apuntar a la carpeta correcta
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Configuración de sesiones
SESSION_COOKIE_AGE = 3600 * 12  # Duración de la sesión en segundos (12 horas)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Expirar sesión cuando se cierra el navegador

LOGIN_REDIRECT_URL = '/user/login/'    # Redirige al inicio después de un login exitoso
LOGIN_URL = '/user/login/'   # Redirigir al login si no está autenticado


########## DESPLIEGUE ##########

SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = os.environ.get("DEBUG", "False").lower() == "true" # SECURITY WARNING: don't run with debug turned on in production!
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(" ")

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# This production code might break development mode, so we check whether we're in DEBUG mode
if not DEBUG:
    # Tell Django to copy static assets into a path called `staticfiles` (this is specific to Render)
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    # Enable the WhiteNoise storage backend, which compresses static files to reduce disk use
    # and renames the files with unique names for each version to support long-term caching
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

database_url = os.environ.get("DATABASES_URL")
DATABASES['default'] = dj_database_url.parse(database_url) 

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')



##########################################################
##########################################################
##########################################################
##########################################################
#################### DESARROLLO ##########################
##########################################################
##########################################################
##########################################################
##########################################################
##########################################################

# #PASO N1: Agregar la siguiente configuracion para adaptar el ambiente a desarrollo

# # SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-uoa7$hdjz+ok151$j8h=s!6r=#f!n2u^4qno+j3s0nx=+mhg$w'

# DATABASES = {
#     'default': {
#             'ENGINE': 'django.db.backends.postgresql',
#             'NAME': 'juanitadb',
#             'USER': 'administrator_jsystem',
#             'PASSWORD': 'juanita.pass.2024',
#             'HOST': 'localhost',
#             'PORT': 5432,
#         },

# }

# # database_url = 'postgresql://juanitadb_user:dRHm1eDJC6pMywIrOO931avP9CpRuGdk@dpg-cshuma9u0jms73f6rgog-a.oregon-postgres.render.com/juanitadb'
# # DATABASES['default'] = dj_database_url.parse(database_url) 

# DEBUG = True

# ALLOWED_HOSTS = []

# GOOGLE_API_KEY = "AIzaSyAjTuqaptDsxiU79IQ5nil8JyVw5AxQenU"