pid_file=.pyjianying.pid

if [ -f ~/$pid_file ]; then
  ps -p `cat ~/$pid_file` > /dev/null 2>&1

  if [ $? -eq 0 ]; then
    echo "Process is running with PID `cat ~/$pid_file`"

    echo 'kill' `cat ~/$pid_file`
    kill `cat ~/$pid_file`
  else
    echo "Process with PID `cat ~/$pid_file` is not running"
  fi
fi

source .venv/bin/activate

nohup python http_server.py > nohup.out 2>&1 &
pid=$!

echo "Started process with PID $pid"
echo $pid > ~/$pid_file


