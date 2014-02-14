project_root="/home/parking/intelligent_parking"
uwsgi --plugin=python --pythonpath /home/parking/intelligent_parking -s 127.0.0.1:2221 -w wsgi -M -p 20 -t 6000 -d $project_root/uwsgi.log -b 32768 --enable-threads --pidfile=$project_root/uwsgi.pid
