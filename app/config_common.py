TIMEZONE = 'US/Eastern'
TIME_FMT = '%Y-%m-%d %H:%M:%S %Z%z'

# Secret key for generating tokens
SECRET_KEY = 'houdini'

# LDAP server details
# LDAP_SERVER =''
# LDAP_SERVICE_USERNAME = ''
# LDAP_SERVICE_PASSWORD = ''

# Admin credentials
ADMIN_CREDENTIALS = ('admin', 'pa$$word')

# Database choice
SQLALCHEMY_DATABASE_URI = 'sqlite:///app_new.db'
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Configuration of a Gmail account for sending mails
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'NetSecShare'
MAIL_PASSWORD = 'NetSecShare123'
ADMINS = ['kylebowman99@gmail.com']

# Number of times a password is hashe
BCRYPT_LOG_ROUNDS = 12

# Permission table
Permission = {1: 'Read'}

# Flask-Uploads config options
UPLOADS_DEFAULT_DEST = 'app/static'
UPLOADS_DIR = 'static/uploads'
UPLOAD_PATH = 'app/static/uploads'
