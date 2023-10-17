"""Default configuration

Use env var to override
"""
import os

SERVER_NAME = os.getenv("SERVER_NAME")
SECRET_KEY = os.getenv("SECRET_KEY")
# URL scheme to use outside of request context
PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", 'http')
FHIR_SERVER_URL = os.getenv('FHIR_SERVER_URL')
UPLOAD_BUNDLE_SIZE = int(os.getenv("UPLOAD_BUNDLE_SIZE", "20"))

# Used to access keycloak db for event log extraction
DB_VENDOR = os.getenv("DB_VENDOR", "postgres")
DB_ADDR = os.getenv("DB_ADDR", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_DATABASE = os.getenv("DB_DATABASE", "keycloak")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

LOGSERVER_TOKEN = os.getenv('LOGSERVER_TOKEN')
LOGSERVER_URL = os.getenv('LOGSERVER_URL')

# NB log level hardcoded at INFO for logserver
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG').upper()
