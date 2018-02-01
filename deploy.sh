BRANCH="$(git rev-parse --abbrev-ref HEAD)"

if [ $BRANCH == "master" ]; then
    echo "Deployment starting..."
    git push dokku@opencult.com:opencult master
else
    echo "Not on master, deployment canceled."
fi
