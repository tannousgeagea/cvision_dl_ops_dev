#! /bin/bash
set -e

/bin/bash -c "python3 /home/$user/src/cvision_ops/manage.py makemigrations"
/bin/bash -c "python3 /home/$user/src/cvision_ops/manage.py migrate"
/bin/bash -c "python3 /home/$user/src/cvision_ops/manage.py create_superuser"

sudo -E supervisord -n -c /etc/supervisord.conf