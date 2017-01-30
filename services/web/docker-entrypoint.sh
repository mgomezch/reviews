#!/bin/bash
set -e


touch reviews/migrations/__init__.py

if [[ "${1}" == 'production' ]]
then
  export DEBUG="${DEBUG:-False}"
else
  export DEBUG="${DEBUG:-True}"
fi


case "${1}" in

  ('bash')
    exec "$@"
  ;;

  ('sync')
    ./manage.py makemigrations
    ./manage.py migrate
  ;;

  ('production')
    ./manage.py collectstatic --noinput || true
  ;& ('development')
    exec gunicorn --config='config/gunicorn.py' reviews.wsgi
  ;;

  (*)
    exec ./manage.py "$@"
  ;;
esac
