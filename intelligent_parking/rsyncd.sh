#! /bin/sh
#远程用户名
RUSER=parking
#远程服务器地址
RHOST=60.160.152.127
#djoin.net
#远程目录
RPATH=/home/parking
#本地目录
LPATH=/home/wdong/intelligent_parking

#rsync -e "ssh" -avz --delete  $LPATH $RUSER@$RHOST:$RPATH
rsync --exclude '*.out' --exclude '.svn' --exclude '*.pyc' --exclude '*.log' --exclude '*.swp' --exclude 'apk' --exclude '*.apk' --exclude 'uwsgi.pid' --exclude 'mobile_app' --exclude 'pg.py' --exclude 'bin' --exclude 'session' -e "ssh" -avz $LPATH $RUSER@$RHOST:$RPATH

