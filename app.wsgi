import sys
import logging
sys.path.insert(0, '/var/www/VocPrez')
logging.basicConfig(stream=sys.stderr)

from app import app as application