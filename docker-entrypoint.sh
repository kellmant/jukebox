#!/bin/bash
#set -eo pipefail

rm -rf /var/run/apache2/apache2.pid


/usr/bin/pip install --upgrade youtube-dl

exec /usr/sbin/apache2ctl -D FOREGROUND
