netstat -nlp|grep 8080|grep -v grep|awk '{print$7}' | awk  -F '/' '{print "kill -9 "$1}'|sh
nohup python3 server.py &
