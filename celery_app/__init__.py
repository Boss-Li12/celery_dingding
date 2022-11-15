# celery_app will load these info atomatically
from celery import Celery

# strict name format
app = Celery('dingding') # create an instance
app.config_from_object('celery_app.celeryconfig') # load the config