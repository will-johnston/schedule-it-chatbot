# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'fsch+6!=q+@ol&%0x!nwdl@48^ixbd4clx5f1i!5n^66y+pmn*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['willjohnston.pythonanywhere.com', '127.0.0.1']

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'django-cors-headers',
    'chatterbot.ext.django_chatterbot',
    'chatsite',
)

# ChatterBot settings

#CORS_ORIGIN_ALLOW_ALL = True
CHATTERBOT = {
    'name': 'Clarence',
    'trainer': 'chatterbot.trainers.ChatterBotCorpusTrainer',
    'training_data': [
        'chatterbot.corpus.english.botprofile', 'chatterbot.corpus.english.conversations',
        'chatterbot.corpus.english.emotion', 'chatterbot.corpus.english.food', 'chatterbot.corpus.english.gossip',
        'chatterbot.corpus.english.humor', 'chatterbot.corpus.english.politics', 'chatterbot.corpus.english.psychology',
        'my_corpus'
    ],
    #'training_data': [
    #    {"What can you tell me?", """My main function is to help schedule events. However, I can also give you information on any events for the group.
    #   This could range from event names and descriptions to timing (whether an event time is set or flexible to your preferences)."""
    #    },
    #    {"Could you explain event time to me?", """Event timing works in two ways.
    #   Either an exact time is set or the best time is found from the group members preferences.
    #   When creating an event, you will have the option to choose.
    #   \nIf you set the timing to look for the best time, I will ask all group members who wish to attend their top two preferences.
    #   An expiration date will determine when to process all the preferences and calculate the best time."""
    #    }
    #],

    'logic_adapters': ['schedule_adapter.my_schedule_adapter'],

    #[
     #   {   
      #      'import_path': 'schedule_adapter.my_schedule_adapter' 
       # },

    #    {
    #        'import_path':'chatterbot.logic.BestMatch',
    #        'statement_comparison_function': 'chatterbot.comparisons.levenshtein_distance'
     #   },
     #   {
     #       'import_path': 'chatterbot.logic.LowConfidenceAdapter',
     #       'threshold': 0.65,
     #       'default_response': 'I am sorry, but I do not understand.'
     #   }
    #],

    'django_app_name': 'django_chatterbot'

}
MIDDLEWARE_CLASSES = (
    #'corsheaders.middleware.CorsMiddleware',    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'chatsite.urls'

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

WSGI_APPLICATION = 'chatsite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
APPEND_SLASH = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = (
    os.path.join(
        os.path.dirname(__file__),
        'static',
    ),
)
