nohup $1 > $2 2>&1 &
echo $! > save_pid.txt
