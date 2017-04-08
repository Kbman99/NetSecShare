TIMEZONE = 'Europe/Paris'

# Secret key for generating tokens
SECRET_KEY = 'houdini'

# LDAP server details
LDAP_SERVER =''
LDAP_SERVICE_USERNAME = ''
LDAP_SERVICE_PASSWORD = ''

# Admin credentials
ADMIN_CREDENTIALS = ('admin', 'pa$$word')

# Database choice
SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Configuration of a Gmail account for sending mails
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'NetSecShare'
MAIL_PASSWORD = 'NetSecShare123'
ADMINS = ['kylebowman99@gmail.com']

# Number of times a password is hashed
BCRYPT_LOG_ROUNDS = 12
