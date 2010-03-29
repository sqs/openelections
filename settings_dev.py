from openelections.settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'data/oe.sqlite'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

#MEDIA_ROOT = '/home/sqs/proj/ec/openelections/public'
MEDIA_ROOT = '/afs/ir/users/s/q/sqs/proj/openelections/public'

WEBAUTH_SECRET = '2aca147905asioerhdf67fds7y7ydsyhdsg6afbfbyfbbo4957'
WEBAUTH_URL = "http://stanford.edu/~sqs/cgi-bin/authenticate_elections2_dev.php?from="

MEDIA_URL = 'http://corn24.stanford.edu:32145/'
