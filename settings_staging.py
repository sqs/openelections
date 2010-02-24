from openelections.settings import *
DEBUG = TEMPLATE_DEBUG = False
DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'oe_staging'
DATABASE_USER = 'oe_staging'
DATABASE_PASSWORD = 'sdfjef77fdsh76g3a7hauak46drbgkinajghe'
DATABASE_HOST = ''
DATABASE_PORT = ''

MEDIA_ROOT = '/var/www/staging/openelections/media/'

TEMPLATE_DIRS = ('/var/www/staging/openelections/templates/',)
