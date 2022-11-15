from datetime import timedelta
from celery.schedules import crontab

BROKER_URL = 'redis://127.0.0.1:6379'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'

CELERY_TIMEZONE = 'Asia/Shanghai'

# task modules to import
# god damn 'S'!!!!!
CELERY_IMPORTS = (
    'celery_app.crontabTasks.task_weiboTop10',
    'celery_app.crontabTasks.task_jinseNews',
    'celery_app.crontabTasks.task_liepin',
    'celery_app.crontabTasks.task_shixiseng',
)

# schedules(beat)
CELERYBEAT_SCHEDULE = {
    'weiboTop10-every-1-hour': {
        'task': 'task_weiboTop10.get_news',
        'schedule': timedelta(seconds = 3600),
    },
    
    'jinseNew-every-1-hour': {
        'task': 'task_jinseNews.get_news',
        'schedule': timedelta(seconds = 3600),
    },

    'liepin-every-1-day': {
        'task': 'task_liepin.get_started',
        'schedule': timedelta(seconds = 3600 * 24),
    },

    'shixiseng-every-1-day': {
        'task': 'task_shixiseng.get_started',
        'schedule': timedelta(seconds=3600 * 24),
    },
    
}
