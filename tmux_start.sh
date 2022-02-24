#ps aux | grep 5000 | awk '{print $2}' | xargs kill -9
#tmux send-keys -t flask-server '^C'
ps aux | grep 5000 | awk '{print $2}' | xargs kill -9
tmux send-keys -t flask-server '' C-m
tmux send-keys -t flask-server 'cd ~/work/wsmserver' C-m
tmux send-keys -t flask-server 'bash start_cloud.sh' C-m
