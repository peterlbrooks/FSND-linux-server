sportsCatalog App

APP OVERVIEW

- To start enter from your browser:
http://ec2-18-219-188-90.us-east-2.compute.amazonaws.com
- You will see the home page
- From this page a user can login via facebook or google, or be a public user
- Logged in users can create, add, and delete items. Public users can not udpate
- All instructions are from the app home directory


Catalog Page

- Default view is catalog categories on left, and the 10 last updated items on the left
- Catalog categories are predefined in the DB, no editting allowed
- Click on a category to see the list of items for that category
- Click on the title word "Category" to see the list of the last 10 updated items
- Log in if you want item edit / delete capabilty. Google and Facebook logins are included


Items
- To add an item, click on the category in which you wish to add an item. The list of current items will appear as well as an "New Item" link next to the Item List title (top right)
- To view an item, click on the item name (rigth coloum of the main screen)
- Editting and deleting an item is done from buttons on the view item screen


Json
- There are two JSON outputs
    - List of catalog categories from a link on the lower right of the main catalog screen
    - Item detail from a link on the lower right of a show item screen
    - From a JSON screen, to continue press your browser back button


SSH'ING IN

use 'ssh -p 2200 grader@18.219.188.90' to log in. The grader password is: mygrader.


TECHNOLOGY OVERVIEW

Amazon Lightship is used as the cloud providrer.

The IP address is: http://18.219.188.90 (static IP address). However, the Google OAuth2 setup now does not accept a straight IP address so you can use the reverse lookup: : http://ec2-18-219-188-90.us-east-2.compute.amazonaws.com

Software and versions used are:

- Apache 2.4.18 (Ubuntu)
- Ubuntu 16.04.3 LTS (codename xenial)
- UFW (uncomplicated firewall) 0.35
- virtualenv 15.0.1
- Python 2.7.12
- PostgresSQL 9.5.11



TECHNOLOGY CONFIGURATIONS

Some of the above software requires a configuration file to work. These configuration files are:

- virtualenv config at /etc/apache2/sites-available/sportsCatalog.conf

<VirtualHost *:80>
        ServerName 18.219.188.90
        ServerAdmin plbrooks@gmail.com
        WSGIScriptAlias / /var/www/sportsCatalog.wsgi
        <Directory /var/www/sportsCatalog/>
            Order allow,deny
            Allow from all
            Options -Indexes
        </Directory>
        Alias /static /var/www/sportsCatalog/static
        <Directory /var/www/sportsCatalog/static/>
            Order allow,deny
            Allow from all
            Options -Indexes
        </Directory>
        ErrorLog ${APACHE_LOG_DIR}/error.log
        LogLevel warn
        CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>

- Apache Flask for the app at /var/www/sportsCatalog.wsgi

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

- ssh_config file at /etc/ssh/sshd_config

Text not included here for security reasons.

RESOURCES USED

Thanks to Udacitiy discussion forums and courses, Stack Overflow, and DigitalOcean!

https://discussions.udacity.com/c/nd004-full-stack-broadcast
https://discussions.udacity.com/t/https://discussions.udacity.com/t/
https://discussions.udacity.com/t/google-outh-login-issue/568071/2
https://discussions.udacity.com/t/how-to-move-a-flask-app-from-using-a-sqlite3-db-to-postgresql/7004
https://www.udacity.com/course/configuring-linux-web-servers--ud299
https://www.digitalocean.com/community/questions/how-do-i-remove-apache2-ubuntu-default-page
https://www.digitalocean.com/community/tutorials/how-to-set-up-apache-virtual-hosts-on-ubuntu-14-04-lts
http://flask.pocoo.org/docs/0.12/deploying/mod_wsgi/
https://www.thecodeship.com/deployment/deploy-django-apache-virtualenv-and-mod_wsgi/
https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
various stackoverflow answers








