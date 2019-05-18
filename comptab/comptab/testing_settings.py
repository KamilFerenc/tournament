import tempfile
from .settings import *
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

MEDIA_ROOT = os.path.join(tempfile.gettempdir(), 'tournament_test/')
