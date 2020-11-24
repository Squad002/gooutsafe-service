#!/bin/bash
source venv/bin/activate
export FLASK_APP="gooutsafe"

while true; do
    flask deploy
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Deploy command failed, retrying in 5 secs...
    sleep 5
done

celery -A gooutsafe.celery worker -l DEBUG -E -B &
exec gunicorn -b 0.0.0.0:5000 --access-logfile - --error-logfile - gooutsafe:app 
