# 拉取远程仓库
git pull origin master
# ster
export FLASK_ENV=staging
export FLASK_DEBUG=1

#source ../venv/bin/activate
#pip install -r requirements.txt
#flask run --host=0.0.0.0 --port=5000

# 改为由uwsgi启动

uwsgi --http-socket 0.0.0.0:5000 --module app:app --enable-threads --thunder-lock --processes 32 --buffer-size=65535
#uwsgi uwsgi.ini