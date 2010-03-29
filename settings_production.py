from openelections.settings import *
DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'oe_production'
DATABASE_USER = 'oe_production'
DATABASE_PASSWORD = 'so36v5ri6yaoncgzi3m8vdsg23yria5tkpbghaqs'
DATABASE_HOST = ''
DATABASE_PORT = ''

TEMPLATE_DIRS = ('/var/www/openelections/templates/',)

MEDIA_ROOT = '/var/www/openelections/public/'

WEBAUTH_URL = "http://stanford.edu/~sqs/cgi-bin/authenticate_elections2.php?from="
from openelections.settings_secret import WEBAUTH_SECRET

MEDIA_URL = 'http://voterguide.stanford.edu/'
