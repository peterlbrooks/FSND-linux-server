activate_this = '/var/www/sportsCatalog/ENV/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/sportsCatalog/")
#sys.path.insert(0,"/var/www/")

# from application.py will import app as an application
from application import app as application
application.secret_key = '12345'

