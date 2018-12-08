#! /bin/bash

### BEGIN INIT INFO
# Provides:          photo-float
# Required-Start:    $remote_fs $syslog $network
# Required-Stop:     $remote_fs $syslog $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Manage the local photo server
### END INIT INFO


case "$1" in 
    start)
        echo "Starting photofloat"
	cd [[ CHECKOUT DIR ]]
	source venv/bin/activate
	cd scanner
        gunicorn \
		--bind=unix:/var/run/photofloat.socket \
		--pid=/var/run/photofloat.pid \
		--capture-output \
		--workers 1 \   # this is necessary
		--timeout 120 \
		--log-file=/var/log/gunicron-photofloat.log \
		floatapp:app &
	exit 0
        ;;
    stop)
        kill `cat /var/run/photofloat.pid`
	exit 0
        ;;
    *)
        echo "Usage: /etc/init.d/gunicorn-photo-float start|stop"
        exit 1
        ;;
esac

exit 0
