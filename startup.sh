pid_file=.pyjianying.pid

if [ -f ~/$pid_file ]; then
  kill `cat ~/$pid_file`
  echo 'kill' `cat ~/$pid_file`
fi

NODE_ENV=production nohup python http_server.py > nohup.out 2>&1 &
echo $! > ~/$pid_file