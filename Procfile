web: gunicorn --pythonpath="$PWD" XmasShuffle.wsgi:application

worker: python XmasShuffle/manage.py rqworker heroku default
