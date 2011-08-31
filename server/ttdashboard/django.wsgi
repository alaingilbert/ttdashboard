import os                                                                                                                                                                                                                                   
import sys 
import site
 
# FIXME: this should not be there at all!
sys.path.append('/var/www/ttdashboard/server/ttdashboard')
 
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
 
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
