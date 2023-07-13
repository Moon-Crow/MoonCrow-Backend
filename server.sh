#!/usr/bin/env bash

SERVER_HOME=/ops/server/openGauss-visualtool
cd $SERVER_HOME
API_NAME=visualtool-main
JAR_NAME=$SERVER_HOME/$API_NAME\.jar
LOG=$SERVER_HOME/logs/$API_NAME\.out
PID=$SERVER_HOME/$API_NAME\.pid

usage() {
    echo "Usage: sh server.sh [start|stop|restart|status]"
    exit 1
}

is_exist(){
  pid=`ps -ef|grep $JAR_NAME|grep -v grep|awk '{print $2}' `
  if [ -z "${pid}" ]; then
   return 1
  else
    return 0
  fi
}

start(){
  is_exist
  if [ $? -eq "0" ]; then
    echo ">>> ${JAR_NAME} is already running PID=${pid} <<<"
  else
    echo '' > $LOG
    nohup java -Xms2048m -Xmx4096m -jar $JAR_NAME --spring.profiles.active=cus >$LOG 2>&1 &
    echo $! > $PID
    echo ">>> start $JAR_NAME successed PID=$! <<<"
   fi
  }

stop(){
  pidf=$(cat $PID)
  echo ">>> ${API_NAME} PID = $pidf begin kill $pidf <<<"
  kill $pidf
  rm -rf $PID
  sleep 2
  is_exist
  if [ $? -eq "0" ]; then
    echo ">>> ${API_NAME} 2 PID = $pid begin kill -9 $pid  <<<"
    kill -9  $pid
    sleep 2
    echo ">>> $JAR_NAME process stopped <<<"
  else
    echo ">>> ${JAR_NAME} is not running <<<"
  fi
}

status(){
  is_exist
  if [ $? -eq "0" ]; then
    echo ">>> ${JAR_NAME} is running PID is ${pid} <<<"
  else
    echo ">>> ${JAR_NAME} is not running <<<"
  fi
}

restart(){
  stop
  start
}

case "$1" in
  "start")
    start
    ;;
  "stop")
    stop
    ;;
  "status")
    status
    ;;
  "restart")
    restart
    ;;
  *)
    usage
    ;;
esac
exit 0
}