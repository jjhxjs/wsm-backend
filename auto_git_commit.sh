git pull
git add .
if [ $1 ]; then
  git commit -m $1
else
  git commit -m "auto_commit"
fi
git push
